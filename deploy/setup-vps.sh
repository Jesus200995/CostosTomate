#!/bin/bash
set -e

# ================================================
# COSTOS - Setup inicial del VPS
# Ejecutar UNA SOLA VEZ en el servidor
# ================================================

echo "🔧 Configurando VPS para COSTOS..."

# Actualizar sistema
apt update && apt upgrade -y

# Instalar Node.js 20 LTS
if ! command -v node &> /dev/null; then
    echo "📦 Instalando Node.js 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi

# Instalar build tools para módulos nativos (better-sqlite3)
apt install -y build-essential python3 git nginx certbot python3-certbot-nginx

# Instalar PM2 globalmente
if ! command -v pm2 &> /dev/null; then
    echo "📦 Instalando PM2..."
    npm install -g pm2
fi

# Crear directorio de logs
mkdir -p /var/log/costos

# Clonar repositorio si no existe
if [ ! -d /var/www/costos ]; then
    echo "📥 Clonando repositorio..."
    cd /var/www
    git clone https://github.com/Jesus200995/costos.git
fi

cd /var/www/costos

# Configurar nginx
echo "🌐 Configurando Nginx..."
cp deploy/nginx-costos.conf /etc/nginx/sites-available/costos
ln -sf /etc/nginx/sites-available/costos /etc/nginx/sites-enabled/costos

# Remover default si existe
rm -f /etc/nginx/sites-enabled/default

# Validar configuración nginx
nginx -t

# Ejecutar el deploy
echo "🚀 Ejecutando primer despliegue..."
chmod +x deploy/deploy.sh
bash deploy/deploy.sh

# Reiniciar nginx
systemctl restart nginx
systemctl enable nginx

# Configurar PM2 para iniciar al boot
pm2 startup systemd -u root --hp /root
pm2 save

# SSL con Let's Encrypt
echo ""
echo "🔒 Configurando SSL..."
certbot --nginx -d costos.sembrandodatos.com --non-interactive --agree-tos -m admin@sembrandodatos.com || echo "⚠️  SSL falló - asegúrate que el DNS apunte a este servidor"

echo ""
echo "============================================"
echo "✅ Setup completado!"
echo "🌐 https://costos.sembrandodatos.com"
echo "============================================"
echo ""
echo "Para futuros despliegues, ejecuta:"
echo "  cd /var/www/costos && git pull && bash deploy/deploy.sh"
echo ""
