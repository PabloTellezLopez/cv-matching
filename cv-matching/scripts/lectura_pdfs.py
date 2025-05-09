import os
import csv
import pdfplumber

# Definir la carpeta donde están los CVs
ruta_cvs = r"C:\Users\Pablo\OneDrive - Universidad Loyola Andalucía\Master\TFM\CVs_Train"
ruta_csv = r"C:\Users\Pablo\OneDrive - Universidad Loyola Andalucía\Master\TFM\cvs_texto_train.csv"

# Obtener todos los archivos PDF en la carpeta y ordenarlos
archivos_cvs = sorted([f for f in os.listdir(ruta_cvs) if f.endswith(".pdf")])

# Crear y escribir el CSV
with open(ruta_csv, mode="w", newline="", encoding="utf-8-sig") as archivo_csv:
    escritor_csv = csv.writer(archivo_csv)
    
    # Escribir encabezados
    escritor_csv.writerow(["Nombre del archivo", "Texto extraído"])
    
    # Recorrer cada CV y extraer su texto
    for archivo in archivos_cvs:
        ruta_pdf = os.path.join(ruta_cvs, archivo)
        texto_completo = ""

        with pdfplumber.open(ruta_pdf) as pdf:
            for pagina in pdf.pages:
                texto_completo += " " + (pagina.extract_text() or "").replace("\n", " ")

        # Escribir en el CSV
        escritor_csv.writerow([archivo, texto_completo])

print(f"✅ CSV generado correctamente en: {ruta_csv}")
