# Deployment Runbooks

This folder contains ready-to-run deployment assets for both Linux and Windows.

## 1. Linux (Recommended)

### Files
- `deploy/linux/install_server.sh`
- `deploy/linux/deploy_release.sh`
- `deploy/linux/tanker.service`
- `deploy/linux/nginx.tanker.conf`

### First-time server setup (root)
```bash
cd /opt
# copy repo or pull it, then:
bash /opt/tanker/current/deploy/linux/install_server.sh
```

### Configure environment
Edit `/etc/tanker.env`:
- `DATABASE_URL`
- `SECRET_KEY`
- `INITIAL_SUPERADMIN_EMAIL`
- `INITIAL_SUPERADMIN_PASSWORD`
- `SITE_NAME`

### Deploy or update release
```bash
sudo bash /opt/tanker/current/deploy/linux/deploy_release.sh <repo_url> <branch>
```
Example:
```bash
sudo bash /opt/tanker/current/deploy/linux/deploy_release.sh https://github.com/your-org/tanker.git master
```

### TLS (Let's Encrypt)
After DNS points to server and nginx site is loaded:
```bash
sudo certbot --nginx -d tanker.example.com
```

### Verify
```bash
systemctl status tanker
curl -f http://127.0.0.1:8000/healthz
curl -f https://tanker.example.com/healthz
```

## 2. Windows + IIS

### Files
- `deploy/windows/install_service.ps1`
- `deploy/windows/uninstall_service.ps1`
- `deploy/windows/run_tanker.ps1`
- `deploy/windows/configure_iis.ps1`
- `deploy/windows/web.config`

### Prerequisites
- Python 3.12 installed
- IIS installed
- IIS URL Rewrite module installed
- IIS ARR installed
- NSSM downloaded (set path in script args)

### Install and start app service (elevated PowerShell)
```powershell
cd D:\Repos\Python\tanker
.\deploy\windows\install_service.ps1 -ProjectRoot "D:\Repos\Python\tanker" -NssmPath "C:\tools\nssm\win64\nssm.exe"
```

### Configure IIS reverse proxy (elevated PowerShell)
```powershell
cd D:\Repos\Python\tanker
.\deploy\windows\configure_iis.ps1 -SiteName "Tanker" -HostHeader "tanker.local"
```

### Verify
```powershell
Get-Service TankerApi
Invoke-WebRequest http://127.0.0.1:8000/healthz
Invoke-WebRequest http://tanker.local/healthz
```

### Remove service (if needed)
```powershell
.\deploy\windows\uninstall_service.ps1 -ServiceName "TankerApi" -NssmPath "C:\tools\nssm\win64\nssm.exe"
```

## Notes
- Keep `.env` out of git.
- Run `alembic upgrade head` and `tanker-seed-base` for each environment.
- For production, use a strong `SECRET_KEY` and TLS on the reverse proxy.
