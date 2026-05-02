#!/bin/bash
set -e

# ================================================
# COSTOS - Script de despliegue automático
# Se ejecuta cada vez que se hace git pull
# ================================================

APP_DIR="/var/www/costos"
LOG_DIR="/var/log/costos"

echo "🚀 Desplegando COSTOS..."
echo "📅 $(date)"

cd "$APP_DIR"

# Instalar dependencias del backend (FastAPI)
echo "📦 Instalando dependencias del backend..."
cd "$APP_DIR/backend"
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -r requirements.txt --quiet

# Copiar .env si no existe
if [ ! -f .env ]; then
    echo 'PORT=3001' > .env
    echo 'JWT_SECRET=costos_prod_secret_change_me' >> .env
    echo 'DATABASE_URL=postgresql://jesus:2025@localhost:5432/costos' >> .env
    echo "⚠️  Archivo .env creado - Revisa la configuración"
fi

# Instalar dependencias y construir frontend
echo "📦 Instalando dependencias del frontend..."
cd "$APP_DIR/pwacostos"
npm ci 2>/dev/null || npm install

echo "🔨 Construyendo frontend..."
npx vite build

# Reiniciar backend con PM2
echo "🔄 Reiniciando backend..."
cd "$APP_DIR"
pm2 startOrRestart deploy/ecosystem.config.cjs --update-env
pm2 save

echo "✅ Despliegue completado exitosamente!"
echo "🌐 https://costos.sembrandodatos.com"
