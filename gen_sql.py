import json

with open('catalogos.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

sql_lines = []

sql_lines.append('DROP TABLE IF EXISTS municipios CASCADE;')
sql_lines.append('DROP TABLE IF EXISTS estados CASCADE;')
sql_lines.append('''CREATE TABLE estados (
  cve_ent VARCHAR(5) PRIMARY KEY,
  nom_ent VARCHAR(100) NOT NULL
);''')

for e in data['estados']:
    nom = e['nom_ent'].replace("'", "''")
    sql_lines.append(f"INSERT INTO estados (cve_ent, nom_ent) VALUES ('{e['cve_ent']}', '{nom}');")

sql_lines.append('''CREATE TABLE municipios (
  clave_mun INTEGER PRIMARY KEY,
  nomgeo VARCHAR(200) NOT NULL,
  cve_ent VARCHAR(5) NOT NULL REFERENCES estados(cve_ent)
);''')

ent_map = {e['nom_ent']: e['cve_ent'] for e in data['estados']}
for m in data['municipios']:
    nomgeo = m['nomgeo'].replace("'", "''")
    cve = ent_map.get(m['nom_ent'], '00')
    sql_lines.append(f"INSERT INTO municipios (clave_mun, nomgeo, cve_ent) VALUES ({m['clave_mun']}, '{nomgeo}', '{cve}');")

sql_lines.append('''
ALTER TABLE users ADD COLUMN IF NOT EXISTS tipo_capturista VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS estado VARCHAR(5);
ALTER TABLE users ADD COLUMN IF NOT EXISTS municipio INTEGER;
ALTER TABLE users ADD COLUMN IF NOT EXISTS localidad VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS telefono VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS consent BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS cac_id VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS cac_nombre VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS territorio VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS rol_comision VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS correo_institucional VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS rol_interno VARCHAR(100);
''')

with open('setup_db.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_lines))
print(f'Generated setup_db.sql with {len(sql_lines)} lines')
