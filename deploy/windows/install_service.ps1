param(
  [string]$ProjectRoot = "D:\Repos\Python\tanker",
  [string]$ServiceName = "TankerApi",
  [string]$NssmPath = "C:\tools\nssm\win64\nssm.exe",
  [string]$PythonExe = "C:\Python312\python.exe"
)

if (-not (Test-Path $NssmPath)) {
  throw "nssm.exe not found at $NssmPath"
}
if (-not (Test-Path $ProjectRoot)) {
  throw "Project root not found: $ProjectRoot"
}

$venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
  & $PythonExe -m venv (Join-Path $ProjectRoot ".venv")
}

& $venvPython -m pip install --upgrade pip setuptools wheel
& $venvPython -m pip install -e $ProjectRoot

Push-Location $ProjectRoot
try {
  & $venvPython -m alembic upgrade head
  & $venvPython -m app.scripts.seed_base
}
finally {
  Pop-Location
}

$runner = Join-Path $ProjectRoot "deploy\windows\run_tanker.ps1"
$ps = "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe"
$envPath = Join-Path $ProjectRoot ".env"
$args = '-NoProfile -ExecutionPolicy Bypass -File "{0}" -ProjectRoot "{1}" -EnvFile "{2}"' -f $runner, $ProjectRoot, $envPath

& $NssmPath remove $ServiceName confirm | Out-Null
& $NssmPath install $ServiceName $ps $args
& $NssmPath set $ServiceName AppDirectory $ProjectRoot
& $NssmPath set $ServiceName Start SERVICE_AUTO_START
& $NssmPath set $ServiceName AppStdout (Join-Path $ProjectRoot "logs\service-out.log")
& $NssmPath set $ServiceName AppStderr (Join-Path $ProjectRoot "logs\service-err.log")

New-Item -ItemType Directory -Path (Join-Path $ProjectRoot "logs") -Force | Out-Null
Start-Service $ServiceName
Write-Host "Service installed and started: $ServiceName"
