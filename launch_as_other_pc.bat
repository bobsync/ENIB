@echo off

if not defined ACA_PYTHON_ENV_PATH (
    echo Environment variable ACA_ENV_PATH is not defined.
    exit /b 1
)

start %ACA_PYTHON_ENV_PATH%/Scripts/python modules_handler/modules_handler.py