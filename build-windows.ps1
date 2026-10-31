$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

python -m pip install --upgrade -r requirements.txt pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed `
  --name NemesisScanner --distpath dist/windows `
  --add-data 'Logo.png;.' --collect-data core `
  --hidden-import nmap --hidden-import requests --hidden-import PIL `
  main.py

Write-Host "EXE: $PSScriptRoot\dist\windows\NemesisScanner.exe"
