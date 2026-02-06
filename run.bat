@echo off
echo ============================================================
echo Market Analyzer - Iniciando...
echo ============================================================
echo.

python gui_main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao executar o programa!
    echo.
    echo Certifique-se de que as dependencias estao instaladas:
    echo   install.bat
    echo.
    pause
    exit /b 1
)
