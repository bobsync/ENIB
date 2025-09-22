import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === 1. Importa il file excel ===
merged_df = pd.read_excel("decider/qualtrics/output_bfi_all.xlsx")

# === 2. Seleziona solo i punteggi Big Five ===
bfi_cols = ["openness", "conscientiousness", "extroversion", "agreeableness", "neuroticism"]  # ordine OCEAN
df_bfi = merged_df[bfi_cols].copy()
df_bfi.index = merged_df["Q36"]  # Usa Q36 come ID dei partecipanti

# === 3. Calcola i valori medi del gruppo ===
df_mean = df_bfi.mean(axis=0)

# === 4. Imposta angoli per gli assi ===
labels = ["O", "C", "E", "A", "N"]
num_vars = len(labels)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]

# === 5. Colori per i partecipanti ===
colors = plt.colormaps.get_cmap("Dark2")

# === 6. Imposta griglia rettangolare fissa ===
rows, cols = 2, 5  # 5 colonne, 4 righe
fig_width, fig_height = 16, 9
fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height), subplot_kw=dict(polar=True))
fig.suptitle("Confronto dei Profili di Personalità (Big Five)", fontsize=28, y=1.03)

axes = axes.flatten()

# === 7. Plot dei partecipanti ===
for i, participant in enumerate(df_bfi.index):
    ax = axes[i]

    # Media del gruppo
    values_mean = df_mean.tolist()
    values_mean += values_mean[:1]
    ax.plot(angles, values_mean, color="gray", linestyle="dashed", linewidth=2, label="Media del Gruppo")
    ax.fill(angles, values_mean, color="gray", alpha=0.1)

    # Dati partecipante
    values_participant = df_bfi.loc[participant].tolist()
    values_participant += values_participant[:1]
    ax.plot(angles, values_participant, color=colors(i), linewidth=2)
    ax.fill(angles, values_participant, color=colors(i), alpha=0.4)

    # Etichette assi e titolo
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylim(0, 7)
    ax.set_title(f"{participant}", size=14, pad=25)

# Nascondi subplot vuoti
for j in range(len(df_bfi.index), len(axes)):
    fig.delaxes(axes[j])

# Legenda unica
handles, labels_leg = ax.get_legend_handles_labels()
fig.legend(handles, labels_leg, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.02), fontsize="large")

# Padding tra subplot
fig.subplots_adjust(wspace=0.5, hspace=0.6)

# Salva immagine a risoluzione minore
fig.savefig("decider/qualtrics/out/bfi_profiles.png", dpi=150, bbox_inches="tight")