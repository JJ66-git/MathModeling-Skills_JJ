param(
    [string]$SevenZipPath = 'C:\Program Files\7-Zip\7z.exe'
)

$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path (Split-Path -Parent $PSScriptRoot) 'package_supporting_materials.ps1'

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) {
        throw "ASSERTION FAILED: $Message"
    }
}

if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
    throw "Production script is missing: $scriptPath"
}
if (-not (Test-Path -LiteralPath $SevenZipPath -PathType Leaf)) {
    throw "7-Zip is missing: $SevenZipPath"
}

$tempRoot = Join-Path $env:TEMP ("supporting-materials-test-" + [guid]::NewGuid().ToString('N'))
try {
    $source = Join-Path $tempRoot 'supporting-materials'
    $codeDir = Join-Path $source 'code'
    $output = Join-Path $tempRoot 'supporting-materials.zip'
    $extract = Join-Path $tempRoot 'extracted'
    New-Item -ItemType Directory -Path $codeDir, $extract -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $codeDir 'main.py') -Value 'print("ok")' -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $source 'AI 工具使用详情.pdf') -Value 'test-pdf-content' -Encoding UTF8

    & $scriptPath -SourceDirectory $source -OutputZip $output -SevenZipPath $SevenZipPath | Out-Null

    Assert-True (Test-Path -LiteralPath $output -PathType Leaf) 'ZIP was not created.'
    Assert-True ((Get-Item -LiteralPath $output).Length -lt 20MB) 'ZIP is not below 20 MiB.'

    & $SevenZipPath t -bd -y $output | Out-Null
    Assert-True ($LASTEXITCODE -eq 0) '7-Zip integrity test failed.'

    & $SevenZipPath x -bd -y "-o$extract" $output | Out-Null
    Assert-True ($LASTEXITCODE -eq 0) 'ZIP extraction failed.'
    $manifestPath = Join-Path $extract '支撑材料文件清单.md'
    Assert-True (Test-Path -LiteralPath $manifestPath -PathType Leaf) 'Manifest is not included in the ZIP.'
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8
    Assert-True ($manifest.Contains('code/main.py')) 'Manifest does not list code/main.py.'
    Assert-True ($manifest.Contains('AI 工具使用详情.pdf')) 'Manifest does not list the AI detail PDF.'
    Assert-True ($manifest.Contains('SHA-256')) 'Manifest does not include SHA-256 hashes.'

    $smallLimitSource = Join-Path $tempRoot 'over-limit-source'
    $smallLimitOutput = Join-Path $tempRoot 'over-limit.zip'
    New-Item -ItemType Directory -Path $smallLimitSource -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $smallLimitSource 'payload.txt') -Value ('x' * 2048) -Encoding UTF8
    $failedAsExpected = $false
    try {
        & $scriptPath -SourceDirectory $smallLimitSource -OutputZip $smallLimitOutput -SevenZipPath $SevenZipPath -MaxBytes 100 | Out-Null
    }
    catch {
        $failedAsExpected = $_.Exception.Message -match 'size limit'
    }
    Assert-True $failedAsExpected 'Oversized archive did not fail the size gate.'
    Assert-True (-not (Test-Path -LiteralPath $smallLimitOutput)) 'Oversized archive was not removed.'

    Write-Output 'ALL_TESTS_PASS'
}
finally {
    if (Test-Path -LiteralPath $tempRoot) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force
    }
}
