# C0 Environment Seal — run at the start of every C1-C6 session
# Loads all tool cache redirects so nothing writes to C:
Get-Content D:\CRM\.env.local | ForEach-Object {
    if ($_ -match '^([^=]+)=(.+)$') {
        [System.Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], 'Process')
    }
}
Write-Host "Seal active. PLAYWRIGHT_BROWSERS_PATH=$env:PLAYWRIGHT_BROWSERS_PATH"
