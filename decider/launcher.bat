@echo off
TITLE Decider : conversation gesture
if not defined ACA_PYTHON_ENV_PATH (
    echo Environment variable ACA_ENV_PATH is not defined.
    exit /b 1
)
%ACA_PYTHON_ENV_PATH%/Scripts/python decider_conversation_gesture.py
pause
exit