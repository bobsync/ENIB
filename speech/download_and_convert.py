import os
import subprocess
import sys
import shutil
from huggingface_hub import snapshot_download

# === Percorsi ===
base_dir = os.path.join("speech", "realtime_whisper", "models")
hf_model_dir = os.path.join(base_dir, "whisper-small.en-hf")
ct_model_dir = os.path.join(base_dir, "whisper_small_en_ct_32")
quantization = "float16"

# === 1. Controlla se la cartella 'speech/realtime_whisper/models/' esiste ed è vuota ===
if not os.path.exists(base_dir) or not os.listdir(base_dir):
    os.makedirs(base_dir, exist_ok=True)
    print("Cartella 'speech/realtime_whisper/models/' assente o vuota. Scaricamento e conversione del modello.")

    # Scarica
    try:
        snapshot_download(repo_id="openai/whisper-small.en", local_dir=hf_model_dir, local_dir_use_symlinks=False)
        print(f"Modello scaricato in: {hf_model_dir}")
    except Exception as e:
        print(f"Errore durante il download: {e}")
        sys.exit(1)

    # Converte
    print("Avvio conversione in formato CTranslate2...")
    cmd = [
        sys.executable,
        "-m", "ctranslate2.converters.transformers",
        "--model", hf_model_dir,
        "--output_dir", ct_model_dir,
        "--quantization", quantization
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Conversione completata. Modello convertito in: {ct_model_dir}")
    except subprocess.CalledProcessError as e:
        print("Errore nella conversione.")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)

    # Chiede se eliminare il modello Hugging Face
    while True:
        answer = input(f"\nVuoi eliminare la cartella scaricata da Hugging Face ({hf_model_dir})? [s/n]: ").strip().lower()
        if answer == "s":
            shutil.rmtree(hf_model_dir)
            print("Cartella eliminata.")
            break
        elif answer == "n":
            print("Cartella mantenuta.")
            break
        else:
            print("Risposta non valida. Scrivi 's' o 'n'.")
    sys.exit(0)

# === 2. La cartella 'speech/realtime_whisper/models/' esiste e contiene qualcosa ===
contents = os.listdir(base_dir)
has_hf = "whisper-small.en-hf" in contents and os.listdir(hf_model_dir)
has_ct = "whisper_small_en_ct_32" in contents and os.listdir(ct_model_dir)

if has_ct:
    print(f"Modello già convertito presente in: {ct_model_dir}")
    print("Nessuna operazione necessaria.")
    sys.exit(0)

if has_hf and not has_ct:
    print("Modello Hugging Face trovato. Procedo con la conversione.")
    cmd = [
        sys.executable,
        "-m", "ctranslate2.converters.transformers",
        "--model", hf_model_dir,
        "--output_dir", ct_model_dir,
        "--quantization", quantization
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Conversione completata. Modello convertito in: {ct_model_dir}")
    except subprocess.CalledProcessError as e:
        print("Errore nella conversione.")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)

    while True:
        answer = input(f"\nVuoi eliminare la cartella scaricata da Hugging Face ({hf_model_dir})? [s/n]: ").strip().lower()
        if answer == "s":
            shutil.rmtree(hf_model_dir)
            print("Cartella eliminata.")
            break
        elif answer == "n":
            print("Cartella mantenuta.")
            break
        else:
            print("Risposta non valida. Scrivi 's' o 'n'.")
    sys.exit(0)

# === 3. Caso anomalo: né hf né ct ===
print("La cartella 'speech/realtime_whisper/models/' contiene file, ma non i modelli attesi.")
print("Controlla il contenuto manualmente.")
sys.exit(1)
