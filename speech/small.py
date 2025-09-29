import os
import subprocess
import sys
import shutil
from huggingface_hub import snapshot_download

# --- Settings ---
model = "whisper-small"
quantization = "int8"

# --- Paths ---
base_dir = os.path.join("speech", "realtime_whisper", "models")
hf_model_dir = os.path.join(base_dir, model)
ct_model_dir = os.path.join(base_dir, f"{model}-{quantization}")

# --- Ensure base directory exists ---
os.makedirs(base_dir, exist_ok=True)

# --- Skip if already exists ---
if os.path.exists(ct_model_dir) and os.listdir(ct_model_dir):
    print(f"✅ Model already exists at: {ct_model_dir}")
    sys.exit(0)

print(f"🚀 Downloading and converting {model} with quantization={quantization}")

# --- 1. Download from HF ---
try:
    print("\n1/3 - Downloading Hugging Face model...")
    snapshot_download(
        repo_id=f"openai/{model}",
        local_dir=hf_model_dir,
        local_dir_use_symlinks=False
    )
    print(f"✅ Download complete: {hf_model_dir}")
except Exception as e:
    print(f"❌ Error downloading model: {e}")
    sys.exit(1)

# --- 2. Convert to CTranslate2 ---
try:
    print("\n2/3 - Converting to CTranslate2...")
    cmd = [
        sys.executable,
        "-m", "ctranslate2.converters.transformers",
        "--model", hf_model_dir,
        "--output_dir", ct_model_dir,
        "--quantization", quantization,
        "--force"
    ]
    process = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print(f"✅ Conversion complete: {ct_model_dir}")
except subprocess.CalledProcessError as e:
    print("❌ Conversion failed")
    print("STDOUT:", e.stdout)
    print("STDERR:", e.stderr)
    sys.exit(1)

# --- 3. Cleanup ---
try:
    print("\n3/3 - Cleaning up...")
    if os.path.exists(hf_model_dir):
        shutil.rmtree(hf_model_dir)
        print(f"✅ Removed temporary folder: {hf_model_dir}")
except Exception as e:
    print(f"⚠️ Cleanup failed: {e}")

print("\n✨ All done! Model ready at:", ct_model_dir)
