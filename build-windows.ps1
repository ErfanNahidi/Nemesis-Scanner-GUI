$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$Python = (Get-Command python -ErrorAction Stop).Source
$BuildEnv = Join-Path $PSScriptRoot '.venv-windows-build'
$BuildPython = Join-Path $BuildEnv 'Scripts\python.exe'
$OutputDir = Join-Path $PSScriptRoot 'dist\windows'
$Version = (& $Python -c 'from nemesis_gui import __version__; print(__version__)').Trim()

if (-not (Test-Path $BuildPython)) {
  & $Python -m venv $BuildEnv
}
& $BuildPython -m pip install --disable-pip-version-check -r requirements.txt 'pyinstaller==6.21.0'
if ($LASTEXITCODE -ne 0) { throw 'Installing the Windows build dependencies failed.' }

Remove-Item (Join-Path $PSScriptRoot 'build') -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $PSScriptRoot 'NemesisScanner.spec') -Force -ErrorAction SilentlyContinue
New-Item $OutputDir -ItemType Directory -Force | Out-Null
Remove-Item (Join-Path $OutputDir 'NemesisScanner.exe') -Force -ErrorAction SilentlyContinue

$env:PYTHONHASHSEED = '0'
& $BuildPython -m PyInstaller --noconfirm --clean --onefile --windowed --optimize 2 `
  --name NemesisScanner --distpath $OutputDir --workpath (Join-Path $PSScriptRoot 'build\windows') `
  --icon 'NemesisScanner.ico' --add-data 'Logo-small.png;.' --add-data 'NemesisScanner.ico;.' --collect-data core `
  --hidden-import nmap --hidden-import requests `
  --exclude-module numpy --exclude-module scipy --exclude-module pandas `
  --exclude-module matplotlib --exclude-module pytest --exclude-module IPython `
  --exclude-module tkinter.test --exclude-module unittest.test `
  main.py
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller could not build the Windows executable.' }

$Executable = Join-Path $OutputDir 'NemesisScanner.exe'
$SizeMiB = [math]::Round((Get-Item $Executable).Length / 1MB, 1)
Write-Host "EXE: $Executable ($SizeMiB MiB)"


# Publish a convenient portable bundle with usage and dependency notes beside the executable.
$Stage = Join-Path $PSScriptRoot 'build\windows-package'
Remove-Item $Stage -Recurse -Force -ErrorAction SilentlyContinue
New-Item $Stage -ItemType Directory -Force | Out-Null
Copy-Item $Executable $Stage
Copy-Item (Join-Path $PSScriptRoot 'README.md') $Stage
Copy-Item (Join-Path $PSScriptRoot 'MANUAL.md') $Stage
$Bundle = Join-Path $OutputDir "NemesisScanner-$Version-windows-x64.zip"
Remove-Item $Bundle -Force -ErrorAction SilentlyContinue
Compress-Archive -Path (Join-Path $Stage '*') -DestinationPath $Bundle -CompressionLevel Optimal
Write-Host "Bundle: $Bundle"
