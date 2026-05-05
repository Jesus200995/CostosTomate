import pandas as pd

filepath = r'c:\Users\Admin_1\Pictures\TOMATE\CostosTomate\central_abasto_final.xlsx'
df = pd.read_excel(filepath, sheet_name='capa_unida')

def esc(val):
    if pd.isna(val) or val is None:
        return 'NULL'
    s = str(val).strip().replace("'", "''")
    return f"'{s}'"

def num(val):
    if pd.isna(val) or val is None:
        return 'NULL'
    return str(float(val))

lines = []
lines.append("-- Carga de centrales desde central_abasto_final.xlsx")
lines.append("-- Limpia e inserta 87 centrales")
lines.append("")
lines.append("DELETE FROM catalogo_centrales WHERE id > 0;")
lines.append("ALTER SEQUENCE catalogo_centrales_id_seq RESTART WITH 1;")
lines.append("")
lines.append("INSERT INTO catalogo_centrales (nombre_central, tipo, municipio, estado, latitud, longitud, estatus, visible_pwa) VALUES")

rows = []
for _, row in df.iterrows():
    nombre = esc(row.get('Nombre_Central'))
    tipo   = esc(row.get('Tipo'))
    mun    = esc(row.get('Municipio'))
    estado = esc(row.get('Estado'))
    lat    = num(row.get('latitud'))
    lon    = num(row.get('longitud'))
    rows.append(f"  ({nombre}, {tipo}, {mun}, {estado}, {lat}, {lon}, 'autorizado', TRUE)")

lines.append(',\n'.join(rows) + ';')
lines.append("")
lines.append("SELECT COUNT(*) as total_insertadas FROM catalogo_centrales;")
lines.append("SELECT DISTINCT estado FROM catalogo_centrales ORDER BY estado;")

sql = '\n'.join(lines)

with open(r'c:\Users\Admin_1\Pictures\TOMATE\CostosTomate\load_centrales.sql', 'w', encoding='utf-8') as f:
    f.write(sql)

print(f"SQL generado: {len(rows)} centrales")
print("Archivo: load_centrales.sql")
