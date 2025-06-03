@echo off

if not defined ACA_PYTHON_ENV_PATH (
    echo Environment variable ACA_ENV_PATH is not defined.
    exit /b 1
)

start whiteboard\x64\Debug\WhiteBoard.exe
start %ACA_PYTHON_ENV_PATH%/Scripts/python gui/graphical_user_interface.py
start %ACA_PYTHON_ENV_PATH%/Scripts/python modules_handler/modules_handler.py