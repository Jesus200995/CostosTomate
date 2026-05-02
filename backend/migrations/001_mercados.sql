-- Categorias
CREATE TABLE IF NOT EXISTS categorias (
    id VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT
);

-- Subcategorias
CREATE TABLE IF NOT EXISTS subcategorias (
    id VARCHAR(30) PRIMARY KEY,
    categoria_id VARCHAR(20) NOT NULL REFERENCES categorias(id),
    nombre VARCHAR(100) NOT NULL
);

-- Productos
CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    subcategoria_id VARCHAR(30) NOT NULL REFERENCES subcategorias(id),
    nombre VARCHAR(100) NOT NULL,
    UNIQUE(subcategoria_id, nombre)
);

-- Unidades por subcategoria
CREATE TABLE IF NOT EXISTS unidades_subcategoria (
    id SERIAL PRIMARY KEY,
    subcategoria_id VARCHAR(30) NOT NULL REFERENCES subcategorias(id),
    nombre VARCHAR(50) NOT NULL,
    UNIQUE(subcategoria_id, nombre)
);

-- Mercados del usuario
CREATE TABLE IF NOT EXISTS mercados (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Reportes de precios
CREATE TABLE IF NOT EXISTS reportes_precios (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    mercado_id INT NOT NULL REFERENCES mercados(id),
    tipo_precio VARCHAR(20) NOT NULL CHECK (tipo_precio IN ('MENUDEO','MAYOREO')),
    fecha DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Detalle de precios
CREATE TABLE IF NOT EXISTS detalle_precios (
    id SERIAL PRIMARY KEY,
    reporte_id INT NOT NULL REFERENCES reportes_precios(id) ON DELETE CASCADE,
    producto_id INT NOT NULL REFERENCES productos(id),
    precio DECIMAL(10,2) NOT NULL CHECK (precio > 0),
    unidad VARCHAR(50) NOT NULL,
    UNIQUE(reporte_id, producto_id, unidad)
);

-- SEED: Categorias
INSERT INTO categorias (id, nombre, descripcion) VALUES
('AGRICOLA', 'Agrícola', 'Cultivos agrícolas'),
('PECUARIO', 'Pecuario', 'Bovinos, porcinos, aves y huevo')
ON CONFLICT DO NOTHING;

-- SEED: Subcategorias
INSERT INTO subcategorias (id, categoria_id, nombre) VALUES
('AGR_GRANOS_BASICOS', 'AGRICOLA', 'Granos básicos'),
('AGR_LEGUMINOSAS', 'AGRICOLA', 'Leguminosas'),
('AGR_OLEAG_SEMILLAS', 'AGRICOLA', 'Oleaginosas y semillas'),
('AGR_HORTALIZAS', 'AGRICOLA', 'Hortalizas'),
('AGR_TUBERCULOS', 'AGRICOLA', 'Tubérculos y raíces'),
('AGR_FRUTAS', 'AGRICOLA', 'Frutas'),
('AGR_FORRAJES', 'AGRICOLA', 'Forrajes'),
('AGR_INDUSTRIALES', 'AGRICOLA', 'Industriales'),
('PEC_BOV', 'PECUARIO', 'Bovinos'),
('PEC_POR', 'PECUARIO', 'Porcinos'),
('PEC_AVE', 'PECUARIO', 'Aves'),
('PEC_HUE', 'PECUARIO', 'Huevo')
ON CONFLICT DO NOTHING;

-- SEED: Productos
INSERT INTO productos (subcategoria_id, nombre) VALUES
('AGR_GRANOS_BASICOS', 'Maíz'),
('AGR_GRANOS_BASICOS', 'Arroz'),
('AGR_GRANOS_BASICOS', 'Trigo'),
('AGR_GRANOS_BASICOS', 'Avena'),
('AGR_GRANOS_BASICOS', 'Cebada'),
('AGR_GRANOS_BASICOS', 'Sorgo'),
('AGR_LEGUMINOSAS', 'Frijol'),
('AGR_LEGUMINOSAS', 'Garbanzo'),
('AGR_LEGUMINOSAS', 'Lenteja'),
('AGR_LEGUMINOSAS', 'Haba'),
('AGR_OLEAG_SEMILLAS', 'Soya'),
('AGR_OLEAG_SEMILLAS', 'Cacahuate'),
('AGR_OLEAG_SEMILLAS', 'Ajonjolí'),
('AGR_OLEAG_SEMILLAS', 'Chía'),
('AGR_OLEAG_SEMILLAS', 'Amaranto'),
('AGR_HORTALIZAS', 'Jitomate'),
('AGR_HORTALIZAS', 'Tomate'),
('AGR_HORTALIZAS', 'Chile'),
('AGR_HORTALIZAS', 'Cebolla'),
('AGR_HORTALIZAS', 'Lechuga'),
('AGR_HORTALIZAS', 'Pepino'),
('AGR_HORTALIZAS', 'Calabaza'),
('AGR_HORTALIZAS', 'Zanahoria'),
('AGR_TUBERCULOS', 'Papa'),
('AGR_FRUTAS', 'Plátano'),
('AGR_FRUTAS', 'Fresa'),
('AGR_FRUTAS', 'Melón'),
('AGR_FRUTAS', 'Sandía'),
('AGR_FORRAJES', 'Alfalfa'),
('AGR_INDUSTRIALES', 'Caña de azúcar'),
('PEC_BOV', 'Bovino en pie'),
('PEC_BOV', 'Bovino en canal'),
('PEC_POR', 'Porcino en pie'),
('PEC_POR', 'Porcino en canal'),
('PEC_AVE', 'Pollo entero'),
('PEC_AVE', 'Pollo por pieza'),
('PEC_HUE', 'Huevo blanco'),
('PEC_HUE', 'Huevo rojo')
ON CONFLICT DO NOTHING;

-- SEED: Unidades por subcategoria
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('AGR_GRANOS_BASICOS', 'Kg'),
('AGR_GRANOS_BASICOS', 'Costal/Bulto'),
('AGR_GRANOS_BASICOS', 'Bolsa'),
('AGR_LEGUMINOSAS', 'Kg'),
('AGR_LEGUMINOSAS', 'Costal/Bulto'),
('AGR_LEGUMINOSAS', 'Bolsa'),
('AGR_OLEAG_SEMILLAS', 'Kg'),
('AGR_OLEAG_SEMILLAS', 'Bolsa'),
('AGR_HORTALIZAS', 'Kg'),
('AGR_HORTALIZAS', 'Pieza'),
('AGR_HORTALIZAS', 'Caja/Jaba'),
('AGR_HORTALIZAS', 'Bolsa'),
('AGR_TUBERCULOS', 'Kg'),
('AGR_TUBERCULOS', 'Costal/Bulto'),
('AGR_FRUTAS', 'Kg'),
('AGR_FRUTAS', 'Pieza'),
('AGR_FRUTAS', 'Caja/Jaba'),
('AGR_FORRAJES', 'Kg'),
('AGR_FORRAJES', 'Costal/Bulto'),
('AGR_INDUSTRIALES', 'Kg'),
('AGR_INDUSTRIALES', 'Costal/Bulto'),
('PEC_BOV', 'Kg'),
('PEC_POR', 'Kg'),
('PEC_AVE', 'Kg'),
('PEC_AVE', 'Pieza'),
('PEC_HUE', 'Docena'),
('PEC_HUE', 'Charola')
ON CONFLICT DO NOTHING;
