param(
  [string]$ProjectRoot = "D:\Repos\Python\tanker",
  [string]$EnvFile = "D:\Repos\Python\tanker\.env"
)

if (-not (Test-Path $ProjectRoot)) {
  throw "Project root not found: $ProjectRoot"
}
if (-not (Test-Path $EnvFile)) {
  throw "Env file not found: $EnvFile"
}

Get-Content $EnvFile | ForEach-Object {
  if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
  $parts = $_ -split '=', 2
  if ($parts.Count -eq 2) {
    $name = $parts[0].Trim()
    $value = $parts[1]
    [Environment]::SetEnvironmentVariable($name, $value, 'Process')
  }
}

$uvicorn = Join-Path $ProjectRoot ".venv\Scripts\uvicorn.exe"
if (-not (Test-Path $uvicorn)) {
  throw "Uvicorn not found: $uvicorn"
}

Push-Location $ProjectRoot
try {
  & $uvicorn "app.main:app" --host 127.0.0.1 --port 8000
}
finally {
  Pop-Location
}
