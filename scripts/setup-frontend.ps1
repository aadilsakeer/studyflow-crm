# Globvio CRM — Frontend setup (Windows)
$ErrorActionPreference = "Stop"

Set-Location "$PSScriptRoot\..\frontend"

npm install
Write-Host "Frontend ready. Run: npm run dev"
