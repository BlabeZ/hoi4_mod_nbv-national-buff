$ErrorActionPreference = 'Stop'
$nbvGame = 'E:\Steam\steamapps\common\Hearts of Iron IV'
$nbvWork = 'D:\projects\hoi4_mod\1\nbv-test-workspace'
$nbvConfig = Join-Path $nbvGame 'launcher-settings.json'
$nbvBackup = Join-Path $nbvWork 'launcher-settings.v018-original.json'
$nbvPlayset = 'C:\Users\1\Documents\Paradox Interactive\Hearts of Iron IV\dlc_load.json'
$nbvLog = Join-Path $nbvWork 'profile\logs\game.log'
if (Get-Process hoi4 -ErrorAction SilentlyContinue) { throw 'HOI4 is running; no settings changed.' }
$nbvPreviousGameLog = if (Test-Path -LiteralPath $nbvLog) { [IO.File]::ReadAllText($nbvLog) } else { '' }
$nbvOriginalHash = (Get-FileHash -LiteralPath $nbvConfig -Algorithm SHA256).Hash
$nbvPlaysetHash = (Get-FileHash -LiteralPath $nbvPlayset -Algorithm SHA256).Hash
if (Test-Path -LiteralPath $nbvBackup) {
    if ((Get-FileHash -LiteralPath $nbvBackup -Algorithm SHA256).Hash -ne $nbvOriginalHash) {
        throw 'Existing backup differs from current launcher settings; no settings changed.'
    }
} else { Copy-Item -LiteralPath $nbvConfig -Destination $nbvBackup }
$nbvArchive = Join-Path $nbvWork ('before-v018-' + (Get-Date -Format yyyyMMdd-HHmmss))
New-Item -ItemType Directory -Path $nbvArchive | Out-Null
foreach ($nbvName in @('game.log', 'error.log')) {
    $nbvOldLog = Join-Path $nbvWork ('profile\logs\' + $nbvName)
    if (Test-Path -LiteralPath $nbvOldLog) { Copy-Item -LiteralPath $nbvOldLog -Destination $nbvArchive }
}
$nbvText = [IO.File]::ReadAllText($nbvConfig)
$nbvExpectedPath = '"gameDataPath": "%USER_DOCUMENTS%/Paradox Interactive/Hearts of Iron IV"'
if (-not $nbvText.Contains($nbvExpectedPath)) { throw 'Unexpected launcher profile path; no settings changed.' }
$nbvText = $nbvText.Replace($nbvExpectedPath, '"gameDataPath": "D:/projects/hoi4_mod/1/nbv-test-workspace/profile"')
$nbvChild = $null
$nbvComplete = $false
try {
    [IO.File]::WriteAllText($nbvConfig, $nbvText, [Text.UTF8Encoding]::new($false))
    $nbvChangedHash = (Get-FileHash -LiteralPath $nbvConfig -Algorithm SHA256).Hash
    $nbvChild = Start-Process -FilePath (Join-Path $nbvGame 'hoi4.exe') -WorkingDirectory $nbvGame -ArgumentList '-quickstart','-nolauncher','-debug','-start_tag=GER' -WindowStyle Hidden -PassThru
    $nbvStart = $nbvChild.StartTime
    $nbvLaunch = @{pid=$nbvChild.Id; started=$nbvStart.ToString('o'); config=$nbvConfig; backup=$nbvBackup; original_hash=$nbvOriginalHash; changed_hash=$nbvChangedHash; playset=$nbvPlayset; playset_hash=$nbvPlaysetHash}
    $nbvLaunch | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $nbvWork 'launch-v018.json') -Encoding utf8
    Write-Output ('Started isolated engine PID ' + $nbvChild.Id)
    $nbvDeadline = (Get-Date).AddSeconds(300)
    while ((Get-Date) -lt $nbvDeadline) {
        if ($nbvChild.HasExited) { throw 'Isolated game process exited before test completion.' }
        if (Test-Path -LiteralPath $nbvLog) {
            # The game retains write access and Windows may defer LastWriteTime.
            # Permit the existing writer and reject the exact previous log text.
            $nbvReader = $null
            try {
                $nbvStream = [IO.FileStream]::new($nbvLog, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
                $nbvReader = [IO.StreamReader]::new($nbvStream)
                $nbvContent = $nbvReader.ReadToEnd()
            } catch { $nbvContent = '' }
            finally { if ($nbvReader) { $nbvReader.Dispose() } }
            if ($nbvContent -ne $nbvPreviousGameLog -and $nbvContent.Contains('NBV_SMOKE_END')) { $nbvComplete = $true; break }
        }
        Start-Sleep -Seconds 2
    }
    if (-not $nbvComplete) { throw 'Isolated engine test did not complete within 300 seconds.' }
    Write-Output 'NBV_SMOKE_END found.'
} finally {
    if ($nbvChild) {
        $nbvActive = Get-Process -Id $nbvChild.Id -ErrorAction SilentlyContinue
        if ($nbvActive -and $nbvActive.ProcessName -eq 'hoi4' -and [Math]::Abs(($nbvActive.StartTime-$nbvStart).TotalSeconds) -lt 5) {
            Stop-Process -Id $nbvActive.Id
            Wait-Process -Id $nbvActive.Id -Timeout 20 -ErrorAction SilentlyContinue
        }
    }
    $nbvCurrentHash = (Get-FileHash -LiteralPath $nbvConfig -Algorithm SHA256).Hash
    if ($nbvCurrentHash -eq $nbvChangedHash) { Copy-Item -LiteralPath $nbvBackup -Destination $nbvConfig -Force }
    elseif ($nbvCurrentHash -ne $nbvOriginalHash) { throw 'Launcher settings changed externally; backup preserved for review.' }
    $nbvRestored = (Get-FileHash -LiteralPath $nbvConfig -Algorithm SHA256).Hash -eq $nbvOriginalHash
    $nbvPlaysetUnchanged = (Get-FileHash -LiteralPath $nbvPlayset -Algorithm SHA256).Hash -eq $nbvPlaysetHash
    @{completed=$nbvComplete; launcher_restored=$nbvRestored; playset_unchanged=$nbvPlaysetUnchanged} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $nbvWork 'cleanup-v018.json') -Encoding utf8
    Write-Output ('Launcher restored: ' + $nbvRestored + '; user playset unchanged: ' + $nbvPlaysetUnchanged)
    if (-not $nbvRestored -or -not $nbvPlaysetUnchanged) { throw 'Cleanup verification failed.' }
}
