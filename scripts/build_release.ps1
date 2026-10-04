param(
    [string]$Version = "0.1.0",
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root

function Remove-WorkspaceDirectory {
    param([Parameter(Mandatory = $true)][string]$Path)

    $resolved = [System.IO.Path]::GetFullPath($Path)
    $rootPath = [System.IO.Path]::GetFullPath($Root)
    $prefix = $rootPath.TrimEnd('\') + '\'

    if (-not $resolved.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "拒绝删除工作区外目录: $resolved"
    }

    if (Test-Path -LiteralPath $resolved) {
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
}

$python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "未找到虚拟环境: $python"
}

foreach ($target in @(
    (Join-Path $Root "build"),
    (Join-Path $Root "dist"),
    (Join-Path $Root "release")
)) {
    Remove-WorkspaceDirectory -Path $target
}

New-Item -ItemType Directory -Force -Path (Join-Path $Root "release") | Out-Null

$env:QT_QPA_PLATFORM = "offscreen"
$env:PYTHONPATH = "src"

& $python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) {
    throw "单元测试失败"
}

& $python -m jingwei --smoke-test
if ($LASTEXITCODE -ne 0) {
    throw "源码冒烟测试失败"
}

& $python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name JingweiZhizao `
    --distpath dist `
    --workpath build\pyinstaller `
    --specpath build\spec `
    --paths src `
    src\jingwei\__main__.py
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller构建失败"
}

$appDir = Join-Path $Root "dist\JingweiZhizao"
$appExe = Join-Path $appDir "JingweiZhizao.exe"
if (-not (Test-Path -LiteralPath $appExe)) {
    throw "未生成应用可执行文件: $appExe"
}

$processInfo = [System.Diagnostics.ProcessStartInfo]::new()
$processInfo.FileName = $appExe
$processInfo.Arguments = "--smoke-test"
$processInfo.UseShellExecute = $false
$processInfo.CreateNoWindow = $true

$packagedProcess = [System.Diagnostics.Process]::Start($processInfo)
if (-not $packagedProcess.WaitForExit(60000)) {
    $packagedProcess.Kill($true)
    throw "打包程序冒烟测试超时"
}
if ($packagedProcess.ExitCode -ne 0) {
    throw "打包程序冒烟测试失败，退出码: $($packagedProcess.ExitCode)"
}

$portableZip = Join-Path $Root "release\JingweiZhizao-Portable-$Version.zip"
Compress-Archive -Path $appDir -DestinationPath $portableZip -CompressionLevel Optimal -Force

if (-not $SkipInstaller) {
$isccCandidates = @(
    (Get-Command ISCC.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
    (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"),
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }

if (-not $isccCandidates) {
    throw "未找到Inno Setup编译器ISCC.exe，请先安装Inno Setup 6"
}

$iscc = @($isccCandidates)[0]
& $iscc `
    "/DMyAppVersion=$Version" `
    "/DMyOutputBaseFilename=JingweiZhizao-Setup-$Version" `
    "packaging\windows\installer.iss"
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup构建失败"
}

$installerPath = Join-Path $Root "release\JingweiZhizao-Setup-$Version.exe"
if (-not (Test-Path -LiteralPath $installerPath)) {
    throw "未生成安装程序: $installerPath"
}
}

$hashAssets = @($portableZip)
$installerPath = Join-Path $Root "release\JingweiZhizao-Setup-$Version.exe"
if (Test-Path -LiteralPath $installerPath) {
    $hashAssets += $installerPath
}
$hashLines = @()
foreach ($asset in $hashAssets) {
    $hash = (Get-FileHash -LiteralPath $asset -Algorithm SHA256).Hash.ToLowerInvariant()
    $hashLines += "$hash  $([System.IO.Path]::GetFileName($asset))"
}
[System.IO.File]::WriteAllLines(
    (Join-Path $Root "release\SHA256SUMS.txt"),
    $hashLines,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host "发布资产已生成:"
Get-ChildItem -LiteralPath (Join-Path $Root "release") -File |
    Select-Object Name, Length |
    Format-Table -AutoSize