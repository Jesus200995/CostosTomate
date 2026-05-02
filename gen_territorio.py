import openpyxl

wb = openpyxl.load_workbook('municipios (1).xlsx')
ws = wb['territorios_mun_psv___territori']

lines = []
lines.append("ALTER TABLE municipios ADD COLUMN IF NOT EXISTS territorio VARCHAR(100);")

for i, row in enumerate(ws.iter_rows(values_only=True)):
    if i == 0:
        continue
    clave_mun = row[7]
    territorio = row[8]
    if territorio and clave_mun:
        terr_escaped = str(territorio).replace("'", "''")
        lines.append(f"UPDATE municipios SET territorio = '{terr_escaped}' WHERE clave_mun = {clave_mun};")

with open('update_territorio.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Generated update_territorio.sql with {len(lines)} lines')
