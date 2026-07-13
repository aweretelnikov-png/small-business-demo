param(
    [string]$BackupDir
)

$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $PSScriptRoot
$BackupsRoot = Join-Path $ProjectDir "backups"
$TestDatabase = "twenty_restore_test"
$ContainerDump = "/tmp/twenty_restore_test.dump"

if (-not $BackupDir) {
    $LatestBackup = Get-ChildItem -Path $BackupsRoot -Directory |
        Sort-Object Name -Descending |
        Select-Object -First 1

    if (-not $LatestBackup) {
        throw "No backup directories found in $BackupsRoot"
    }

    $BackupDir = $LatestBackup.FullName
}

$DumpFile = Join-Path $BackupDir "twenty.dump"
if (-not (Test-Path $DumpFile)) {
    throw "Dump not found: $DumpFile"
}

function Invoke-Docker {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)

    & docker @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Docker command failed: docker $($Arguments -join ' ')"
    }
}

Write-Host "Testing Twenty restore from: $DumpFile"

try {
    Invoke-Docker cp $DumpFile "twenty-db-1:$ContainerDump"
    Invoke-Docker exec twenty-db-1 dropdb `
        -U postgres `
        --if-exists `
        --force `
        $TestDatabase
    Invoke-Docker exec twenty-db-1 createdb `
        -U postgres `
        $TestDatabase
    Invoke-Docker exec twenty-db-1 pg_restore `
        -U postgres `
        "--dbname=$TestDatabase" `
        --no-owner `
        --no-privileges `
        $ContainerDump

    $TableCount = & docker exec twenty-db-1 psql `
        -U postgres `
        -d $TestDatabase `
        -tA `
        -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema');"
    if ($LASTEXITCODE -ne 0) {
        throw "Could not inspect restored Twenty database"
    }

    $WorkspaceCount = & docker exec twenty-db-1 psql `
        -U postgres `
        -d $TestDatabase `
        -tA `
        -c 'SELECT COUNT(*) FROM core."workspace";'
    if ($LASTEXITCODE -ne 0) {
        throw "Could not count restored Twenty workspaces"
    }

    Write-Host "Restored tables: $($TableCount.Trim())"
    Write-Host "Restored workspaces: $($WorkspaceCount.Trim())"
    Write-Host "Twenty restore test passed."
}
finally {
    & docker exec twenty-db-1 dropdb `
        -U postgres `
        --if-exists `
        --force `
        $TestDatabase | Out-Null
    & docker exec twenty-db-1 rm -f $ContainerDump | Out-Null
}
