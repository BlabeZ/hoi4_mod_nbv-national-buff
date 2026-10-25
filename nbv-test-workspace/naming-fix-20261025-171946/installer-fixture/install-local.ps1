param(
    [string]$UserDirectory = (Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Paradox Interactive\Hearts of Iron IV')
)
$ErrorActionPreference = 'Stop'
$nbvRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path.Replace('\', '/')
$nbvModDirectory = Join-Path $UserDirectory 'mod'
$nbvDescriptor = Join-Path $nbvModDirectory 'nbv_national_buff.mod'
$nbvSourceDescriptor = Join-Path $PSScriptRoot 'descriptor.mod'
$nbvBody = Get-Content -LiteralPath $nbvSourceDescriptor -Raw -Encoding UTF8
if ($nbvBody -notmatch '(?m)^\s*name\s*=\s*"[^"\r\n]+"\s*$') {
    throw 'descriptor.mod must contain a display name; no registration changed.'
}
New-Item -ItemType Directory -Path $nbvModDirectory -Force | Out-Null
if (Test-Path -LiteralPath $nbvDescriptor) {
    $nbvExisting = Get-Content -LiteralPath $nbvDescriptor -Raw -Encoding UTF8
    $nbvKnownPath = $nbvExisting -match ('(?m)^path="' + [regex]::Escape($nbvRoot) + '"\s*$')
    if ($nbvExisting -notmatch '# NBV local registration' -and -not $nbvKnownPath) {
        throw "A different descriptor already exists at $nbvDescriptor; it has not been overwritten."
    }
    # A launcher may keep the Workshop ID in the local registration only.
    # Retain it when absent in the source, and stop on conflicting IDs.
    $nbvIdPattern = '(?m)^\s*remote_file_id\s*=\s*"([0-9]+)"\s*$'
    $nbvExistingId = [regex]::Match($nbvExisting, $nbvIdPattern)
    $nbvSourceId = [regex]::Match($nbvBody, $nbvIdPattern)
    if ($nbvExistingId.Success -and $nbvSourceId.Success -and $nbvExistingId.Groups[1].Value -ne $nbvSourceId.Groups[1].Value) {
        throw 'Conflicting Workshop IDs; existing registration has not been overwritten.'
    }
    if ($nbvExistingId.Success -and -not $nbvSourceId.Success) {
        $nbvBody = $nbvBody.TrimEnd() + "`n" + $nbvExistingId.Value.Trim() + "`n"
    }
}
$nbvBody = [regex]::Replace($nbvBody, '(?m)^\s*path\s*=.*(?:\r?\n|$)', '')
$nbvBody = "# NBV local registration`n" + $nbvBody.TrimEnd() + "`npath=`"$nbvRoot`"`n"
[IO.File]::WriteAllText($nbvDescriptor, $nbvBody, [Text.UTF8Encoding]::new($false))
Write-Output "Registered: $nbvDescriptor"
Write-Output 'Display name and publishing metadata copied from descriptor.mod. Existing playsets have not been edited.'
