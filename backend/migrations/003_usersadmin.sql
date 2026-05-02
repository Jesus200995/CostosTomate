-- Tabla de usuarios administrativos
CREATE TABLE IF NOT EXISTS usersadmin (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100) NOT NULL,
    curp VARCHAR(18) NOT NULL UNIQUE,
    correo VARCHAR(150) NOT NULL UNIQUE,
    telefono VARCHAR(10) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'usuario' CHECK (rol IN ('usuario', 'administrador')),
    estatus VARCHAR(20) NOT NULL DEFAULT 'activo' CHECK (estatus IN ('activo', 'inactivo')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_usersadmin_curp ON usersadmin(curp);
CREATE INDEX IF NOT EXISTS idx_usersadmin_correo ON usersadmin(correo);
CREATE INDEX IF NOT EXISTS idx_usersadmin_rol ON usersadmin(rol);
CREATE INDEX IF NOT EXISTS idx_usersadmin_estatus ON usersadmin(estatus);

-- Insertar usuario administrador inicial
INSERT INTO usersadmin (nombre, apellido_paterno, apellido_materno, curp, correo, telefono, password_hash, rol, estatus)
VALUES (
    'ADMIN',
    'SISTEMA',
    'PRINCIPAL',
    'XEXX010101HNEXXXA4',
    'admin@costos.com',
    '0000000000',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4edV4R.wuK0m0KHi', -- password: Admin123!
    'administrador',
    'activo'
) ON CONFLICT (curp) DO NOTHING;
