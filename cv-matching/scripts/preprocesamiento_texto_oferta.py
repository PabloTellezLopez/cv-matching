import os
import re
import unicodedata
# from ftfy import fix_text  # Descomenta si quieres usar ftfy para arreglar codificaciones extrañas
import pandas as pd
from pathlib import Path
from typing import List, Dict

def normalizar_unicode(texto: str) -> str:
    """
    Descompone caracteres Unicode (NFD), elimina marcas de acento,
    y recompone (NFC), dejando solo la forma base de cada carácter.
    """
    # 1) Arregla codificaciones extrañas (opcional)
    # texto = fix_text(texto)

    # 2) Descomposición canónica
    texto = unicodedata.normalize('NFD', texto)
    # 3) Elimina todas las marcas de categoría 'Mn' (Nonspacing_Mark)
    texto = ''.join(ch for ch in texto if unicodedata.category(ch) != 'Mn')
    # 4) Recomposición canónica
    return unicodedata.normalize('NFC', texto)

def limpiar_texto(texto: str) -> str:
    """
    1) Normaliza tildes y caracteres raros
    2) Elimina saltos de línea, múltiples espacios y trim.
    """
    texto = str(texto)
    texto = normalizar_unicode(texto)
    texto = re.sub(r'\s*\n\s*', ' ', texto)
    texto = re.sub(r'\s{2,}', ' ', texto)
    return texto.strip()

def extraer_descripcion(offer_text: str) -> str:
    """
    Extrae la descripción de la oferta desde la sección 'Descripción:'.
    Corta antes de 'Descripción del puesto:' si está presente.
    """
    if "Descripción:" in offer_text:
        desc = offer_text.split("Descripción:", 1)[1]
        if "Descripción del puesto:" in desc:
            desc = desc.split("Descripción del puesto:", 1)[0]
        return limpiar_texto(desc)
    return ""

def procesar_ofertas_archivo(ruta_archivo: str) -> pd.DataFrame:
    """
    Procesa un archivo .txt con varias ofertas separadas por líneas de guiones.
    Retorna un DataFrame con el nombre del archivo y la descripción de cada oferta.
    """
    with open(ruta_archivo, 'r', encoding='utf-8') as file:
        contenido = file.read()

    offers: List[str] = re.split(r'-{5,}', contenido)
    offers = [offer.strip() for offer in offers if offer.strip()]

    data: List[Dict[str, str]] = []
    for offer in offers:
        descripcion = extraer_descripcion(offer)
        data.append({
            'nombre_archivo': os.path.basename(ruta_archivo),
            'descripcion_oferta': descripcion
        })

    return pd.DataFrame(data)

def procesar_carpeta_ofertas(ruta_carpeta: str) -> Dict[str, pd.DataFrame]:
    """
    Procesa todos los archivos .txt en una carpeta y devuelve un diccionario
    con un DataFrame por archivo.
    """
    carpeta = Path(ruta_carpeta)
    archivos_txt = list(carpeta.glob("*.txt"))

    dataframes_por_archivo: Dict[str, pd.DataFrame] = {}

    for ruta in archivos_txt:
        nombre_archivo = ruta.stem
        df = procesar_ofertas_archivo(str(ruta))
        dataframes_por_archivo[nombre_archivo] = df

    return dataframes_por_archivo

if __name__ == "__main__":
    # Ruta de la carpeta donde están los .txt
    ruta_carpeta = "data/raw/ofertas"

    # Procesar todos los archivos
    dataframes = procesar_carpeta_ofertas(ruta_carpeta)

    # Mostrar una vista previa y guardar cada DataFrame
    for nombre, df in dataframes.items():
        print(f"\nArchivo: {nombre}")
        print(df.head(), "\n")
        ruta_salida = f"data/interim/{nombre}_ofertas.csv"
        df.to_csv(ruta_salida, index=False, encoding='utf-8')
        print(f"Guardado: {ruta_salida}")
