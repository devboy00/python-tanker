param(
  [string]$SiteName = "Tanker",
  [string]$AppPoolName = "TankerPool",
  [string]$PhysicalPath = "D:\Repos\Python\tanker\deploy\windows\site-root",
  [string]$HostHeader = "tanker.local"
)

Import-Module WebAdministration

# Requires IIS URL Rewrite + ARR installed.
Set-WebConfigurationProperty -pspath 'MACHINE/WEBROOT/APPHOST' -filter "system.webServer/proxy" -name "enabled" -value "True"

if (-not (Test-Path $PhysicalPath)) {
  New-Item -ItemType Directory -Path $PhysicalPath -Force | Out-Null
}

Copy-Item "D:\Repos\Python\tanker\deploy\windows\web.config" (Join-Path $PhysicalPath "web.config") -Force

if (-not (Test-Path "IIS:\AppPools\$AppPoolName")) {
  New-WebAppPool -Name $AppPoolName | Out-Null
}
Set-ItemProperty "IIS:\AppPools\$AppPoolName" -Name managedRuntimeVersion -Value ""
Set-ItemProperty "IIS:\AppPools\$AppPoolName" -Name processModel.identityType -Value 4

if (Get-Website -Name $SiteName -ErrorAction SilentlyContinue) {
  Remove-Website -Name $SiteName
}

New-Website -Name $SiteName -PhysicalPath $PhysicalPath -ApplicationPool $AppPoolName -Port 80 -HostHeader $HostHeader | Out-Null

Write-Host "IIS site configured: $SiteName"
Write-Host "Remember to map DNS/hosts for $HostHeader and bind TLS cert for production."
