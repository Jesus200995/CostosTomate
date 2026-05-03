-- =============================================================
-- SETUP COMPLETO: Base de datos costostomate
-- Sistema especializado en monitoreo de jitomate Saladette/huaje
-- =============================================================
-- Ejecutar como usuario jesus:
--   psql -U jesus -d costostomate -f setup_costostomate.sql
-- Crear la BD primero (conectado a postgres como jesus):
--   createdb -U jesus cosostomate  ← nombre correcto: cosostomate
--   psql -h 31.97.8.51 -U jesus -c "CREATE DATABASE cosostomate;"
-- O directamente:
--   psql -h 31.97.8.51 -U jesus -d cosostomate -f setup_cosostomate.sql
-- =============================================================

-- Extensión para UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ───────────────────────────────────────────────────────────────
-- 1. TABLA USERS (capturistas)
-- ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    avatar VARCHAR(500),
    curp VARCHAR(18) UNIQUE,
    tipo_capturista VARCHAR(50) DEFAULT 'CAPTURISTA',
    estado VARCHAR(100),
    municipio INTEGER,
    localidad VARCHAR(200),
    telefono VARCHAR(15),
    consent BOOLEAN DEFAULT FALSE,
    cac_id VARCHAR(50),
    cac_nombre VARCHAR(200),
    territorio VARCHAR(100),
    ruta VARCHAR(100),
    rol_comision VARCHAR(100),
    correo_institucional VARCHAR(200),
    rol_interno VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ───────────────────────────────────────────────────────────────
-- 2. TABLA USUARIOS ADMIN
-- ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS usersadmin (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(200) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(200),
    rol VARCHAR(50) DEFAULT 'ADMIN',
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Admin por defecto (password: admin2025)
INSERT INTO usersadmin (username, email, password, nombre, rol)
VALUES ('admin', 'admin@costostomate.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewxTcf.BaKCNrFwq', 'Administrador', 'SUPERADMIN')
ON CONFLICT (username) DO NOTHING;

-- ───────────────────────────────────────────────────────────────
-- 3. DATOS GEOGRÁFICOS: ESTADOS
-- ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS estados (
    cve_ent VARCHAR(5) PRIMARY KEY,
    nom_ent VARCHAR(100) NOT NULL
);

INSERT INTO estados (cve_ent, nom_ent) VALUES
('01', 'Aguascalientes'), ('02', 'Baja California'), ('03', 'Baja California Sur'),
('04', 'Campeche'), ('05', 'Coahuila de Zaragoza'), ('06', 'Colima'),
('07', 'Chiapas'), ('08', 'Chihuahua'), ('09', 'Ciudad de México'),
('10', 'Durango'), ('11', 'Guanajuato'), ('12', 'Guerrero'),
('13', 'Hidalgo'), ('14', 'Jalisco'), ('15', 'México'),
('16', 'Michoacán de Ocampo'), ('17', 'Morelos'), ('18', 'Nayarit'),
('19', 'Nuevo León'), ('20', 'Oaxaca'), ('21', 'Puebla'),
('22', 'Querétaro'), ('23', 'Quintana Roo'), ('24', 'San Luis Potosí'),
('25', 'Sinaloa'), ('26', 'Sonora'), ('27', 'Tabasco'),
('28', 'Tamaulipas'), ('29', 'Tlaxcala'), ('30', 'Veracruz de Ignacio de la Llave'),
('31', 'Yucatán'), ('32', 'Zacatecas')
ON CONFLICT (cve_ent) DO NOTHING;

-- ───────────────────────────────────────────────────────────────
-- 4. DATOS GEOGRÁFICOS: MUNICIPIOS
-- ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS municipios (
    clave_mun INTEGER PRIMARY KEY,
    nomgeo VARCHAR(200) NOT NULL,
    cve_ent VARCHAR(5) REFERENCES estados(cve_ent),
    territorio VARCHAR(100)
);

-- NOTA: Importar municipios desde la base costos existente:
-- pg_dump -U jesus -d costos -t municipios --data-only | psql -U jesus -d costostomate

-- ───────────────────────────────────────────────────────────────
-- 5. CATÁLOGO DE CENTRALES DE ABASTO
-- ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS catalogo_centrales (
    id SERIAL PRIMARY KEY,
    nombre_central VARCHAR(255) NOT NULL,
    tipo VARCHAR(100),
    municipio VARCHAR(100),
    estado VARCHAR(100),
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    estatus VARCHAR(50) DEFAULT 'pendiente' CHECK (estatus IN ('autorizado', 'pendiente', 'inactivo')),
    visible_pwa BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_catalogo_centrales_estatus ON catalogo_centrales(estatus);
CREATE INDEX IF NOT EXISTS idx_catalogo_centrales_visible ON catalogo_centrales(visible_pwa);

-- Centrales de ejemplo (para desarrollo)
INSERT INTO catalogo_centrales (nombre_central, tipo, municipio, estado, latitud, longitud, estatus, visible_pwa) VALUES
('Central de Abasto CDMX', 'Central de Abasto', 'Iztapalapa', 'Ciudad de México', 19.3847, -99.0669, 'autorizado', true),
('Central de Abasto Guadalajara', 'Central de Abasto', 'Guadalajara', 'Jalisco', 20.6597, -103.3496, 'autorizado', true),
('Central de Abasto Monterrey', 'Central de Abasto', 'Monterrey', 'Nuevo León', 25.6714, -100.3097, 'autorizado', true),
('Mercado Mayorista Puebla', 'Mercado Mayorista', 'Puebla', 'Puebla', 19.0414, -98.2063, 'autorizado', true),
('Central de Abasto Querétaro', 'Central de Abasto', 'Querétaro', 'Querétaro', 20.5888, -100.3899, 'autorizado', true)
ON CONFLICT DO NOTHING;

-- ───────────────────────────────────────────────────────────────
-- 6. MIS CENTRALES (relación capturista-central)
-- ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS capturista_centrales (
    id SERIAL PRIMARY KEY,
    usuario_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    central_id INTEGER NOT NULL REFERENCES catalogo_centrales(id) ON DELETE CASCADE,
    es_favorita BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_id, central_id)
);

CREATE INDEX IF NOT EXISTS idx_capturista_centrales_usuario ON capturista_centrales(usuario_id);
CREATE INDEX IF NOT EXISTS idx_capturista_centrales_central ON capturista_centrales(central_id);

-- ───────────────────────────────────────────────────────────────
-- 7. PROPUESTAS DE NUEVAS CENTRALES
-- ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS propuestas_centrales (
    id SERIAL PRIMARY KEY,
    usuario_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    nombre_central VARCHAR(255) NOT NULL,
    tipo VARCHAR(100),
    municipio VARCHAR(100),
    estado VARCHAR(100),
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    estatus VARCHAR(50) DEFAULT 'pendiente' CHECK (estatus IN ('pendiente', 'aprobada', 'rechazada')),
    motivo_rechazo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_propuestas_centrales_usuario ON propuestas_centrales(usuario_id);
CREATE INDEX IF NOT EXISTS idx_propuestas_centrales_estatus ON propuestas_centrales(estatus);

-- ───────────────────────────────────────────────────────────────
-- 8. REPORTES JITOMATE (cabecera)
-- ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reportes_jitomate (
    id SERIAL PRIMARY KEY,
    central_id INTEGER NOT NULL REFERENCES catalogo_centrales(id) ON DELETE CASCADE,
    usuario_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    corte VARCHAR(20) NOT NULL CHECK (corte IN ('matutino', 'mediodia')),
    hora_captura TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    captura_tardia BOOLEAN DEFAULT FALSE,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(central_id, fecha, corte)
);

CREATE INDEX IF NOT EXISTS idx_reportes_jitomate_central ON reportes_jitomate(central_id);
CREATE INDEX IF NOT EXISTS idx_reportes_jitomate_usuario ON reportes_jitomate(usuario_id);
CREATE INDEX IF NOT EXISTS idx_reportes_jitomate_fecha ON reportes_jitomate(fecha);
CREATE INDEX IF NOT EXISTS idx_reportes_jitomate_corte ON reportes_jitomate(corte);

-- ───────────────────────────────────────────────────────────────
-- 9. PRECIOS JITOMATE POR CALIDAD (detalle)
-- ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS precios_jitomate_calidad (
    id SERIAL PRIMARY KEY,
    reporte_jitomate_id INTEGER NOT NULL REFERENCES reportes_jitomate(id) ON DELETE CASCADE,
    calidad VARCHAR(20) NOT NULL CHECK (calidad IN ('primera', 'segunda', 'tercera')),
    precio DECIMAL(10, 2),
    sin_dato BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(reporte_jitomate_id, calidad)
);

CREATE INDEX IF NOT EXISTS idx_precios_jitomate_reporte ON precios_jitomate_calidad(reporte_jitomate_id);
CREATE INDEX IF NOT EXISTS idx_precios_jitomate_calidad ON precios_jitomate_calidad(calidad);

-- ───────────────────────────────────────────────────────────────
-- 10. ALERTAS JITOMATE
-- ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS alertas_jitomate (
    id SERIAL PRIMARY KEY,
    central_id INTEGER NOT NULL REFERENCES catalogo_centrales(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL,
    descripcion TEXT,
    fecha_alerta DATE,
    corte VARCHAR(20),
    calidad VARCHAR(20),
    precio_anterior DECIMAL(10, 2),
    precio_actual DECIMAL(10, 2),
    variacion_porcentaje DECIMAL(5, 2),
    estatus VARCHAR(50) DEFAULT 'activa' CHECK (estatus IN ('activa', 'resuelta')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alertas_jitomate_central ON alertas_jitomate(central_id);
CREATE INDEX IF NOT EXISTS idx_alertas_jitomate_tipo ON alertas_jitomate(tipo);
CREATE INDEX IF NOT EXISTS idx_alertas_jitomate_estatus ON alertas_jitomate(estatus);

-- ───────────────────────────────────────────────────────────────
-- COMENTARIOS
-- ───────────────────────────────────────────────────────────────
COMMENT ON TABLE reportes_jitomate IS 'CRÍTICO: UNIQUE(central_id, fecha, corte) previene duplicados';
COMMENT ON TABLE precios_jitomate_calidad IS 'primera, segunda, tercera. sin_dato=true cuando no hay dato';
COMMENT ON TABLE catalogo_centrales IS 'visible_pwa=true + estatus=autorizado para mostrar en PWA';
COMMENT ON TABLE users IS 'tipo_capturista siempre CAPTURISTA en cosostomate';

-- FIN DEL SCRIPT
SELECT 'cosostomate configurado correctamente.' AS resultado;
