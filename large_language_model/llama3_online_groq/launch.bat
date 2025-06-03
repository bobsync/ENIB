@echo off
TITLE Large Language Model : Llama3 online Groq
if not defined ACA_PYTHON_ENV_PATH (
    echo Environment variable ACA_ENV_PATH is not defined.
    exit /b 1
)
%ACA_PYTHON_ENV_PATH%/Scripts/python module_process.py
exit