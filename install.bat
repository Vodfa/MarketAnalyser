@echo off
echo ============================================================
echo Market Analyzer - Script de Instalacao
echo ============================================================
echo.

REM Verifica se Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.8+ de https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version
echo.

REM Atualiza pip, setuptools e wheel primeiro
echo [1/3] Atualizando pip, setuptools e wheel...
python -m pip install --upgrade pip setuptools wheel

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao atualizar pip/setuptools/wheel!
    pause
    exit /b 1
)

echo.
echo [2/3] Instalando dependencias principais...
python -m pip install pandas numpy requests python-dateutil cryptography ccxt

if %errorlevel% neq 0 (
    echo.
    echo [AVISO] Algumas dependencias falharam, continuando...
)

echo.
echo [3/3] Instalando PyQt5 (pode demorar)...
python -m pip install PyQt5 PyQtWebEngine

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao instalar PyQt5!
    echo.
    echo Tente instalar manualmente:
    echo   python -m pip install PyQt5
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Instalacao concluida com sucesso!
echo ============================================================
echo.
echo Para executar o programa:
echo   python gui_main.py
echo.
echo Ou simplesmente execute:
echo   run.bat
echo.
echo Para compilar para .exe:
echo   python build.py
echo.
pause
