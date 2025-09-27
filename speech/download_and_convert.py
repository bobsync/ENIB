import os
import subprocess
import sys
import shutil
from huggingface_hub import snapshot_download

# --- Impostazioni ---
# Modifica qui il tipo di quantizzazione che desideri: "float16", "int8_float16", "int8"
quantization = "float32"
model = "whisper-large-v3-turbo"

# --- Percorsi ---
# I percorsi vengono definiti in modo dinamico
base_dir = os.path.join("speech", "realtime_whisper", "models")
hf_model_dir = os.path.join(base_dir, model)
ct_model_dir = os.path.join(base_dir, f"whisper_small_en_ct_{quantization}")

# --- Logica Principale ---

# 1. Crea la cartella base dei modelli se non esiste
os.makedirs(base_dir, exist_ok=True)

# 2. Controlla se il modello convertito esiste già
if os.path.exists(ct_model_dir) and os.listdir(ct_model_dir):
    print(f"✅ Modello già convertito e presente in: {ct_model_dir}")
    print("Nessuna operazione necessaria.")
    sys.exit(0)

# 3. Se il modello non esiste, avvia il processo completo
print(f"Modello convertito con quantizzazione '{quantization}' non trovato.")
print("🚀 Avvio del processo automatico di scaricamento e conversione...")

# --- Download ---
try:
    print(f"\n1/3 - Download del modello da Hugging Face...")
    snapshot_download(
        repo_id="openai/whisper-large-v3-turbo",
        local_dir=hf_model_dir,
        local_dir_use_symlinks=False
    )
    print(f"Modello scaricato in: {hf_model_dir}")
except Exception as e:
    print(f"❌ Errore durante il download: {e}")
    sys.exit(1)

# --- Conversione ---
try:
    print(f"\n2/3 - Conversione del modello in formato CTranslate2 ({quantization})...")
    cmd = [
        sys.executable,
        "-m", "ctranslate2.converters.transformers",
        "--model", hf_model_dir,
        "--output_dir", ct_model_dir,
        "--quantization", quantization,
        "--force"  # Forza la conversione anche se la cartella di output esiste (ma è vuota)
    ]
    # Usiamo subprocess.PIPE per catturare l'output in modo più pulito
    process = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
    print(f"Conversione completata. Modello salvato in: {ct_model_dir}")
except subprocess.CalledProcessError as e:
    print("❌ Errore durante la conversione del modello.")
    print("\n--- Dettagli Errore ---")
    print("STDOUT:", e.stdout)
    print("STDERR:", e.stderr)
    print("----------------------")
    sys.exit(1)

# --- Pulizia ---
try:
    print("\n3/3 - Pulizia dei file intermedi...")
    if os.path.exists(hf_model_dir):
        shutil.rmtree(hf_model_dir)
        print(f"Cartella intermedia '{hf_model_dir}' eliminata con successo.")
except Exception as e:
    print(f"⚠️ Errore durante la pulizia della cartella intermedia: {e}")

print("\n✨ Processo completato con successo!")
sys.exit(0)