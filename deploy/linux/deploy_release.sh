#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <repo_url> [branch]"
  exit 1
fi

REPO_URL="$1"
BRANCH="${2:-master}"
APP_USER="tanker"
APP_GROUP="www-data"
APP_ROOT="/opt/tanker"
CURRENT_DIR="$APP_ROOT/current"
SERVICE_FILE_SRC="./deploy/linux/tanker.service"
SERVICE_FILE_DST="/etc/systemd/system/tanker.service"
NGINX_FILE_SRC="./deploy/linux/nginx.tanker.conf"
NGINX_FILE_DST="/etc/nginx/sites-available/tanker"

mkdir -p "$APP_ROOT"

if [[ ! -d "$CURRENT_DIR/.git" ]]; then
  git clone --branch "$BRANCH" "$REPO_URL" "$CURRENT_DIR"
else
  git -C "$CURRENT_DIR" fetch origin
  git -C "$CURRENT_DIR" checkout "$BRANCH"
  git -C "$CURRENT_DIR" pull --ff-only origin "$BRANCH"
fi

cd "$CURRENT_DIR"

python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip setuptools wheel
.venv/bin/python -m pip install -e .

.venv/bin/alembic upgrade head
.venv/bin/tanker-seed-base

cp "$SERVICE_FILE_SRC" "$SERVICE_FILE_DST"
systemctl daemon-reload
systemctl enable tanker
systemctl restart tanker

cp "$NGINX_FILE_SRC" "$NGINX_FILE_DST"
ln -sf "$NGINX_FILE_DST" /etc/nginx/sites-enabled/tanker
nginx -t
systemctl reload nginx

chown -R "$APP_USER":"$APP_GROUP" "$APP_ROOT"

echo "Deploy complete."
