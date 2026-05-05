-- Correcciones de acentos y nombres finales
UPDATE catalogo_centrales SET municipio='Torreón' WHERE id=61;
UPDATE catalogo_centrales SET municipio='Culiacán' WHERE id=80;
UPDATE catalogo_centrales SET municipio='Mérida' WHERE id=86;
UPDATE catalogo_centrales SET estado='Yucatán' WHERE id=86;
UPDATE catalogo_centrales SET nombre_central='Central de Abasto de Mérida / Unión de Comerciantes del Mercado de Abastos de Yucatán' WHERE id=86;
UPDATE catalogo_centrales SET nombre_central='Mercado de Abasto Felipe Ángeles' WHERE id=69;
UPDATE catalogo_centrales SET nombre_central='Central de Abasto de Veracruz / Asociación de Locatarios de la Central de Veracruz S.A. de C.V.' WHERE id=85;
UPDATE catalogo_centrales SET nombre_central='Union de Comerciantes Productores y Condominos del Centro de Abasto de Ecatepec, A.C.' WHERE id=31;

-- Verificación final
SELECT id, nombre_central, estado, municipio FROM catalogo_centrales WHERE id IN (61,69,80,85,86) ORDER BY id;
SELECT DISTINCT estado FROM catalogo_centrales WHERE estatus='autorizado' AND visible_pwa=TRUE ORDER BY estado;
