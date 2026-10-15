BeforeAll {
    $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
    $script:GfxPath = Join-Path $script:RepoRoot "interface\nato_counters_expanded.gfx"
    $script:ManifestPath = Join-Path $script:RepoRoot "assets\counters\index_manifest.json"
    $script:CountersRoot = Join-Path $script:RepoRoot "gfx\interface\counters"
    $script:FirstIndex = 1080
    $script:SizeRules = @{
        large = @{ Width = 76; Height = 42; Folder = 'division_templates_large'; Suffix = 'designer' }
        small = @{ Width = 56; Height = 31; Folder = 'division_templates_small'; Suffix = 'map' }
    }

    $gfxContent = [System.IO.File]::ReadAllText($script:GfxPath, [System.Text.Encoding]::UTF8)
    $spritePattern = 'name\s*=\s*"GFX_div_templ_(\d+)_(large|small)"\s+textureFile\s*=\s*"([^"]+)"'
    $script:Sprites = @([regex]::Matches($gfxContent, $spritePattern) | ForEach-Object {
            [PSCustomObject]@{
                Index       = [int]$_.Groups[1].Value
                Size        = $_.Groups[2].Value
                TextureFile = $_.Groups[3].Value
            }
        })
    $script:LargeIndices = @($script:Sprites | Where-Object { $_.Size -eq 'large' } | ForEach-Object { $_.Index } | Sort-Object)
    $script:SmallIndices = @($script:Sprites | Where-Object { $_.Size -eq 'small' } | ForEach-Object { $_.Index } | Sort-Object)

    $manifest = (Get-Content -LiteralPath $script:ManifestPath -Raw | ConvertFrom-Json).counters
    $script:ManifestEntries = @($manifest.PSObject.Properties | ForEach-Object {
            [PSCustomObject]@{ Key = $_.Name; Index = [int]$_.Value }
        })

    function Get-DdsHeader {
        param([string]$Path)
        $stream = [System.IO.File]::OpenRead($Path)
        try {
            $header = New-Object byte[] 128
            [void]$stream.Read($header, 0, 128)
            return [PSCustomObject]@{
                Magic       = [System.Text.Encoding]::ASCII.GetString($header, 0, 4)
                Height      = [BitConverter]::ToUInt32($header, 12)
                Width       = [BitConverter]::ToUInt32($header, 16)
                FourCC      = [BitConverter]::ToUInt32($header, 84)
                BitCount    = [BitConverter]::ToUInt32($header, 88)
                PayloadSize = $stream.Length - 128
            }
        }
        finally {
            $stream.Dispose()
        }
    }
}

Describe "Counter sprite definitions" {
    It "sprite file is saved without UTF-8 BOM" {
        $bytes = [System.IO.File]::ReadAllBytes($script:GfxPath)
        ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) | Should -Be $false
    }

    It "defines at least one counter" {
        $script:LargeIndices.Count | Should -BeGreaterThan 0
    }

    It "never redefines an icon index of RBM's GFX Overhaul, the game or its DLC (below 1080)" {
        @($script:Sprites | Where-Object { $_.Index -lt $script:FirstIndex }).Count | Should -Be 0
    }

    It "uses one unbroken index range starting right after RBM's last icon, 1080 [LIM-002]" {
        $expected = @($script:FirstIndex..($script:FirstIndex + $script:LargeIndices.Count - 1))
        ($script:LargeIndices -join ',') | Should -Be ($expected -join ',')
    }

    It "ships every echelon and colour of every symbol" {
        $symbols = @($script:ManifestEntries | ForEach-Object { ($_.Key -split '\.')[0] } | Sort-Object -Unique)
        $script:ManifestEntries.Count | Should -Be ($symbols.Count * 48)
    }

    It "defines a large and a small sprite for every index" {
        ($script:SmallIndices -join ',') | Should -Be ($script:LargeIndices -join ',')
    }

    It "matches the saved index manifest" {
        $fromManifest = @(foreach ($entry in $script:ManifestEntries) {
                foreach ($sizeName in @('large', 'small')) {
                    $rule = $script:SizeRules[$sizeName]
                    "{0}|{1}|gfx/interface/counters/{2}/nce.{3}.{4}.dds" -f $entry.Index, $sizeName, $rule.Folder, $entry.Key, $rule.Suffix
                }
            }) | Sort-Object
        $fromGfx = @($script:Sprites | ForEach-Object { "{0}|{1}|{2}" -f $_.Index, $_.Size, $_.TextureFile }) | Sort-Object
        ($fromGfx -join "`n") | Should -Be ($fromManifest -join "`n")
    }
}

Describe "Counter textures" {
    It "every sprite points to an existing texture" {
        $missing = @($script:Sprites | Where-Object { -not (Test-Path -LiteralPath (Join-Path $script:RepoRoot $_.TextureFile)) })
        $missing.Count | Should -Be 0
    }

    It "every texture is an uncompressed 32-bit DDS of the size RBM's GFX Overhaul uses" {
        $wrong = @(foreach ($sprite in $script:Sprites) {
                $rule = $script:SizeRules[$sprite.Size]
                $header = Get-DdsHeader -Path (Join-Path $script:RepoRoot $sprite.TextureFile)
                $isExpected = $header.Magic -eq 'DDS ' -and $header.Width -eq $rule.Width -and $header.Height -eq $rule.Height -and
                    $header.FourCC -eq 0 -and $header.BitCount -eq 32 -and $header.PayloadSize -eq ($rule.Width * $rule.Height * 4)
                if (-not $isExpected) { $sprite.TextureFile }
            })
        $wrong.Count | Should -Be 0
    }

    It "has no generated texture without a sprite" {
        $referenced = @($script:Sprites | ForEach-Object { [System.IO.Path]::GetFileName($_.TextureFile) })
        $onDisk = @(Get-ChildItem -LiteralPath $script:CountersRoot -Recurse -File -Filter 'nce.*.dds' | ForEach-Object { $_.Name })
        @($onDisk | Where-Object { $referenced -notcontains $_ }).Count | Should -Be 0
    }
}

Describe "Expansion only: nothing from RBM's GFX Overhaul or vanilla is replaced" {
    It "defines no sprite other than division template icons" {
        $gfxContent = [System.IO.File]::ReadAllText($script:GfxPath, [System.Text.Encoding]::UTF8)
        $allNames = @([regex]::Matches($gfxContent, 'name\s*=\s*"([^"]+)"') | ForEach-Object { $_.Groups[1].Value })
        @($allNames | Where-Object { $_ -notmatch '^GFX_div_templ_\d+_(large|small)$' }).Count | Should -Be 0
        $allNames.Count | Should -Be $script:Sprites.Count
    }

    It "ships only its own sprite file in interface" {
        $interfaceFiles = @(Get-ChildItem -LiteralPath (Join-Path $script:RepoRoot "interface") -Recurse -File | ForEach-Object { $_.Name })
        ($interfaceFiles -join ',') | Should -Be 'nato_counters_expanded.gfx'
    }

    It "ships only textures carrying this mod's file prefix" {
        $foreign = @(Get-ChildItem -LiteralPath (Join-Path $script:RepoRoot "gfx") -Recurse -File | Where-Object { $_.Name -notmatch '^nce\..+\.(designer|map)\.dds$' })
        $foreign.Count | Should -Be 0
    }

    It "does not use replace_path" {
        $descriptor = [System.IO.File]::ReadAllText((Join-Path $script:RepoRoot "descriptor.mod"), [System.Text.Encoding]::UTF8)
        $descriptor | Should -Not -Match 'replace_path'
    }

    It "declares RBM's GFX Overhaul as a dependency" {
        $descriptor = [System.IO.File]::ReadAllText((Join-Path $script:RepoRoot "descriptor.mod"), [System.Text.Encoding]::UTF8)
        $descriptor | Should -Match "dependencies\s*=\s*\{[^}]*`"RBM's GFX Overhaul`""
    }
}
