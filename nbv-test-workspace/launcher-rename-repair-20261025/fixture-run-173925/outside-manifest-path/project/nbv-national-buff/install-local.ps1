param(
    [string]$UserDirectory = (Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Paradox Interactive\Hearts of Iron IV'),
    [string]$DisplayName
)
$ErrorActionPreference = 'Stop'
$nbvSource = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$nbvModDirectory = [IO.Path]::GetFullPath((Join-Path $UserDirectory 'mod'))
$nbvInstallId = 'nbv-national-buff-local-install-v1'
$nbvUtf8 = [Text.UTF8Encoding]::new($false)

function Get-NbvField([string]$Text, [string]$Field) {
    $matchesFound = [regex]::Matches($Text, ('(?m)^[ \t]*' + [regex]::Escape($Field) + '[ \t]*=[ \t]*"([^"\r\n]*)"[ \t]*\r?$'))
    if ($matchesFound.Count -gt 1) { throw "Duplicate descriptor field: $Field" }
    if ($matchesFound.Count -eq 1) { return $matchesFound[0].Groups[1].Value }
    return $null
}
function Set-NbvField([string]$Text, [string]$Field, [string]$Value) {
    if ($Value -match '["\r\n]') { throw "Invalid descriptor field: $Field" }
    $pattern = '(?m)^[ \t]*' + [regex]::Escape($Field) + '[ \t]*=.*(?:\r?\n|$)'
    return ([regex]::Replace($Text, $pattern, '').TrimEnd() + "`n$Field=`"$Value`"`n")
}
function Test-NbvChild([string]$Path, [string]$Parent) {
    return [IO.Path]::GetFullPath($Path).StartsWith($Parent.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)
}

$nbvBody = Get-Content -LiteralPath (Join-Path $nbvSource 'descriptor.mod') -Raw -Encoding UTF8
if (-not (Get-NbvField $nbvBody 'name')) { throw 'descriptor.mod must contain a display name.' }
New-Item -ItemType Directory -Path $nbvModDirectory -Force | Out-Null
$nbvCandidates = @()
foreach ($nbvFile in Get-ChildItem -LiteralPath $nbvModDirectory -Filter '*.mod' -File) {
    $nbvText = Get-Content -LiteralPath $nbvFile.FullName -Raw -Encoding UTF8
    $nbvPath = Get-NbvField $nbvText 'path'
    if (-not $nbvPath -or -not [IO.Path]::IsPathRooted($nbvPath)) { continue }
    $nbvPath = [IO.Path]::GetFullPath($nbvPath)
    $nbvMarker = Join-Path $nbvPath '.nbv-install.json'
    $nbvManaged = $false
    if ((Split-Path -Parent $nbvPath) -eq $nbvModDirectory -and (Test-Path -LiteralPath $nbvMarker)) {
        $nbvManaged = (Get-Content -LiteralPath $nbvMarker -Raw -Encoding UTF8 | ConvertFrom-Json).install_id -eq $nbvInstallId
    }
    $nbvLegacy = $nbvFile.Name -eq 'nbv_national_buff.mod' -and $nbvPath -eq $nbvSource
    if ($nbvManaged -or $nbvLegacy) {
        $nbvCandidates += [pscustomobject]@{ Registration = $nbvFile.FullName; Path = $nbvPath; Text = $nbvText; Managed = $nbvManaged }
    }
}
if ($nbvCandidates.Count -gt 1) { throw 'Multiple NBV installations found; no installation changed.' }
$nbvRegistration = Join-Path $nbvModDirectory 'nbv_national_buff.mod'
$nbvTarget = Join-Path $nbvModDirectory 'nbv-national-buff'
$nbvPreviousFiles = @()
if ($nbvCandidates.Count -eq 1) {
    $nbvExisting = $nbvCandidates[0]
    $nbvRegistration = $nbvExisting.Registration
    if ($nbvExisting.Managed) {
        $nbvTarget = $nbvExisting.Path
        $nbvPreviousFiles = @((Get-Content -LiteralPath (Join-Path $nbvTarget '.nbv-install.json') -Raw -Encoding UTF8 | ConvertFrom-Json).files)
    }
    foreach ($nbvField in @('name', 'picture', 'remote_file_id')) {
        $nbvOldValue = Get-NbvField $nbvExisting.Text $nbvField
        $nbvNewValue = Get-NbvField $nbvBody $nbvField
        if ($nbvField -eq 'remote_file_id' -and $nbvOldValue -and $nbvNewValue -and $nbvOldValue -ne $nbvNewValue) {
            throw 'Conflicting Workshop IDs; no installation changed.'
        }
        if ($nbvOldValue) { $nbvBody = Set-NbvField $nbvBody $nbvField $nbvOldValue }
    }
} elseif (Test-Path -LiteralPath $nbvRegistration) {
    throw 'A different descriptor already uses nbv_national_buff.mod; no installation changed.'
}
if ($PSBoundParameters.ContainsKey('DisplayName')) {
    if ([string]::IsNullOrWhiteSpace($DisplayName)) { throw 'DisplayName must not be empty.' }
    $nbvBody = Set-NbvField $nbvBody 'name' $DisplayName
}
if ($nbvTarget -eq $nbvSource -or (Split-Path -Parent $nbvTarget) -ne $nbvModDirectory) { throw 'Unsafe installation target.' }
if ((Test-Path -LiteralPath $nbvTarget) -and -not ($nbvCandidates.Count -eq 1 -and $nbvCandidates[0].Managed)) {
    throw 'The installation directory already exists and is not managed by this installer.'
}
if ((Test-Path -LiteralPath $nbvTarget) -and ((Get-Item -LiteralPath $nbvTarget).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
    throw 'The installation target must be a real directory, not a link.'
}
if (Test-Path -LiteralPath $nbvTarget) {
    $nbvPending = [Collections.Generic.Stack[string]]::new()
    $nbvPending.Push($nbvTarget)
    while ($nbvPending.Count -gt 0) {
        foreach ($nbvChild in Get-ChildItem -LiteralPath $nbvPending.Pop() -Force) {
            if ($nbvChild.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked files or subdirectories are not allowed in the installation.' }
            if ($nbvChild.PSIsContainer) { $nbvPending.Push($nbvChild.FullName) }
        }
    }
}
$nbvFiles = @()
foreach ($nbvPart in @('common', 'gfx', 'interface', 'localisation')) {
    foreach ($nbvFile in Get-ChildItem -LiteralPath (Join-Path $nbvSource $nbvPart) -Recurse -File) {
        $nbvFiles += $nbvFile.FullName.Substring($nbvSource.Length + 1)
    }
}
foreach ($nbvPart in @('README.md', 'REFERENCE-AND-PORTING.md', 'TEST-REPORT.md')) {
    if (Test-Path -LiteralPath (Join-Path $nbvSource $nbvPart)) { $nbvFiles += $nbvPart }
}
$nbvPicture = Get-NbvField $nbvBody 'picture'
if ($nbvPicture) {
    $nbvPictureSource = [IO.Path]::GetFullPath((Join-Path $nbvSource $nbvPicture))
    $nbvPictureTarget = [IO.Path]::GetFullPath((Join-Path $nbvTarget $nbvPicture))
    if (-not (Test-NbvChild $nbvPictureSource $nbvSource) -or -not (Test-NbvChild $nbvPictureTarget $nbvTarget)) { throw 'Picture must be inside the mod directory.' }
    if (Test-Path -LiteralPath $nbvPictureSource) { $nbvFiles += $nbvPicture }
    elseif (-not (Test-Path -LiteralPath $nbvPictureTarget)) { throw 'The descriptor picture is missing.' }
}
$nbvFiles = @($nbvFiles | Select-Object -Unique)
foreach ($nbvRelative in $nbvPreviousFiles) {
    $nbvOldFile = [IO.Path]::GetFullPath((Join-Path $nbvTarget $nbvRelative))
    if (-not (Test-NbvChild $nbvOldFile $nbvTarget)) { throw 'Unsafe path in installation manifest.' }
}
New-Item -ItemType Directory -Path $nbvTarget -Force | Out-Null
foreach ($nbvRelative in $nbvFiles) {
    $nbvDestination = Join-Path $nbvTarget $nbvRelative
    New-Item -ItemType Directory -Path (Split-Path -Parent $nbvDestination) -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $nbvSource $nbvRelative) -Destination $nbvDestination -Force
}
foreach ($nbvRelative in $nbvPreviousFiles) {
    if ($nbvRelative -notin $nbvFiles -and $nbvRelative -ne $nbvPicture) {
        $nbvOldFile = [IO.Path]::GetFullPath((Join-Path $nbvTarget $nbvRelative))
        if (Test-Path -LiteralPath $nbvOldFile -PathType Leaf) { Remove-Item -LiteralPath $nbvOldFile }
    }
}
$nbvBody = [regex]::Replace($nbvBody, '(?m)^[ \t]*path[ \t]*=.*(?:\r?\n|$)', '').TrimEnd() + "`n"
[IO.File]::WriteAllText((Join-Path $nbvTarget 'descriptor.mod'), $nbvBody, $nbvUtf8)
$nbvExternal = "# NBV local registration`n" + (Set-NbvField $nbvBody 'path' $nbvTarget.Replace('\', '/'))
[IO.File]::WriteAllText($nbvRegistration, $nbvExternal, $nbvUtf8)
$nbvManifest = @{ install_id = $nbvInstallId; source = $nbvSource; files = $nbvFiles; registration = (Split-Path -Leaf $nbvRegistration) } | ConvertTo-Json -Depth 4
[IO.File]::WriteAllText((Join-Path $nbvTarget '.nbv-install.json'), $nbvManifest, $nbvUtf8)
Write-Output "Installed: $nbvTarget"
Write-Output "Registered: $nbvRegistration"
Write-Output 'Restart the launcher to reload the installation. Existing playsets have not been edited.'
