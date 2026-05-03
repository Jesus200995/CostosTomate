-- Migración 009: Tablas para sistema de monitoreo de jitomate
-- Fecha: 2026-05-02

-- 1. Tabla de centrales de abasto autorizadas
CREATE TABLE catalogo_centrales (
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

CREATE INDEX idx_catalogo_centrales_estatus ON catalogo_centrales(estatus);
CREATE INDEX idx_catalogo_centrales_visible ON catalogo_centrales(visible_pwa);

-- 2. Tabla de relación usuario-centrales (Mis Centrales)
CREATE TABLE capturista_centrales (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    central_id INTEGER NOT NULL REFERENCES catalogo_centrales(id) ON DELETE CASCADE,
    es_favorita BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_id, central_id)
);

CREATE INDEX idx_capturista_centrales_usuario ON capturista_centrales(usuario_id);
CREATE INDEX idx_capturista_centrales_central ON capturista_centrales(central_id);

-- 3. Tabla de propuestas de nuevas centrales
CREATE TABLE propuestas_centrales (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
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

CREATE INDEX idx_propuestas_centrales_usuario ON propuestas_centrales(usuario_id);
CREATE INDEX idx_propuestas_centrales_estatus ON propuestas_centrales(estatus);

-- 4. Tabla cabecera de reportes de jitomate (CRÍTICA: UNIQUE en central, fecha, corte)
CREATE TABLE reportes_jitomate (
    id SERIAL PRIMARY KEY,
    central_id INTEGER NOT NULL REFERENCES catalogo_centrales(id) ON DELETE CASCADE,
    usuario_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    corte VARCHAR(20) NOT NULL CHECK (corte IN ('matutino', 'mediodía')),
    hora_captura TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    captura_tardia BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(central_id, fecha, corte)
);

CREATE INDEX idx_reportes_jitomate_central ON reportes_jitomate(central_id);
CREATE INDEX idx_reportes_jitomate_usuario ON reportes_jitomate(usuario_id);
CREATE INDEX idx_reportes_jitomate_fecha ON reportes_jitomate(fecha);
CREATE INDEX idx_reportes_jitomate_corte ON reportes_jitomate(corte);

-- 5. Tabla detalle de precios por calidad
CREATE TABLE precios_jitomate_calidad (
    id SERIAL PRIMARY KEY,
    reporte_jitomate_id INTEGER NOT NULL REFERENCES reportes_jitomate(id) ON DELETE CASCADE,
    calidad VARCHAR(20) NOT NULL CHECK (calidad IN ('primera', 'segunda', 'tercera')),
    precio DECIMAL(10, 2),
    sin_dato BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(reporte_jitomate_id, calidad)
);

CREATE INDEX idx_precios_jitomate_reporte ON precios_jitomate_calidad(reporte_jitomate_id);
CREATE INDEX idx_precios_jitomate_calidad ON precios_jitomate_calidad(calidad);

-- 6. Tabla de alertas generadas
CREATE TABLE alertas_jitomate (
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

CREATE INDEX idx_alertas_jitomate_central ON alertas_jitomate(central_id);
CREATE INDEX idx_alertas_jitomate_tipo ON alertas_jitomate(tipo);
CREATE INDEX idx_alertas_jitomate_estatus ON alertas_jitomate(estatus);

-- Comentarios
COMMENT ON TABLE reportes_jitomate IS 'CRÍTICO: Constraint UNIQUE(central_id, fecha, corte) previene duplicados';
COMMENT ON TABLE precios_jitomate_calidad IS 'Detalle de precios: primera, segunda, tercera. Sin_dato=true cuando no hay información';
COMMENT ON TABLE catalogo_centrales IS 'Catálogo de centrales autorizadas. visible_pwa=true para mostrar en PWA';
