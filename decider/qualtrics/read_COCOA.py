import pandas as pd
import glob
import os
import warnings

# === Ignora warning di openpyxl ===
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# === 1. Leggi tutti i file Excel nella cartella "pre" ===
input_folder = "decider/qualtrics/pre"
output_file = "decider/qualtrics/out/output_bfi_all.xlsx"

all_data = []

for file_path in glob.glob(os.path.join(input_folder, "*.xlsx")):
    print(f"Elaboro: {file_path}")
    df = pd.read_excel(file_path)

    # === 2. Filtra le colonne che iniziano con "Q29" ===
    bfi_df = df.filter(regex="^Q29")

    # === 2a. Estrai le descrizioni dalla prima riga ===
    descriptions = bfi_df.iloc[0]  # prima riga = testo delle domande
    bfi_df = bfi_df.iloc[1:]       # rimuovi la prima riga (solo dati da qui in avanti)

    # 🔹 Rimuovi righe completamente vuote
    bfi_df = bfi_df.dropna(how="all").reset_index(drop=True)
    df = df.iloc[1:].dropna(how="all").reset_index(drop=True)

    # === 3. Mappa testo → punteggio Likert (1–7) ===
    likert_scale = {
        "strongly disagree": 1,
        "disagree": 2,
        "somewhat disagree": 3,
        "neither agree nor disagree": 4,
        "somewhat agree": 5,
        "agree": 6,
        "strongly agree": 7
    }

    bfi_df_mapped = bfi_df.map(lambda x: likert_scale.get(str(x).strip().lower(), None))

    # === 5. Reverse Scoring (7-point Likert → 8 - x) ===
    reverse_items = [3, 6, 10, 14]  # 1-based item numbers
    for i in reverse_items:
        col_name = f"Q29_{i}"
        if col_name in bfi_df_mapped.columns:
            bfi_df_mapped[col_name] = bfi_df_mapped[col_name].apply(
                lambda x: 8 - x if pd.notna(x) else x
            )

    # === 6. Calcolo dei tratti BFI ===
    traits = {
        "neuroticism":        [1, 2, 3],
        "extroversion":       [4, 5, 6],
        "openness":           [7, 8, 9],
        "agreeableness":      [10, 11, 12],
        "conscientiousness":  [13, 14, 15],
    }

    bfi_scores = pd.DataFrame(index=bfi_df_mapped.index)
    for trait, indices in traits.items():
        cols = [f"Q29_{i}" for i in indices if f"Q29_{i}" in bfi_df_mapped.columns]
        bfi_scores[trait] = bfi_df_mapped[cols].mean(axis=1).round(1)

    # === 7. Aggiungi i punteggi ai dati originali ===
    final_df = pd.concat([df.reset_index(drop=True), bfi_scores.reset_index(drop=True)], axis=1)
    all_data.append(final_df)

# === 8. Unisci tutti i file in un unico DataFrame ===
merged_df = pd.concat(all_data, ignore_index=True)

# === 9. Elimina i duplicati e ordina in base a Q36 ===
if "Q36" in merged_df.columns:
    merged_df = merged_df.drop_duplicates(subset="Q36", keep="first")
    merged_df = merged_df.sort_values(by="Q36").reset_index(drop=True)

# === 10. Salvataggio finale ===
merged_df.to_excel(output_file, index=False)
print(f"✅ File unico salvato in: {output_file}")
