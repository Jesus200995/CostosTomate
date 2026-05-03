import pdfplumber
import json

pdf_path = r"c:\Users\jesus\Pictures\Costos Tomate\CostosTomate\documento_desarrollador_jitomate_costos_v2.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total de páginas: {len(pdf.pages)}\n")
        print("="*80)
        print("CONTENIDO COMPLETO DEL PDF")
        print("="*80 + "\n")
        
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            print(f"\n{'='*80}")
            print(f"PÁGINA {page_num}")
            print(f"{'='*80}\n")
            if text:
                print(text)
            else:
                print("[Página sin texto extraíble]")
                # Intentar extraer tablas
                tables = page.extract_tables()
                if tables:
                    print("\nTablas detectadas:")
                    for i, table in enumerate(tables):
                        print(f"\nTabla {i+1}:")
                        for row in table:
                            print(row)
except Exception as e:
    print(f"Error al leer el PDF: {e}")
    import traceback
    traceback.print_exc()
