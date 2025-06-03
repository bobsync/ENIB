# Crea ambiente virtuale se non esiste
if (!(Test-Path -Path "venv")) {
    Write-Host "Creo ambiente virtuale..."
    python -m venv venv
}

# Attiva ambiente virtuale
Write-Host "Attivo ambiente virtuale..."
. .\venv\Scripts\Activate.ps1

# Chiedi se installare i requirements
$installReq = Read-Host -Prompt "Vuoi installare le dipendenze da requirements.txt? (s/n)"
if ($installReq -eq "s") {
    Write-Host "Installo dipendenze..."
    pip install -r requirements.txt
} else {
    Write-Host "Installazione delle dipendenze saltata."
}

# Chiedi se aggiornare la OPENAI_API_KEY
$updateOpenAI = Read-Host -Prompt "Vuoi aggiornare la OPENAI_API_KEY? (s/n)"
if ($updateOpenAI -eq "s") {
    $openaiKey = Read-Host -Prompt "Inserisci la tua OPENAI_API_KEY"
    [System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $openaiKey, "User")
    Write-Host "OPENAI_API_KEY aggiornata."
} else {
    Write-Host "OPENAI_API_KEY lasciata invariata."
}

# Chiedi se aggiornare la GROQ_API_KEY
$updateGroq = Read-Host -Prompt "Vuoi aggiornare la GROQ_API_KEY? (s/n)"
if ($updateGroq -eq "s") {
    $groqKey = Read-Host -Prompt "Inserisci la tua GROQ_API_KEY"
    [System.Environment]::SetEnvironmentVariable("GROQ_API_KEY", $groqKey, "User")
    Write-Host "GROQ_API_KEY aggiornata."
} else {
    Write-Host "GROQ_API_KEY lasciata invariata."
}

# Imposta ACA_PYTHON_ENV_PATH automaticamente
$scriptDir = Get-Location
$venvPythonPath = Join-Path $scriptDir "venv"

if (Test-Path $venvPythonPath) {
    [System.Environment]::SetEnvironmentVariable("ACA_PYTHON_ENV_PATH", $venvPythonPath, "User")
    Write-Host "ACA_PYTHON_ENV_PATH impostata a $venvPythonPath"
} else {
    Write-Warning "Impossibile trovare python.exe in venv\Scripts"
}

Write-Host "Setup completato con successo!"
Write-Host "Riavvia il terminale per rendere effettive le variabili di ambiente."
