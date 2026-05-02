-- Limpieza de tablas (en orden por dependencias)
DELETE FROM detalle_precios;
DELETE FROM reportes_precios;
DELETE FROM unidades_subcategoria;
DELETE FROM productos;
DELETE FROM subcategorias;
DELETE FROM categorias;

-- Reset sequences
ALTER SEQUENCE productos_id_seq RESTART WITH 1;
ALTER SEQUENCE unidades_subcategoria_id_seq RESTART WITH 1;

-- ═══════════════════════════════════════════════════════════════════
-- CATEGORIAS
-- ═══════════════════════════════════════════════════════════════════
INSERT INTO categorias (id, nombre, descripcion) VALUES
('AGRICOLA', 'Agrícola', 'Cultivos agrícolas'),
('PECUARIO', 'Pecuario', 'Bovinos, porcinos, aves y huevo');

-- ═══════════════════════════════════════════════════════════════════
-- SUBCATEGORIAS
-- ═══════════════════════════════════════════════════════════════════
INSERT INTO subcategorias (id, categoria_id, nombre) VALUES
-- Agrícola
('AGR_AROMATICAS_MED', 'AGRICOLA', 'Aromáticas y medicinales'),
('AGR_FLORES', 'AGRICOLA', 'Flores ornamentales'),
('AGR_FORRAJES', 'AGRICOLA', 'Forrajes'),
('AGR_FRUTAS', 'AGRICOLA', 'Frutas'),
('AGR_GRANOS_BASICOS', 'AGRICOLA', 'Granos básicos'),
('AGR_HORTALIZAS', 'AGRICOLA', 'Hortalizas'),
('AGR_INDUSTRIALES', 'AGRICOLA', 'Industriales'),
('AGR_LEGUMINOSAS', 'AGRICOLA', 'Leguminosas'),
('AGR_OLEAG_SEMILLAS', 'AGRICOLA', 'Oleaginosas y semillas'),
('AGR_OTROS_REVISION', 'AGRICOLA', 'Otros / Revisar'),
('AGR_TUBERCULOS', 'AGRICOLA', 'Tubérculos y raíces'),
-- Pecuario
('PEC_AVE', 'PECUARIO', 'Aves (pollo)'),
('PEC_BOV', 'PECUARIO', 'Bovinos'),
('PEC_HUE', 'PECUARIO', 'Huevo'),
('PEC_POR', 'PECUARIO', 'Porcinos');

-- ═══════════════════════════════════════════════════════════════════
-- PRODUCTOS
-- ═══════════════════════════════════════════════════════════════════

-- Aromáticas y medicinales (18)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('AGR_AROMATICAS_MED', 'Albahaca'),
('AGR_AROMATICAS_MED', 'Anís'),
('AGR_AROMATICAS_MED', 'Árnica'),
('AGR_AROMATICAS_MED', 'Cilantro'),
('AGR_AROMATICAS_MED', 'Eneldo'),
('AGR_AROMATICAS_MED', 'Epazote'),
('AGR_AROMATICAS_MED', 'Gordolobo'),
('AGR_AROMATICAS_MED', 'Hierbabuena'),
('AGR_AROMATICAS_MED', 'Manzanilla'),
('AGR_AROMATICAS_MED', 'Mejorana'),
('AGR_AROMATICAS_MED', 'Menta'),
('AGR_AROMATICAS_MED', 'Orégano'),
('AGR_AROMATICAS_MED', 'Pápalo'),
('AGR_AROMATICAS_MED', 'Perejil'),
('AGR_AROMATICAS_MED', 'Salvia'),
('AGR_AROMATICAS_MED', 'Tarragón'),
('AGR_AROMATICAS_MED', 'Tomillo'),
('AGR_AROMATICAS_MED', 'Toronjil');

-- Flores ornamentales (16)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('AGR_FLORES', 'Alhelí'),
('AGR_FLORES', 'Alstroemeria'),
('AGR_FLORES', 'Áster'),
('AGR_FLORES', 'Azucena'),
('AGR_FLORES', 'Cempasúchil'),
('AGR_FLORES', 'Clavel'),
('AGR_FLORES', 'Crisantemo'),
('AGR_FLORES', 'Gladiola'),
('AGR_FLORES', 'Margarita'),
('AGR_FLORES', 'Nardo'),
('AGR_FLORES', 'Nube'),
('AGR_FLORES', 'Orquídea'),
('AGR_FLORES', 'Perrito'),
('AGR_FLORES', 'Rosa'),
('AGR_FLORES', 'Statice'),
('AGR_FLORES', 'Terciopelo');

-- Forrajes (4)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('AGR_FORRAJES', 'Alfalfa'),
('AGR_FORRAJES', 'Pastos y forrajes'),
('AGR_FORRAJES', 'Trébol'),
('AGR_FORRAJES', 'Zacate');

-- Frutas (6)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('AGR_FRUTAS', 'Avellana'),
('AGR_FRUTAS', 'Fresa'),
('AGR_FRUTAS', 'Melón'),
('AGR_FRUTAS', 'Plátano'),
('AGR_FRUTAS', 'Sandía'),
('AGR_FRUTAS', 'Tangelo');

-- Granos básicos (14)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('AGR_GRANOS_BASICOS', 'Alpiste'),
('AGR_GRANOS_BASICOS', 'Arroz'),
('AGR_GRANOS_BASICOS', 'Avena'),
('AGR_GRANOS_BASICOS', 'Cebada'),
('AGR_GRANOS_BASICOS', 'Centeno'),
('AGR_GRANOS_BASICOS', 'Harina de maíz'),
('AGR_GRANOS_BASICOS', 'Maíz'),
('AGR_GRANOS_BASICOS', 'Masa de maíz'),
('AGR_GRANOS_BASICOS', 'Mijo'),
('AGR_GRANOS_BASICOS', 'Nixtamal'),
('AGR_GRANOS_BASICOS', 'Quinoa'),
('AGR_GRANOS_BASICOS', 'Sorgo'),
('AGR_GRANOS_BASICOS', 'Tortilla de maíz'),
('AGR_GRANOS_BASICOS', 'Trigo');

-- Hortalizas (24)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('AGR_HORTALIZAS', 'Ajo'),
('AGR_HORTALIZAS', 'Alcachofa'),
('AGR_HORTALIZAS', 'Apio'),
('AGR_HORTALIZAS', 'Berenjena'),
('AGR_HORTALIZAS', 'Brócoli'),
('AGR_HORTALIZAS', 'Calabaza'),
('AGR_HORTALIZAS', 'Cebolla'),
('AGR_HORTALIZAS', 'Cebollín'),
('AGR_HORTALIZAS', 'Chaya'),
('AGR_HORTALIZAS', 'Chayote'),
('AGR_HORTALIZAS', 'Chilacayote'),
('AGR_HORTALIZAS', 'Chile'),
('AGR_HORTALIZAS', 'Chipilín'),
('AGR_HORTALIZAS', 'Col'),
('AGR_HORTALIZAS', 'Espinaca'),
('AGR_HORTALIZAS', 'Huauzontle'),
('AGR_HORTALIZAS', 'Jitomate'),
('AGR_HORTALIZAS', 'Lechuga'),
('AGR_HORTALIZAS', 'Pepino'),
('AGR_HORTALIZAS', 'Poro'),
('AGR_HORTALIZAS', 'Quelite'),
('AGR_HORTALIZAS', 'Tomate'),
('AGR_HORTALIZAS', 'Tomatillo'),
('AGR_HORTALIZAS', 'Verdolaga');

-- Industriales (5)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('AGR_INDUSTRIALES', 'Algodón'),
('AGR_INDUSTRIALES', 'Caña de azúcar'),
('AGR_INDUSTRIALES', 'Jamaica'),
('AGR_INDUSTRIALES', 'Maguey'),
('AGR_INDUSTRIALES', 'Tabaco');

-- Leguminosas (5)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('AGR_LEGUMINOSAS', 'Chícharo'),
('AGR_LEGUMINOSAS', 'Frijol'),
('AGR_LEGUMINOSAS', 'Garbanzo'),
('AGR_LEGUMINOSAS', 'Haba'),
('AGR_LEGUMINOSAS', 'Lenteja');

-- Oleaginosas y semillas (9)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('AGR_OLEAG_SEMILLAS', 'Ajonjolí'),
('AGR_OLEAG_SEMILLAS', 'Amaranto'),
('AGR_OLEAG_SEMILLAS', 'Cacahuate'),
('AGR_OLEAG_SEMILLAS', 'Cártamo'),
('AGR_OLEAG_SEMILLAS', 'Chía'),
('AGR_OLEAG_SEMILLAS', 'Girasol'),
('AGR_OLEAG_SEMILLAS', 'Linaza'),
('AGR_OLEAG_SEMILLAS', 'Mostaza'),
('AGR_OLEAG_SEMILLAS', 'Soya');

-- Otros / Revisar (6)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('AGR_OTROS_REVISION', 'Bangaña'),
('AGR_OTROS_REVISION', 'Clitoria'),
('AGR_OTROS_REVISION', 'Ebo'),
('AGR_OTROS_REVISION', 'Muzu'),
('AGR_OTROS_REVISION', 'Olleto'),
('AGR_OTROS_REVISION', 'Vaporub');

-- Tubérculos y raíces (7)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('AGR_TUBERCULOS', 'Betabel'),
('AGR_TUBERCULOS', 'Camote'),
('AGR_TUBERCULOS', 'Jícama'),
('AGR_TUBERCULOS', 'Nabo'),
('AGR_TUBERCULOS', 'Papa'),
('AGR_TUBERCULOS', 'Rábano'),
('AGR_TUBERCULOS', 'Zanahoria');

-- Aves (pollo) (2)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('PEC_AVE', 'Pollo entero'),
('PEC_AVE', 'Pollo por pieza');

-- Bovinos (2)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('PEC_BOV', 'Bovino en canal'),
('PEC_BOV', 'Bovino en pie');

-- Huevo (2)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('PEC_HUE', 'Huevo blanco'),
('PEC_HUE', 'Huevo rojo');

-- Porcinos (2)
INSERT INTO productos (subcategoria_id, nombre) VALUES
('PEC_POR', 'Porcino en canal'),
('PEC_POR', 'Porcino en pie');

-- ═══════════════════════════════════════════════════════════════════
-- UNIDADES POR SUBCATEGORIA
-- ═══════════════════════════════════════════════════════════════════

-- Aromáticas y medicinales
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('AGR_AROMATICAS_MED', 'Kg'),
('AGR_AROMATICAS_MED', 'Ramo/Manojo'),
('AGR_AROMATICAS_MED', 'Bolsa');

-- Flores ornamentales
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('AGR_FLORES', 'Ramo/Manojo'),
('AGR_FLORES', 'Pieza'),
('AGR_FLORES', 'Docena');

-- Forrajes
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('AGR_FORRAJES', 'Kg'),
('AGR_FORRAJES', 'Costal/Bulto'),
('AGR_FORRAJES', 'Tonelada');

-- Frutas
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('AGR_FRUTAS', 'Kg'),
('AGR_FRUTAS', 'Pieza'),
('AGR_FRUTAS', 'Caja'),
('AGR_FRUTAS', 'Jaba');

-- Granos básicos
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('AGR_GRANOS_BASICOS', 'Kg'),
('AGR_GRANOS_BASICOS', 'Costal/Bulto'),
('AGR_GRANOS_BASICOS', 'Bolsa'),
('AGR_GRANOS_BASICOS', 'Tonelada'),
('AGR_GRANOS_BASICOS', 'Quintal (100 kg)');

-- Hortalizas
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('AGR_HORTALIZAS', 'Kg'),
('AGR_HORTALIZAS', 'Pieza'),
('AGR_HORTALIZAS', 'Caja'),
('AGR_HORTALIZAS', 'Jaba'),
('AGR_HORTALIZAS', 'Bolsa');

-- Industriales
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('AGR_INDUSTRIALES', 'Kg'),
('AGR_INDUSTRIALES', 'Costal/Bulto'),
('AGR_INDUSTRIALES', 'Tonelada'),
('AGR_INDUSTRIALES', 'Quintal (100 kg)');

-- Leguminosas
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('AGR_LEGUMINOSAS', 'Kg'),
('AGR_LEGUMINOSAS', 'Costal/Bulto'),
('AGR_LEGUMINOSAS', 'Bolsa'),
('AGR_LEGUMINOSAS', 'Tonelada'),
('AGR_LEGUMINOSAS', 'Quintal (100 kg)');

-- Oleaginosas y semillas
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('AGR_OLEAG_SEMILLAS', 'Kg'),
('AGR_OLEAG_SEMILLAS', 'Bolsa'),
('AGR_OLEAG_SEMILLAS', 'Costal/Bulto'),
('AGR_OLEAG_SEMILLAS', 'Tonelada');

-- Otros / Revisar
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('AGR_OTROS_REVISION', 'Kg'),
('AGR_OTROS_REVISION', 'Pieza'),
('AGR_OTROS_REVISION', 'Bolsa');

-- Tubérculos y raíces
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('AGR_TUBERCULOS', 'Kg'),
('AGR_TUBERCULOS', 'Costal/Bulto'),
('AGR_TUBERCULOS', 'Pieza');

-- Aves (pollo)
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('PEC_AVE', 'Kg'),
('PEC_AVE', 'Pieza'),
('PEC_AVE', 'Caja');

-- Bovinos
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('PEC_BOV', 'Kg');

-- Huevo
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('PEC_HUE', 'Docena'),
('PEC_HUE', 'Charola'),
('PEC_HUE', 'Caja'),
('PEC_HUE', 'Reja (huevo)');

-- Porcinos
INSERT INTO unidades_subcategoria (subcategoria_id, nombre) VALUES
('PEC_POR', 'Kg');
