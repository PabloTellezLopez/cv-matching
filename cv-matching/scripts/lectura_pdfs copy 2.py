import fitz  # PyMuPDF

def extraer_texto_pymupdf(pdf_path):
    doc = fitz.open(pdf_path)
    texto_total = ""
    for pagina in doc:
        texto_total += pagina.get_text()
    return texto_total

# Uso
texto = extraer_texto_pymupdf(".\CVs\cv00.pdf")
print(texto)