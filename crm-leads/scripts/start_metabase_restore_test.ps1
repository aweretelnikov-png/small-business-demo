param(
    [string]$BackupDir
)

$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $PSScriptRoot
$BackupsRoot = Join-Path $ProjectDir "backups"
$VolumeName = "crm_metabase_restore_test"
$CopyContainer = "metabase-restore-copy"
$TestContainer = "metabase-restore-test"

if (-not $BackupDir) {
    $LatestBackup = Get-ChildItem -Path $BackupsRoot -Directory |
        Sort-Object Name -Descending |
        Select-Object -First 1

    if (-not $LatestBackup) {
        throw "No backup directories found in $BackupsRoot"
    }

    $BackupDir = $LatestBackup.FullName
}

$MetabaseBackupDir = Join-Path $BackupDir "metabase-data"
if (-not (Test-Path $MetabaseBackupDir)) {
    throw "Metabase backup not found: $MetabaseBackupDir"
}

& cmd.exe /c "docker rm -f $TestContainer >nul 2>&1"
& cmd.exe /c "docker rm -f $CopyContainer >nul 2>&1"
& cmd.exe /c "docker volume rm $VolumeName >nul 2>&1"

& docker volume create $VolumeName | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Could not create temporary Docker volume"
}

& docker create `
    --name $CopyContainer `
    -v "${VolumeName}:/metabase-data" `
    --entrypoint /bin/sh `
    metabase/metabase:latest | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Could not create copy container"
}

try {
    & docker cp "$MetabaseBackupDir\." "${CopyContainer}:/metabase-data"
    if ($LASTEXITCODE -ne 0) {
        throw "Could not copy Metabase backup into temporary volume"
    }
}
finally {
    & docker rm $CopyContainer 2>$null | Out-Null
}

& docker run -d `
    --name $TestContainer `
    --network small-business-demo-network `
    -p "127.0.0.1:3005:3000" `
    -e MB_DB_TYPE=h2 `
    -e MB_DB_FILE=/metabase-data/metabase.db `
    -v "${VolumeName}:/metabase-data" `
    metabase/metabase:latest | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Could not start temporary Metabase"
}

Write-Host "Waiting for temporary Metabase..."
$Healthy = $false

for ($Attempt = 1; $Attempt -le 36; $Attempt++) {
    Start-Sleep -Seconds 5
    & curl.exe `
        --noproxy "*" `
        --silent `
        --fail `
        --max-time 3 `
        http://127.0.0.1:3005/api/health 2>$null | Out-Null

    if ($LASTEXITCODE -eq 0) {
        $Healthy = $true
        break
    }
}

if (-not $Healthy) {
    & docker logs --tail 100 $TestContainer
    throw "Temporary Metabase did not become healthy"
}

Write-Host "Metabase restore test is healthy."
Write-Host "Open: http://localhost:3005"
Write-Host "After checking dashboards, run scripts\stop_metabase_restore_test.ps1"
