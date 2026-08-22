# material_converter Windows 环境引导脚本
# 用法: 在仓库根目录的 PowerShell 中执行
#   powershell -ExecutionPolicy Bypass -File apps\tools\material_converter\bootstrap.ps1
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
Set-Location $repo

Write-Host "== 1/3 检查 Python =="
try { python --version } catch { Write-Error "未找到 python，请先安装 Python 3.10+ 并加入 PATH" }

Write-Host "== 2/3 创建虚拟环境 .venv =="
if (-not (Test-Path ".venv")) { python -m venv .venv }
.\.venv\Scripts\pip.exe install -q --upgrade pip
.\.venv\Scripts\pip.exe install -q -r apps\tools\material_converter\requirements.txt

Write-Host "== 3/3 检查 LibreOffice（doc/ppt 及矢量公式转换需要）=="
$soffice = @(
  "$env:ProgramFiles\LibreOffice\program\soffice.exe",
  "${env:ProgramFiles(x86)}\LibreOffice\program\soffice.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($soffice) {
  Write-Host "   找到: $soffice （已写入用户环境变量 MMD_SOFFICE）"
  [Environment]::SetEnvironmentVariable("MMD_SOFFICE", $soffice, "User")
} else {
  Write-Warning "   未找到 LibreOffice。请从 https://www.libreoffice.org 安装后重开终端，"
  Write-Warning "   或手动设置: setx MMD_SOFFICE ""C:\Program Files\LibreOffice\program\soffice.exe"""
}

Write-Host ""
Write-Host "完成。常用命令（在仓库根目录）:"
Write-Host "  .\.venv\Scripts\python.exe -m material_converter.main --course 线性代数 --validate   # 需先 cd apps\tools\material_converter"
Write-Host "  详见 apps\tools\material_converter\README.md"
