param(
    [string]$BackupDir
)

$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $PSScriptRoot
$BackupsRoot = Join-Path $ProjectDir "backups"
$TestDatabase = "crm_restore_test"
$ContainerDump = "/tmp/crm_restore_test.dump"

if (-not $BackupDir) {
    $LatestBackup = Get-ChildItem -Path $BackupsRoot -Directory |
        Sort-Object Name -Descending |
        Select-Object -First 1

    if (-not $LatestBackup) {
        throw "No backup directories found in $BackupsRoot"
    }

    $BackupDir = $LatestBackup.FullName
}

$DumpFile = Join-Path $BackupDir "crm_demo.dump"
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

Write-Host "Testing restore from: $DumpFile"

try {
    Invoke-Docker cp $DumpFile "crm-postgres:$ContainerDump"
    Invoke-Docker exec crm-postgres dropdb `
        -U crm_user `
        --if-exists `
        --force `
        $TestDatabase
    Invoke-Docker exec crm-postgres createdb `
        -U crm_user `
        $TestDatabase
    Invoke-Docker exec crm-postgres pg_restore `
        -U crm_user `
        "--dbname=$TestDatabase" `
        --no-owner `
        --no-privileges `
        $ContainerDump

    $LeadCount = & docker exec crm-postgres psql `
        -U crm_user `
        -d $TestDatabase `
        -tA `
        -c "SELECT COUNT(*) FROM leads;"
    if ($LASTEXITCODE -ne 0) {
        throw "Could not count restored leads"
    }

    $HistoryCount = & docker exec crm-postgres psql `
        -U crm_user `
        -d $TestDatabase `
        -tA `
        -c "SELECT COUNT(*) FROM lead_status_history;"
    if ($LASTEXITCODE -ne 0) {
        throw "Could not count restored status history"
    }

    Write-Host "Restored leads: $($LeadCount.Trim())"
    Write-Host "Restored status events: $($HistoryCount.Trim())"
    Write-Host "CRM restore test passed."
}
finally {
    & docker exec crm-postgres dropdb `
        -U crm_user `
        --if-exists `
        --force `
        $TestDatabase | Out-Null
    & docker exec crm-postgres rm -f $ContainerDump | Out-Null
}
