import os
import pdfplumber

# Definir la carpeta donde están los CVs
ruta_cvs = r"C:\Users\Pablo\OneDrive - Universidad Loyola Andalucía\Master\TFM\CVs"

# Lista de archivos específicos a leer
archivos_a_leer = ["cv11.pdf", "cv13.pdf"]

# Recorrer cada CV y mostrar el texto extraído en pantalla
for archivo in archivos_a_leer:
    ruta_pdf = os.path.join(ruta_cvs, archivo)

    print(f"\n=== Contenido de {archivo} ===\n")

    with pdfplumber.open(ruta_pdf) as pdf:
        for num_pagina, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text()
            if texto:
                print(f"--- Página {num_pagina} ---")
                print(texto.replace("\n", " "))
            else:
                print(f"--- Página {num_pagina} --- (No se pudo extraer texto)")

print("\nProceso finalizado.")
