import os
import glob
import pandas as pd
import random

# --------- 1. Parsear el mapping de CV-sector-score ---------

def parse_cv_sector_mapping(mapping_file):
    mapping = {}
    with open(mapping_file, "r", encoding="utf-8") as f:
        for line in f:
            tokens = line.strip().split()
            if not tokens: continue
            cv_id = tokens[0]
            sector_score_pairs = list(zip(tokens[1::2], map(float, tokens[2::2])))
            mapping[cv_id] = dict(sector_score_pairs)
    return mapping

# --------- 2. Leer todas las ofertas ---------

def read_offers(folder_path=".", pattern="*_ofertas.csv"):
    offer_dfs = []
    for filepath in glob.glob(os.path.join(folder_path, pattern)):
        # Extraer sector del nombre de archivo
        filename = os.path.basename(filepath)
        sector = extract_sector_from_filename(filename)
        df = pd.read_csv(filepath)
        # Añadir sector y offer_id si no existe
        df["sector_oferta"] = sector
        if "offer_id" not in df.columns:
            df["offer_id"] = [f"{sector}_{i}" for i in range(len(df))]
        offer_dfs.append(df)
    offers = pd.concat(offer_dfs, ignore_index=True)
    return offers

def extract_sector_from_filename(filename):
    filename = filename.lower()
    # Puedes ajustar esto según tus nombres reales
    if "jurista" in filename:
        return "jurista"
    elif "traductor" in filename:
        return "traductor"
    elif "cdatos" in filename or "ciencia_de_datos" in filename:
        return "cdatos"
    elif "ingdatos" in filename or "ingeniero_de_datos" in filename:
        return "ingdatos"
    else:
        raise ValueError(f"No se pudo extraer sector de {filename}")

# --------- 3. Generar el dataset de pares y etiquetar ---------

def build_pairwise_dataset(mapping, offers, label_threshold=0.5):
    all_pairs = []
    for cv_id, sector_scores in mapping.items():
        for idx, offer in offers.iterrows():
            sector = offer["sector_oferta"]
            score = sector_scores.get(sector, 0.0)
            label_bin = int(score >= label_threshold)
            offer_info = offer.to_dict()
            offer_id = offer_info.pop("offer_id")
            # Construir el par CV-Oferta
            all_pairs.append({
                "cv_id": cv_id,
                "offer_id": offer_id,
                "sector_oferta": sector,
                "score": score,
                "label_binario": label_bin,
                **offer_info
            })
    df_pairs = pd.DataFrame(all_pairs)
    return df_pairs

# --------- 4. Rankear las ofertas para cada CV ---------

def add_ranking(df_pairs, score_col="score", group_col="cv_id"):
    df_pairs = df_pairs.copy()
    def sort_and_rank(subdf):
        # Orden descendente por score, aleatorizar empates
        subdf = subdf.sample(frac=1, random_state=42).sort_values(score_col, ascending=False)
        subdf["rank"] = range(1, len(subdf)+1)
        return subdf
    df_pairs = df_pairs.groupby(group_col, group_keys=False).apply(sort_and_rank)
    return df_pairs

# --------- 5. Guardar el dataset final ---------

def save_dataset(df, output_file="data/interim/dataset_ranking_test.csv"):
    # Solo conservar las columnas deseadas
    columnas_finales = [
        "cv_id", "offer_id", "sector_oferta", "score", "label_binario", "rank"
    ]
    df[columnas_finales].to_csv(output_file, index=False)

# --------- MAIN ---------

def main():
    # Ajusta la ruta si lo necesitas
    mapping_file = "data/raw/cvs_test/cv_sector.txt"
    offers_folder = "data/interim"
    if not os.path.exists(offers_folder):
        raise FileNotFoundError(f"No se encontró la carpeta de ofertas: {offers_folder}")
    mapping = parse_cv_sector_mapping(mapping_file)
    offers = read_offers(offers_folder)
    df_pairs = build_pairwise_dataset(mapping, offers, label_threshold=0.5)
    df_pairs_ranked = add_ranking(df_pairs)
    save_dataset(df_pairs_ranked)
    print(f"¡Dataset generado con {len(df_pairs_ranked)} pares!")

if __name__ == "__main__":
    main()
