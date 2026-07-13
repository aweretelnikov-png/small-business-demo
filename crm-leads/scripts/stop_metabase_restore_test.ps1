$ErrorActionPreference = "Stop"

$VolumeName = "crm_metabase_restore_test"
$CopyContainer = "metabase-restore-copy"
$TestContainer = "metabase-restore-test"

& cmd.exe /c "docker rm -f $TestContainer >nul 2>&1"
& cmd.exe /c "docker rm -f $CopyContainer >nul 2>&1"
& cmd.exe /c "docker volume rm $VolumeName >nul 2>&1"

Write-Host "Temporary Metabase restore environment removed."
