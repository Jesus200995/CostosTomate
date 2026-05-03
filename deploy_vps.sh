#!/bin/bash
# =============================================================
# DEPLOY COMPLETO: CostosTomate en VPS
# Ejecutar en el VPS como root:
#   curl -fsSL https://raw.githubusercontent.com/Jesus200995/CostosTomate/main/deploy_vps.sh | bash
# O si ya tienes el archivo:
#   bash /root/deploy_vps.sh
# =============================================================

set -e

REPO_URL="https://github.com/Jesus200995/CostosTomate.git"
APP_DIR="/var/www/CostosTomate"
DOMAIN="monitoreo.geodatos.com.mx"
BACKEND_PORT="3002"
DB_NAME="cosostomate"
DB_USER="jesus"
DB_PASS="2025"

echo "=============================================="
echo "  DEPLOY CostosTomate -> $DOMAIN"
echo "=============================================="

# ── 1. Dependencias del sistema ──────────────────
echo ""
echo ">>> [1/8] Instalando dependencias del sistema..."
apt-get update -qq
apt-get install -y -qq git curl nginx python3 python3-pip python3-venv nodejs npm certbot python3-certbot-nginx

# Instalar Node 18+ si la versión actual es vieja
NODE_VER=$(node -v 2>/dev/null | cut -d. -f1 | tr -d 'v' || echo "0")
if [ "$NODE_VER" -lt 18 ]; then
  echo ">>> Actualizando Node.js a v18..."
  curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
  apt-get install -y nodejs
fi

echo "Node: $(node -v) | npm: $(npm -v)"

# ── 2. Clonar / actualizar el repositorio ────────
echo ""
echo ">>> [2/8] Clonando/actualizando repositorio..."
if [ -d "$APP_DIR/.git" ]; then
  echo ">>> Repositorio ya existe, haciendo pull..."
  cd "$APP_DIR"
  git pull origin main
else
  echo ">>> Clonando repositorio..."
  git clone "$REPO_URL" "$APP_DIR"
  cd "$APP_DIR"
fi

# ── 3. Base de datos ──────────────────────────────
echo ""
echo ">>> [3/8] Configurando base de datos $DB_NAME..."
cd "$APP_DIR/backend"
bash init_vps.sh || echo ">>> init_vps.sh completado (puede haber advertencias normales)"

# ── 4. Backend Python ─────────────────────────────
echo ""
echo ">>> [4/8] Configurando backend Python..."
cd "$APP_DIR/backend"

# Crear/actualizar .env
cat > .env << ENVEOF
PORT=$BACKEND_PORT
JWT_SECRET=cosostomate_secret_j8t2m9k4n7r1w5p3
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME
ENVEOF
echo ">>> .env creado."

# Crear entorno virtual
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo ">>> venv creado."
fi

source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
deactivate

echo ">>> Dependencias Python instaladas."

# ── 5. Servicio systemd para el backend ──────────
echo ""
echo ">>> [5/8] Configurando servicio systemd..."
cat > /etc/systemd/system/cosostomate.service << SVCEOF
[Unit]
Description=CostosTomate Backend API
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR/backend
Environment="PATH=$APP_DIR/backend/venv/bin"
ExecStart=$APP_DIR/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port $BACKEND_PORT --workers 2
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable cosostomate
systemctl restart cosostomate
sleep 3

if systemctl is-active --quiet cosostomate; then
  echo ">>> Backend corriendo en puerto $BACKEND_PORT ✓"
else
  echo ">>> WARN: Backend no pudo arrancar. Ver: journalctl -u cosostomate -n 50"
fi

# ── 6. Frontend Vue ───────────────────────────────
echo ""
echo ">>> [6/8] Construyendo frontend Vue..."
cd "$APP_DIR/pwacostos"
npm install --silent
npm run build
echo ">>> Frontend construido en dist/ ✓"

# ── 7. Nginx ──────────────────────────────────────
echo ""
echo ">>> [7/8] Configurando Nginx..."
cat > /etc/nginx/sites-available/cosostomate << NGXEOF
server {
    listen 80;
    server_name $DOMAIN;

    root $APP_DIR/pwacostos/dist;
    index index.html;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml;

    # API -> backend
    location /api {
        proxy_pass http://127.0.0.1:$BACKEND_PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_read_timeout 60s;
    }

    # SPA fallback
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Cache para assets estáticos
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGXEOF

# Activar site
ln -sf /etc/nginx/sites-available/cosostomate /etc/nginx/sites-enabled/cosostomate

# Deshabilitar default si existe
if [ -f /etc/nginx/sites-enabled/default ]; then
  rm -f /etc/nginx/sites-enabled/default
fi

nginx -t && systemctl reload nginx
echo ">>> Nginx configurado ✓"

# ── 8. SSL con Certbot ────────────────────────────
echo ""
echo ">>> [8/8] Instalando certificado SSL..."
certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email jesusgomezmarcas@gmail.com --redirect

echo ""
echo "=============================================="
echo "  DEPLOY COMPLETADO"
echo "=============================================="
echo ""
echo "  URL:     https://$DOMAIN"
echo "  API:     https://$DOMAIN/api/docs"
echo "  Backend: systemctl status cosostomate"
echo "  Logs:    journalctl -u cosostomate -f"
echo ""
echo "Para actualizar en el futuro:"
echo "  cd $APP_DIR && git pull && cd pwacostos && npm run build && systemctl restart cosostomate"
echo ""
