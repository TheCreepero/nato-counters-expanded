[CmdletBinding(DefaultParameterSetName = 'Deploy')]
param(
    [Parameter(ParameterSetName = 'Deploy')]
    [switch]$Deploy,

    [Parameter(ParameterSetName = 'DevLink')]
    [switch]$DevLink,

    [Parameter(ParameterSetName = 'Package')]
    [switch]$Package,

    [Parameter(ParameterSetName = 'PublishSteam')]
    [switch]$PublishSteam,

    [Parameter(ParameterSetName = 'InstallSteamCmd')]
    [switch]$InstallSteamCmd,

    [Parameter(ParameterSetName = 'ValidateOnly')]
    [switch]$ValidateOnly,

    [Parameter(ParameterSetName = 'Test')]
    [switch]$Test,

    [switch]$Validate,
    [switch]$NoValidate,
    [switch]$Clean,

    [string]$ModDir,
    [string]$ZipOutput,
    [string]$SteamUser,
    [string]$ChangeNote,
    [string]$SteamCmdPath,
    [switch]$DryRun,
    [switch]$UpdateDescription
)

$ErrorActionPreference = 'Stop'

if ($PublishSteam -and -not $DryRun) {
    Write-Host 'NATO Counters Expanded is a local mod and is never uploaded to the Steam Workshop (AGENTS.md, section 5.0).' -ForegroundColor Red
    Write-Host 'Its counters can only be picked with the icon picker limit raised in hoi4.exe on this machine.' -ForegroundColor Red
    exit 1
}
. (Join-Path $PSScriptRoot 'tools\HoiModBuild.ps1')

function Write-PickerLimitCheck {
    $manifestPath = Join-Path $PSScriptRoot 'assets\counters\index_manifest.json'
    $highestIndex = (([System.IO.File]::ReadAllText($manifestPath) | ConvertFrom-Json).counters.PSObject.Properties | Measure-Object -Property Value -Maximum).Maximum
    $managerRoot = Get-ModManagerRoot
    if (-not $managerRoot) {
        Write-Host '  [WARN] The Modding Manager was not found, so the icon picker limit of hoi4.exe was not checked.' -ForegroundColor Yellow
        return
    }
    try {
        . (Join-Path $managerRoot 'Scripts\Executable\HoiExecutable.Common.ps1')
        $state = Get-HoiExecutableState -GameRoot (Resolve-Hoi4Install)
    }
    catch {
        Write-Host "  [WARN] The icon picker limit of hoi4.exe was not checked: $($_.Exception.Message)" -ForegroundColor Yellow
        return
    }
    if ($state.Picker.CurrentLimit -gt $highestIndex) {
        Write-Host "  [OK] hoi4.exe lists icon indices below $($state.Picker.CurrentLimit): this mod's counters up to $highestIndex can be picked" -ForegroundColor Green
    }
    else {
        Write-Host "  [WARN] hoi4.exe lists only icon indices below $($state.Picker.CurrentLimit), so none of this mod's counters (1080 to $highestIndex) can be picked." -ForegroundColor Yellow
        Write-Host "         A game update replaces the executable. Patch it again: $managerRoot\Scripts\Executable\Set-HoiIconPickerLimit.ps1" -ForegroundColor Yellow
    }
}

$buildConfig = Get-ModBuildConfig -RepoDir $PSScriptRoot -ModDir $ModDir
$buildParameters = Select-ModBuildParameters -BoundParameters $PSBoundParameters
$exitCode = Invoke-ModBuild -Config $buildConfig @buildParameters
if ($exitCode -eq 0 -and -not $Clean -and $PSCmdlet.ParameterSetName -in @('Deploy', 'DevLink')) {
    Write-PickerLimitCheck
}
exit $exitCode
