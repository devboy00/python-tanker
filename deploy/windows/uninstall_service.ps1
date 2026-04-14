param(
  [string]$ServiceName = "TankerApi",
  [string]$NssmPath = "C:\tools\nssm\win64\nssm.exe"
)

if (-not (Test-Path $NssmPath)) {
  throw "nssm.exe not found at $NssmPath"
}

$svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($svc) {
  if ($svc.Status -ne 'Stopped') {
    Stop-Service -Name $ServiceName -Force
  }
  & $NssmPath remove $ServiceName confirm
  Write-Host "Service removed: $ServiceName"
} else {
  Write-Host "Service not found: $ServiceName"
}
