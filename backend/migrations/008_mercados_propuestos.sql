-- Migration 008: Tabla de mercados propuestos por capturistas
-- Los mercados propuestos quedan pendientes de autorización del admin

CREATE TABLE IF NOT EXISTS mercados_propuestos (
    id SERIAL PRIMARY KEY,
    nombre_mercado VARCHAR(200) NOT NULL,
    tipo_mercado VARCHAR(50) NOT NULL CHECK (tipo_mercado IN ('MERCADO_PUBLICO','TIANGUIS','CENTRAL_ABASTO','OTRO')),
    tipo_mercado_otro VARCHAR(100),
    estado VARCHAR(100) NOT NULL,
    municipio VARCHAR(100) NOT NULL,
    localidad_colonia VARCHAR(200),
    latitud DOUBLE PRECISION NOT NULL,
    longitud DOUBLE PRECISION NOT NULL,
    dias_operacion TEXT[] NOT NULL DEFAULT '{}',
    horario VARCHAR(100),
    referencia TEXT,
    observaciones TEXT,
    foto_url TEXT,
    status VARCHAR(40) NOT NULL DEFAULT 'pendiente_autorizacion'
        CHECK (status IN ('pendiente_autorizacion','autorizado','rechazado')),
    created_by UUID NOT NULL REFERENCES users(id),
    tipo_capturista VARCHAR(50),
    cac_id VARCHAR(50),
    cac_nombre VARCHAR(200),
    territorio VARCHAR(100),
    ruta VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mercados_propuestos_status ON mercados_propuestos(status);
CREATE INDEX IF NOT EXISTS idx_mercados_propuestos_created_by ON mercados_propuestos(created_by);
CREATE INDEX IF NOT EXISTS idx_mercados_propuestos_estado ON mercados_propuestos(estado);
