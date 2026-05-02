import pandas as pd

filepath = r'c:\Users\Admin_1\Pictures\COSTOS\costos\catalogo_precios_PSV_con_mayoreo.xlsx'
xl = pd.ExcelFile(filepath)

print('=' * 80)
print('HOJAS DEL ARCHIVO')
print('=' * 80)
for i, name in enumerate(xl.sheet_names):
    print(f'  {i}: {name}')

print()

for name in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=name)
    print('=' * 80)
    print(f'HOJA: "{name}"  |  Filas: {len(df)}  |  Columnas: {len(df.columns)}')
    print('=' * 80)
    print(f'Columnas: {list(df.columns)}')
    print()
    print('--- Primeras 5 filas ---')
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    pd.set_option('display.max_colwidth', 60)
    print(df.head(5).to_string(index=True))
    print()

print()
print('=' * 80)
print('AHORA: CONTENIDO COMPLETO DE CADA HOJA')
print('=' * 80)

for name in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=name)
    print()
    print('#' * 80)
    print(f'# HOJA COMPLETA: "{name}"  ({len(df)} filas x {len(df.columns)} columnas)')
    print('#' * 80)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 300)
    pd.set_option('display.max_colwidth', 80)
    print(df.to_string(index=True))
    print()
