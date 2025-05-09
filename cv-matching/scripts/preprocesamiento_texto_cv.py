import pandas as pd
import re
from pandas import DataFrame
import unicodedata

def limpiar_texto(texto: str) -> str:
    """
    Limpia el texto eliminando saltos de línea, múltiples espacios y espacios al inicio/fin.
    """
    texto = str(texto)
    texto = texto.replace('\n', ' ')
    texto = texto.replace('\r', ' ')
    texto = texto.replace('\t', ' ')
    texto = quitar_tildes_y_normalizar(texto)
    texto = re.sub(r'\s*\n\s*', ' ', texto)
    texto = re.sub(r'\s{2,}', ' ', texto)
    texto = texto.strip()
    return texto

def cargar_datos(ruta_train: str, ruta_test: str) -> tuple[DataFrame, DataFrame]:
    """
    Carga los archivos CSV de entrenamiento y test.
    """
    df_train = pd.read_csv(ruta_train, sep=',', encoding='utf-8')
    df_test = pd.read_csv(ruta_test, sep=',', encoding='utf-8')
    return df_train, df_test

def normalizar_columnas(df: DataFrame, columna_texto: str) -> DataFrame:
    """
    Aplica la limpieza de texto a una columna del DataFrame.
    """
    df['texto_normalizado'] = df[columna_texto].apply(limpiar_texto)
    return df

def quitar_tildes_y_normalizar(texto: str) -> str:
    # 1) Arregla codificaciones extrañas comunes
    #    (puedes usar ftfy.fix_text si prefieres)
    #    from ftfy import fix_text
    #    texto = fix_text(texto)

    # 2) Descompone caracteres Unicode (NFD)
    texto = unicodedata.normalize('NFD', texto)

    # 3) Elimina las marcas de acento
    texto = ''.join(ch for ch in texto if unicodedata.category(ch) != 'Mn')

    # 4) Reconstruye en forma compuesta (NFC)
    texto = unicodedata.normalize('NFC', texto)
    return texto

if __name__ == "__main__":
    # Rutas de los archivos CSV
    ruta_train = r"data\interim\cvs_texto_train.csv"
    ruta_test = r"data\interim\cvs_texto_test.csv"

    # Cargar datos
    df_train, df_test = cargar_datos(ruta_train, ruta_test)

    # Normalizar texto
    df_train = normalizar_columnas(df_train, 'Texto extraído')
    df_test = normalizar_columnas(df_test, 'Texto extraído')

    # Guardar los DataFrames normalizados
    df_train.to_csv(r"data\interim\cvs_train_preprocesado.csv", index=False, encoding='utf-8')
    df_test.to_csv(r"data\interim\cvs_test_preprocesado.csv", index=False, encoding='utf-8')

    print("Proceso de extracción, normalización y guardado completado.")
