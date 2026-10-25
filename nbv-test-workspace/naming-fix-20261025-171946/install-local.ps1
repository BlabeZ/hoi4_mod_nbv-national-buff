param(
    [string]$UserDirectory = (Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Paradox Interactive\Hearts of Iron IV')
)
$ErrorActionPreference = 'Stop'
$nbvRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path.Replace('\', '/')
$nbvModDirectory = Join-Path $UserDirectory 'mod'
$nbvDescriptor = Join-Path $nbvModDirectory 'nbv_national_buff.mod'
New-Item -ItemType Directory -Path $nbvModDirectory -Force | Out-Null
if (Test-Path -LiteralPath $nbvDescriptor) {
    $nbvExisting = Get-Content -LiteralPath $nbvDescriptor -Raw -Encoding UTF8
    $nbvKnownName = $nbvExisting -match '(?m)^name="国家BUFF统计 UI"\s*$'
    $nbvKnownPath = $nbvExisting -match ('(?m)^path="' + [regex]::Escape($nbvRoot) + '"\s*$')
    if ($nbvExisting -notmatch '# NBV local registration' -and -not ($nbvKnownName -and $nbvKnownPath)) {
        throw "A different descriptor already exists at $nbvDescriptor; it has not been overwritten."
    }
}
$nbvBody = @"
# NBV local registration
name="国家BUFF统计 UI"
version="0.1.11"
supported_version="1.19.*"
path="$nbvRoot"
tags={ "Utilities" "Gameplay" }
"@
[IO.File]::WriteAllText($nbvDescriptor, $nbvBody + "`n", [Text.UTF8Encoding]::new($false))
Write-Output "Registered: $nbvDescriptor"
Write-Output "Enable 国家BUFF统计 UI in a launcher playset. Existing playsets have not been edited."
