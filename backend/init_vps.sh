#!/bin/bash
# =============================================================
# Script de inicializacion del VPS para costostomate
# Ejecutar en el VPS como root:
#   cd /ruta/al/proyecto/backend
#   bash init_vps.sh
# =============================================================

set -e

DB_USER="jesus"
DB_PASS="2025"
DB_NAME="costostomate"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ">>> Verificando base de datos $DB_NAME..."
DB_EXISTS=$(psql -U "$DB_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>/dev/null || echo "0")

if [ "$DB_EXISTS" = "1" ]; then
  echo ">>> La base $DB_NAME ya existe. Aplicando tablas nuevas..."
else
  echo ">>> Creando base de datos $DB_NAME..."
  createdb -U "$DB_USER" "$DB_NAME"
  echo ">>> Base creada."
fi

echo ">>> Aplicando setup_costostomate.sql..."
psql -U "$DB_USER" -d "$DB_NAME" -f "$SCRIPT_DIR/setup_costostomate.sql"

echo ""
echo "=== SETUP COMPLETADO ==="
echo "Base de datos : $DB_NAME"
echo "Usuario       : $DB_USER"
echo ""

echo ">>> Verificando municipios..."
MUNICIPIOS=$(psql -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM municipios" 2>/dev/null || echo "0")
if [ "$MUNICIPIOS" = "0" ]; then
  COSTOS_OK=$(psql -U "$DB_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='costos'" 2>/dev/null || echo "0")
  if [ "$COSTOS_OK" = "1" ]; then
    echo ">>> Copiando estados y municipios desde costos..."
    pg_dump -U "$DB_USER" -d costos -t estados --data-only 2>/dev/null | psql -U "$DB_USER" -d "$DB_NAME" 2>/dev/null || true
    pg_dump -U "$DB_USER" -d costos -t municipios --data-only 2>/dev/null | psql -U "$DB_USER" -d "$DB_NAME" 2>/dev/null || true
    echo ">>> Datos geograficos copiados."
  else
    echo ">>> BD costos no encontrada - municipios deberan importarse manualmente."
  fi
else
  echo ">>> Municipios ya cargados ($MUNICIPIOS registros)."
fi

echo ""
echo "=== TODO LISTO. El backend puede conectarse a $DB_NAME ==="
