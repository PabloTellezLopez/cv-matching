import os
import glob
import pandas as pd


def parse_cv_sector_mapping(mapping_file):
    """
    Parsea un archivo de mapping entre CVs y sectores con sus scores de afinidad.

    Args:
        mapping_file (str): Ruta al archivo de texto, formato esperado:
            cv00.pdf cdatos 0.9 ingdatos 0.6

    Returns:
        dict: Diccionario {cv_id: {sector: score, ...}}

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si alguna línea del archivo no sigue el formato esperado.
    """
    mapping = {}
    if not os.path.exists(mapping_file):
        raise FileNotFoundError(f"No se encontró el archivo de mapping: {mapping_file}")
    with open(mapping_file, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            tokens = line.strip().split()
            if not tokens:
                continue
            if len(tokens) < 3 or len(tokens[1:]) % 2 != 0:
                raise ValueError(f"Formato incorrecto en la línea {lineno}: {line}")
            cv_id = tokens[0]
            try:
                sector_score_pairs = list(zip(tokens[1::2], map(float, tokens[2::2])))
            except Exception as e:
                raise ValueError(
                    f"Error al parsear scores en línea {lineno}: {line}\n{e}"
                )
            mapping[cv_id] = dict(sector_score_pairs)
    return mapping


def extract_sector_from_filename(filename):
    """
    Extrae el sector relevante a partir del nombre de archivo.
    Personalizar según nomenclatura de tus archivos.

    Args:
        filename (str): Nombre del archivo (no la ruta completa).

    Returns:
        str: Sector asociado al archivo.

    Raises:
        ValueError: Si no se reconoce ningún sector en el nombre.
    """
    fname = filename.lower()
    if "jurista" in fname:
        return "jurista"
    elif "traductor" in fname:
        return "traductor"
    elif "cdatos" in fname or "ciencia_de_datos" in fname:
        return "cdatos"
    elif "ingdatos" in fname or "ingeniero_de_datos" in fname:
        return "ingdatos"
    else:
        raise ValueError(f"No se pudo extraer sector de {filename}")


def read_offers(folder_path=".", pattern="*_ofertas.csv"):
    """
    Lee todos los archivos de ofertas de un directorio y añade la columna de sector.

    Args:
        folder_path (str): Carpeta donde buscar los archivos.
        pattern (str): Patrón de archivos a leer.

    Returns:
        pd.DataFrame: Ofertas de trabajo combinadas, con columnas 'sector_oferta' y 'offer_id'.

    Raises:
        FileNotFoundError: Si no se encuentran archivos que coincidan con el patrón.
        ValueError: Si algún archivo no puede ser procesado.
    """
    offer_dfs = []
    file_list = glob.glob(os.path.join(folder_path, pattern))
    if not file_list:
        raise FileNotFoundError(
            f"No se encontraron archivos con patrón '{pattern}' en '{folder_path}'"
        )
    for filepath in file_list:
        filename = os.path.basename(filepath)
        try:
            sector = extract_sector_from_filename(filename)
            df = pd.read_csv(filepath)
        except Exception as e:
            raise ValueError(f"Error procesando '{filename}': {e}")
        df["sector_oferta"] = sector
        if "offer_id" not in df.columns:
            df["offer_id"] = [f"{sector}_{i}" for i in range(len(df))]
        offer_dfs.append(df)
    try:
        offers = pd.concat(offer_dfs, ignore_index=True)
    except Exception as e:
        raise ValueError(f"Error al concatenar las ofertas: {e}")
    return offers


def build_pairwise_dataset(mapping, offers, label_threshold=0.5):
    """
    Genera todas las combinaciones posibles CV-oferta, asignando score y label binario.

    Args:
        mapping (dict): Diccionario {cv_id: {sector: score}}.
        offers (pd.DataFrame): DataFrame de ofertas (debe incluir 'offer_id' y 'sector_oferta').
        label_threshold (float): Umbral para binarizar el score.

    Returns:
        pd.DataFrame: Pares CV-oferta con 'score', 'label_binario', y todos los campos de la oferta.
    """
    all_pairs = []
    if offers.empty:
        raise ValueError("El DataFrame de ofertas está vacío.")
    for cv_id, sector_scores in mapping.items():
        for _, offer in offers.iterrows():
            sector = offer["sector_oferta"]
            score = sector_scores.get(sector, 0.0)
            label_bin = int(score >= label_threshold)
            offer_info = offer.to_dict()
            offer_id = offer_info.pop("offer_id")
            all_pairs.append(
                {
                    "cv_id": cv_id,
                    "offer_id": offer_id,
                    "sector_oferta": sector,
                    "score": score,
                    "label_binario": label_bin,
                    **offer_info,
                }
            )
    if not all_pairs:
        raise ValueError(
            "No se generaron pares CV-oferta. ¿Revisaste los archivos de entrada?"
        )
    df_pairs = pd.DataFrame(all_pairs)
    return df_pairs


def add_ranking(df_pairs, score_col="score", group_col="cv_id"):
    """
    Añade una columna de ranking por CV, ordenando por score descendente y aleatorizando empates.

    Args:
        df_pairs (pd.DataFrame): DataFrame de pares.
        score_col (str): Nombre de la columna de score.
        group_col (str): Nombre de la columna de grupo (CV).

    Returns:
        pd.DataFrame: DataFrame con columna 'rank' añadida.
    """
    df_pairs = df_pairs.copy()

    def sort_and_rank(subdf):
        # Orden descendente por score, aleatorizar empates
        subdf = subdf.sample(frac=1, random_state=42).sort_values(
            score_col, ascending=False
        )
        subdf["rank"] = range(1, len(subdf) + 1)
        return subdf

    df_ranked = df_pairs.groupby(group_col, group_keys=False).apply(sort_and_rank)
    return df_ranked


def save_dataset(df, output_file="data/interim/dataset_ranking_test.csv"):
    """
    Guarda el DataFrame filtrando solo las columnas deseadas.

    Args:
        df (pd.DataFrame): DataFrame de pares rankeados.
        output_file (str): Ruta del archivo de salida.
    """
    columnas_finales = [
        "cv_id",
        "offer_id",
        "sector_oferta",
        "score",
        "label_binario",
        "rank",
    ]
    if not all(col in df.columns for col in columnas_finales):
        missing = [col for col in columnas_finales if col not in df.columns]
        raise ValueError(f"Faltan columnas en el DataFrame para guardar: {missing}")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df[columnas_finales].to_csv(output_file, index=False)


def main():
    """
    Pipeline principal del script: carga mappings, lee ofertas, crea el dataset y lo guarda.
    """
    mapping_file = "data/raw/cvs_test/cv_sector.txt"
    offers_folder = "data/interim"
    output_file = "data/interim/dataset_ranking_test.csv"

    try:
        mapping = parse_cv_sector_mapping(mapping_file)
        offers = read_offers(offers_folder)
        df_pairs = build_pairwise_dataset(mapping, offers, label_threshold=0.5)
        df_pairs_ranked = add_ranking(df_pairs)
        save_dataset(df_pairs_ranked, output_file=output_file)
        print(
            f"¡Dataset generado correctamente con {len(df_pairs_ranked)} pares! Archivo: {output_file}"
        )
    except Exception as e:
        print("ERROR en la ejecución del script:", e)


if __name__ == "__main__":
    main()
