Write-Host "Verifica delle variabili d'ambiente per Audrey..." -ForegroundColor Cyan

# Lista delle variabili da controllare
$vars = @(
    "OPENAI_API_KEY",
    "GROQ_API_KEY",
    "ACA_PYTHON_ENV_PATH"
)

foreach ($var in $vars) {
    $value = [System.Environment]::GetEnvironmentVariable($var, "User")
    if ([string]::IsNullOrEmpty($value)) {
        Write-Host "$var non è impostata." -ForegroundColor Red
    } else {
        Write-Host "${var}: $value" -ForegroundColor Green
    }
}
