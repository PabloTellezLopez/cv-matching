import os
import csv
import pdfplumber
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Extrae el texto de un archivo PDF."""
    texto_completo = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for pagina in pdf.pages:
                texto_completo += " " + (pagina.extract_text() or "").replace("\n", " ")
    except Exception as e:
        print(f"Error al procesar {pdf_path}: {e}")
    return texto_completo.strip()

def process_cvs_folder(input_folder, output_csv):
    """Procesa todos los PDFs de una carpeta y guarda el texto extraído en un CSV."""
    input_path = Path(input_folder)
    pdf_files = sorted([f for f in input_path.iterdir() if f.suffix.lower() == ".pdf"])

    with open(output_csv, mode="w", newline="", encoding="utf-8-sig") as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        escritor_csv.writerow(["Nombre del archivo", "Texto extraído"])
        for pdf_file in pdf_files:
            texto = extract_text_from_pdf(pdf_file)
            escritor_csv.writerow([pdf_file.name, texto])
    print(f"✅ CSV generado correctamente en: {output_csv}")

if __name__ == "__main__":
    datasets = {
        "train": ("data/raw/cvs_train", "data/interim/cvs_texto_train.csv"),
        "test": ("data/raw/cvs_test", "data/interim/cvs_texto_test.csv"),
    }
    for name, (folder, csv_path) in datasets.items():
        print(f"Procesando {name}...")
        process_cvs_folder(folder, csv_path)
