#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Run as root."
  exit 1
fi

APP_USER="tanker"
APP_GROUP="www-data"
APP_ROOT="/opt/tanker"
ENV_FILE="/etc/tanker.env"

apt-get update
apt-get install -y python3.12 python3.12-venv python3-pip nginx git certbot python3-certbot-nginx

id -u "$APP_USER" >/dev/null 2>&1 || useradd -m -s /bin/bash "$APP_USER"
mkdir -p "$APP_ROOT"
chown -R "$APP_USER":"$APP_GROUP" "$APP_ROOT"
chmod 750 "$APP_ROOT"

if [[ ! -f "$ENV_FILE" ]]; then
  cat > "$ENV_FILE" <<'EOF'
APP_ENV=production
DATABASE_URL=postgresql+psycopg://postgres:CHANGE_ME@127.0.0.1:5432/tanker
SECRET_KEY=CHANGE_ME_LONG_RANDOM_VALUE
ACCESS_TOKEN_EXPIRE_MINUTES=60
INITIAL_SUPERADMIN_EMAIL=admin@example.com
INITIAL_SUPERADMIN_PASSWORD=CHANGE_ME_SUPERADMIN_PASSWORD
SITE_NAME=Tanker
EOF
  chmod 600 "$ENV_FILE"
  echo "Created $ENV_FILE. Update it before first deploy."
fi

echo "Server prerequisites installed."
