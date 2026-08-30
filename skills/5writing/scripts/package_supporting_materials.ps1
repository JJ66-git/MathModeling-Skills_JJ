[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SourceDirectory,

    [Parameter(Mandatory = $true)]
    [string]$OutputZip,

    [string]$SevenZipPath,

    [long]$MaxBytes = 20MB
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-SevenZip {
    param([string]$RequestedPath)

    if ($RequestedPath) {
        if (-not (Test-Path -LiteralPath $RequestedPath -PathType Leaf)) {
            throw "7-Zip executable not found: $RequestedPath"
        }
        return (Resolve-Path -LiteralPath $RequestedPath).Path
    }

    $command = Get-Command 7z.exe, 7z -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command) {
        return $command.Source
    }

    foreach ($candidate in @(
        'C:\Program Files\7-Zip\7z.exe',
        'C:\Program Files (x86)\7-Zip\7z.exe',
        (Join-Path $env:LOCALAPPDATA 'Programs\7-Zip\7z.exe')
    )) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }

    throw '7-Zip was not found. Install 7-Zip or pass -SevenZipPath.'
}

if ($MaxBytes -le 0) {
    throw 'MaxBytes must be positive.'
}
if ([IO.Path]::GetExtension($OutputZip) -ine '.zip') {
    throw 'OutputZip must use the .zip extension.'
}
if (-not (Test-Path -LiteralPath $SourceDirectory -PathType Container)) {
    throw "Supporting-materials directory not found: $SourceDirectory"
}

$sourcePath = (Resolve-Path -LiteralPath $SourceDirectory).Path.TrimEnd('\', '/')
$outputPath = [IO.Path]::GetFullPath($OutputZip)
$sourcePrefix = $sourcePath + [IO.Path]::DirectorySeparatorChar
if ($outputPath.StartsWith($sourcePrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'OutputZip must be outside SourceDirectory so the archive cannot include itself.'
}

$sevenZip = Resolve-SevenZip -RequestedPath $SevenZipPath
$manifestName = '支撑材料文件清单.md'
$manifestPath = Join-Path $sourcePath $manifestName

$materials = @(
    Get-ChildItem -LiteralPath $sourcePath -Recurse -File |
        Where-Object { $_.FullName -ine $manifestPath } |
        Sort-Object FullName
)
if ($materials.Count -eq 0) {
    throw 'No supporting-material files were found. Do not create an empty archive.'
}

$prohibitedNames = @(
    $materials | Where-Object {
        $_.FullName.Substring($sourcePath.Length + 1) -match '(承诺书|编号专用页|commitment|numbering.?page)'
    }
)
if ($prohibitedNames.Count -gt 0) {
    $paths = ($prohibitedNames | ForEach-Object { $_.FullName.Substring($sourcePath.Length + 1) }) -join ', '
    throw "Prohibited commitment or numbering-page material found: $paths"
}

$rows = foreach ($file in $materials) {
    $relativePath = $file.FullName.Substring($sourcePath.Length + 1).Replace('\', '/')
    $escapedPath = $relativePath.Replace('|', '\|')
    $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    "| $escapedPath | $($file.Length) | $hash |"
}

$manifest = @(
    '# 支撑材料文件清单'
    ''
    "材料文件总数：$($materials.Count)"
    ''
    '| 相对路径 | 大小（字节） | SHA-256 |'
    '| --- | ---: | --- |'
    $rows
    ''
    '> 本清单文件自身不参与自校验；论文附录中的文件列表应与本清单逐项一致。'
) -join "`r`n"
Set-Content -LiteralPath $manifestPath -Value $manifest -Encoding UTF8

$outputParent = Split-Path -Parent $outputPath
if (-not (Test-Path -LiteralPath $outputParent -PathType Container)) {
    New-Item -ItemType Directory -Path $outputParent -Force | Out-Null
}
if (Test-Path -LiteralPath $outputPath) {
    Remove-Item -LiteralPath $outputPath -Force
}

try {
    Push-Location $sourcePath
    try {
        & $sevenZip a -tzip -mx=9 -mmt=on -bd -y $outputPath '.\*' | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "7-Zip archive creation failed with exit code $LASTEXITCODE."
        }
    }
    finally {
        Pop-Location
    }

    $archive = Get-Item -LiteralPath $outputPath
    if ($archive.Length -ge $MaxBytes) {
        throw "Archive exceeds the size limit: $($archive.Length) bytes (limit requires less than $MaxBytes bytes)."
    }

    & $sevenZip t -bd -y $outputPath | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "7-Zip integrity test failed with exit code $LASTEXITCODE."
    }

    [pscustomobject]@{
        ArchivePath = $archive.FullName
        SizeBytes = $archive.Length
        SizeMiB = [math]::Round($archive.Length / 1MB, 3)
        Sha256 = (Get-FileHash -LiteralPath $archive.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        ManifestPath = $manifestPath
        MaterialFileCount = $materials.Count
    }
}
catch {
    if (Test-Path -LiteralPath $outputPath) {
        Remove-Item -LiteralPath $outputPath -Force
    }
    throw
}
