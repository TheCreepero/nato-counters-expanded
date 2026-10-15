BeforeAll {
    $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    . (Join-Path $script:RepoRoot 'tools\HoiModBuild.ps1')
    $script:BuildConfig = Get-ModBuildConfig -RepoDir $script:RepoRoot
}

Describe 'build.ps1 configuration' {
    It 'ships the gfx and interface folders with the descriptor and thumbnail' {
        $shippedTopLevel = @(Get-ModContentFiles -Config $script:BuildConfig | ForEach-Object { ($_ -split '/')[0] } | Sort-Object -Unique)
        $shippedTopLevel | Should -Be @('descriptor.mod', 'gfx', 'interface', 'thumbnail.png')
    }

    It 'installs as nato-counters-expanded and packages nato-counters-expanded.zip' {
        $script:BuildConfig.ModFolderName | Should -Be 'nato-counters-expanded'
        $script:BuildConfig.ZipArchiveName | Should -Be 'nato-counters-expanded.zip'
        $script:BuildConfig.PackageLayout | Should -Be 'Flat'
    }
}
