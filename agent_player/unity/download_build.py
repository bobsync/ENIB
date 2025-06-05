import gdown
import zipfile
import os

# ID o URL del file (usa direttamente il link condiviso)
file_url = "https://drive.google.com/uc?id=1CaclVAiPZHaP_eh02aeJ0PYaUytB55ol"

zip_path = "agent_player/unity/build_unity.zip"
estrazione_path = "agent_player/unity/"

# Scarica lo ZIP
print("Scaricamento ZIP...")
gdown.download(file_url, zip_path, quiet=False)

# Estrai
print("Estrazione ZIP...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(estrazione_path)

os.remove(zip_path)

print("Completato.")
