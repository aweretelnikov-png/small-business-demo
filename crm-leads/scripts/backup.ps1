$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $PSScriptRoot
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = Join-Path $ProjectDir "backups\$Timestamp"

New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

function Invoke-Docker {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)

    & docker @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Docker command failed: docker $($Arguments -join ' ')"
    }
}

function Export-PostgresDump {
    param(
        [string]$Container,
        [string]$User,
        [string]$Database,
        [string]$OutputName
    )

    $ContainerFile = "/tmp/$OutputName"
    $HostFile = Join-Path $BackupDir $OutputName

    Invoke-Docker exec $Container pg_dump -U $User -d $Database -Fc -f $ContainerFile
    Invoke-Docker exec $Container pg_restore -l $ContainerFile | Out-Null
    Invoke-Docker cp "${Container}:$ContainerFile" $HostFile
    Invoke-Docker exec $Container rm -f $ContainerFile
}

Write-Host "Backup directory: $BackupDir"
Write-Host "1/4 Backing up crm_demo..."
Export-PostgresDump `
    -Container "crm-postgres" `
    -User "crm_user" `
    -Database "crm_demo" `
    -OutputName "crm_demo.dump"

$TwentyStopped = $false
try {
    Write-Host "2/4 Stopping Twenty server and worker..."
    Invoke-Docker stop twenty-worker-1 twenty-server-1
    $TwentyStopped = $true

    Write-Host "3/4 Backing up Twenty database and local storage..."
    Export-PostgresDump `
        -Container "twenty-db-1" `
        -User "postgres" `
        -Database "default" `
        -OutputName "twenty.dump"

    $TwentyStorageDir = Join-Path $BackupDir "twenty-local-storage"
    New-Item -ItemType Directory -Force -Path $TwentyStorageDir | Out-Null
    Invoke-Docker cp `
        "twenty-server-1:/app/packages/twenty-server/.local-storage/." `
        $TwentyStorageDir
}
finally {
    if ($TwentyStopped) {
        Write-Host "Starting Twenty server and worker..."
        Invoke-Docker start twenty-server-1 twenty-worker-1
    }
}

$MetabaseStopped = $false
try {
    Write-Host "4/4 Backing up Metabase application data..."
    Invoke-Docker stop sales-metabase
    $MetabaseStopped = $true

    $MetabaseDir = Join-Path $BackupDir "metabase-data"
    New-Item -ItemType Directory -Force -Path $MetabaseDir | Out-Null
    Invoke-Docker cp "sales-metabase:/metabase-data/." $MetabaseDir
}
finally {
    if ($MetabaseStopped) {
        Write-Host "Starting Metabase..."
        Invoke-Docker start sales-metabase
    }
}

$Manifest = @(
    "created_at=$((Get-Date).ToString('o'))"
    "crm_database=crm_demo"
    "twenty_database=default"
    "contains_personal_data=true"
    "env_files_included=false"
)
$Manifest | Set-Content -Encoding UTF8 (Join-Path $BackupDir "manifest.txt")

$ChecksumLines = Get-ChildItem -Path $BackupDir -Recurse -File |
    Sort-Object FullName |
    ForEach-Object {
        $RelativePath = $_.FullName.Substring($BackupDir.Length + 1).Replace("\", "/")
        $Hash = (Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLower()
        "$Hash *$RelativePath"
    }
$ChecksumLines | Set-Content -Encoding ASCII (Join-Path $BackupDir "checksums.sha256")

Write-Host "Backup completed successfully: $BackupDir"
Write-Host "Remember: store the .env files separately in a secure location."
