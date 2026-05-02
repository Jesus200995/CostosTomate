-- ═══════════════════════════════════════════════════════════════════
-- 004: Diferenciar unidades por tipo_precio (MENUDEO / MAYOREO)
-- ═══════════════════════════════════════════════════════════════════

-- 1. Agregar columna tipo
ALTER TABLE unidades_subcategoria
  ADD COLUMN IF NOT EXISTS tipo VARCHAR(10) NOT NULL DEFAULT 'MENUDEO'
  CHECK (tipo IN ('MENUDEO','MAYOREO'));

-- 2. Eliminar constraint UNIQUE antigua y crear nueva que incluya tipo
ALTER TABLE unidades_subcategoria DROP CONSTRAINT IF EXISTS unidades_subcategoria_subcategoria_id_nombre_key;
ALTER TABLE unidades_subcategoria ADD CONSTRAINT unidades_subcategoria_sub_nombre_tipo_key
  UNIQUE(subcategoria_id, nombre, tipo);

-- 3. Limpiar unidades existentes
DELETE FROM unidades_subcategoria;
ALTER SEQUENCE unidades_subcategoria_id_seq RESTART WITH 1;

-- ═══════════════════════════════════════════════════════════════════
-- INSERTAR UNIDADES POR SUBCATEGORIA + TIPO (según catálogo Excel)
-- ═══════════════════════════════════════════════════════════════════

-- ── Aromáticas y medicinales ──
-- Menudeo: kg, ramo, bolsa | Mayoreo: kg, ramo, bolsa
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('AGR_AROMATICAS_MED', 'Kg', 'MENUDEO'),
('AGR_AROMATICAS_MED', 'Ramo/Manojo', 'MENUDEO'),
('AGR_AROMATICAS_MED', 'Bolsa', 'MENUDEO'),
('AGR_AROMATICAS_MED', 'Kg', 'MAYOREO'),
('AGR_AROMATICAS_MED', 'Ramo/Manojo', 'MAYOREO'),
('AGR_AROMATICAS_MED', 'Bolsa', 'MAYOREO');

-- ── Flores ornamentales ──
-- Menudeo: ramo, pieza | Mayoreo: ramo, pieza, docena
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('AGR_FLORES', 'Ramo/Manojo', 'MENUDEO'),
('AGR_FLORES', 'Pieza', 'MENUDEO'),
('AGR_FLORES', 'Ramo/Manojo', 'MAYOREO'),
('AGR_FLORES', 'Pieza', 'MAYOREO'),
('AGR_FLORES', 'Docena', 'MAYOREO');

-- ── Forrajes ──
-- Menudeo: kg, costal | Mayoreo: kg, costal, tonelada
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('AGR_FORRAJES', 'Kg', 'MENUDEO'),
('AGR_FORRAJES', 'Costal/Bulto', 'MENUDEO'),
('AGR_FORRAJES', 'Kg', 'MAYOREO'),
('AGR_FORRAJES', 'Costal/Bulto', 'MAYOREO'),
('AGR_FORRAJES', 'Tonelada', 'MAYOREO');

-- ── Frutas ──
-- Menudeo: kg, pieza, caja, jaba | Mayoreo: kg, pieza, caja, jaba
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('AGR_FRUTAS', 'Kg', 'MENUDEO'),
('AGR_FRUTAS', 'Pieza', 'MENUDEO'),
('AGR_FRUTAS', 'Caja', 'MENUDEO'),
('AGR_FRUTAS', 'Jaba', 'MENUDEO'),
('AGR_FRUTAS', 'Kg', 'MAYOREO'),
('AGR_FRUTAS', 'Pieza', 'MAYOREO'),
('AGR_FRUTAS', 'Caja', 'MAYOREO'),
('AGR_FRUTAS', 'Jaba', 'MAYOREO');

-- ── Granos básicos ──
-- Menudeo: kg, costal, bolsa | Mayoreo: kg, costal, bolsa, tonelada, quintal
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('AGR_GRANOS_BASICOS', 'Kg', 'MENUDEO'),
('AGR_GRANOS_BASICOS', 'Costal/Bulto', 'MENUDEO'),
('AGR_GRANOS_BASICOS', 'Bolsa', 'MENUDEO'),
('AGR_GRANOS_BASICOS', 'Kg', 'MAYOREO'),
('AGR_GRANOS_BASICOS', 'Costal/Bulto', 'MAYOREO'),
('AGR_GRANOS_BASICOS', 'Bolsa', 'MAYOREO'),
('AGR_GRANOS_BASICOS', 'Tonelada', 'MAYOREO'),
('AGR_GRANOS_BASICOS', 'Quintal (100 kg)', 'MAYOREO');

-- ── Hortalizas ──
-- Menudeo: kg, pieza, caja, jaba, bolsa | Mayoreo: kg, pieza, caja, jaba, bolsa
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('AGR_HORTALIZAS', 'Kg', 'MENUDEO'),
('AGR_HORTALIZAS', 'Pieza', 'MENUDEO'),
('AGR_HORTALIZAS', 'Caja', 'MENUDEO'),
('AGR_HORTALIZAS', 'Jaba', 'MENUDEO'),
('AGR_HORTALIZAS', 'Bolsa', 'MENUDEO'),
('AGR_HORTALIZAS', 'Kg', 'MAYOREO'),
('AGR_HORTALIZAS', 'Pieza', 'MAYOREO'),
('AGR_HORTALIZAS', 'Caja', 'MAYOREO'),
('AGR_HORTALIZAS', 'Jaba', 'MAYOREO'),
('AGR_HORTALIZAS', 'Bolsa', 'MAYOREO');

-- ── Industriales ──
-- Menudeo: kg, costal | Mayoreo: kg, costal, tonelada, quintal
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('AGR_INDUSTRIALES', 'Kg', 'MENUDEO'),
('AGR_INDUSTRIALES', 'Costal/Bulto', 'MENUDEO'),
('AGR_INDUSTRIALES', 'Kg', 'MAYOREO'),
('AGR_INDUSTRIALES', 'Costal/Bulto', 'MAYOREO'),
('AGR_INDUSTRIALES', 'Tonelada', 'MAYOREO'),
('AGR_INDUSTRIALES', 'Quintal (100 kg)', 'MAYOREO');

-- ── Leguminosas ──
-- Menudeo: kg, costal, bolsa | Mayoreo: kg, costal, bolsa, tonelada, quintal
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('AGR_LEGUMINOSAS', 'Kg', 'MENUDEO'),
('AGR_LEGUMINOSAS', 'Costal/Bulto', 'MENUDEO'),
('AGR_LEGUMINOSAS', 'Bolsa', 'MENUDEO'),
('AGR_LEGUMINOSAS', 'Kg', 'MAYOREO'),
('AGR_LEGUMINOSAS', 'Costal/Bulto', 'MAYOREO'),
('AGR_LEGUMINOSAS', 'Bolsa', 'MAYOREO'),
('AGR_LEGUMINOSAS', 'Tonelada', 'MAYOREO'),
('AGR_LEGUMINOSAS', 'Quintal (100 kg)', 'MAYOREO');

-- ── Oleaginosas y semillas ──
-- Menudeo: kg, bolsa | Mayoreo: kg, bolsa, costal, tonelada
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('AGR_OLEAG_SEMILLAS', 'Kg', 'MENUDEO'),
('AGR_OLEAG_SEMILLAS', 'Bolsa', 'MENUDEO'),
('AGR_OLEAG_SEMILLAS', 'Kg', 'MAYOREO'),
('AGR_OLEAG_SEMILLAS', 'Bolsa', 'MAYOREO'),
('AGR_OLEAG_SEMILLAS', 'Costal/Bulto', 'MAYOREO'),
('AGR_OLEAG_SEMILLAS', 'Tonelada', 'MAYOREO');

-- ── Otros / Revisar ──
-- Menudeo: kg, pieza, bolsa | Mayoreo: kg, pieza, bolsa
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('AGR_OTROS_REVISION', 'Kg', 'MENUDEO'),
('AGR_OTROS_REVISION', 'Pieza', 'MENUDEO'),
('AGR_OTROS_REVISION', 'Bolsa', 'MENUDEO'),
('AGR_OTROS_REVISION', 'Kg', 'MAYOREO'),
('AGR_OTROS_REVISION', 'Pieza', 'MAYOREO'),
('AGR_OTROS_REVISION', 'Bolsa', 'MAYOREO');

-- ── Tubérculos y raíces ──
-- Menudeo: kg, costal, pieza | Mayoreo: kg, costal, pieza
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('AGR_TUBERCULOS', 'Kg', 'MENUDEO'),
('AGR_TUBERCULOS', 'Costal/Bulto', 'MENUDEO'),
('AGR_TUBERCULOS', 'Pieza', 'MENUDEO'),
('AGR_TUBERCULOS', 'Kg', 'MAYOREO'),
('AGR_TUBERCULOS', 'Costal/Bulto', 'MAYOREO'),
('AGR_TUBERCULOS', 'Pieza', 'MAYOREO');

-- ── Aves (pollo) ──
-- Menudeo: kg, pieza | Mayoreo: kg, pieza, caja
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('PEC_AVE', 'Kg', 'MENUDEO'),
('PEC_AVE', 'Pieza', 'MENUDEO'),
('PEC_AVE', 'Kg', 'MAYOREO'),
('PEC_AVE', 'Pieza', 'MAYOREO'),
('PEC_AVE', 'Caja', 'MAYOREO');

-- ── Bovinos ──
-- Menudeo: kg | Mayoreo: kg
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('PEC_BOV', 'Kg', 'MENUDEO'),
('PEC_BOV', 'Kg', 'MAYOREO');

-- ── Huevo ──
-- Menudeo: docena, charola | Mayoreo: docena, charola, caja, reja
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('PEC_HUE', 'Docena', 'MENUDEO'),
('PEC_HUE', 'Charola', 'MENUDEO'),
('PEC_HUE', 'Docena', 'MAYOREO'),
('PEC_HUE', 'Charola', 'MAYOREO'),
('PEC_HUE', 'Caja', 'MAYOREO'),
('PEC_HUE', 'Reja (huevo)', 'MAYOREO');

-- ── Porcinos ──
-- Menudeo: kg | Mayoreo: kg
INSERT INTO unidades_subcategoria (subcategoria_id, nombre, tipo) VALUES
('PEC_POR', 'Kg', 'MENUDEO'),
('PEC_POR', 'Kg', 'MAYOREO');
