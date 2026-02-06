@echo off
echo ============================================================
echo Market Analyzer - Instalacao Simplificada
echo ============================================================
echo.
echo Este script instala apenas as dependencias essenciais
echo para executar o programa (sem PyQt5 para compilacao).
echo.

REM Verifica Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Atualiza ferramentas base
echo Atualizando pip...
python -m pip install --upgrade pip setuptools wheel --quiet

REM Instala dependencias uma por uma
echo.
echo Instalando dependencias (isso pode demorar alguns minutos)...
echo.

echo [1/6] Instalando numpy...
python -m pip install numpy --quiet

echo [2/6] Instalando pandas...
python -m pip install pandas --quiet

echo [3/6] Instalando ccxt...
python -m pip install ccxt --quiet

echo [4/6] Instalando cryptography...
python -m pip install cryptography --quiet

echo [5/6] Instalando requests...
python -m pip install requests python-dateutil --quiet

echo [6/6] Instalando PyQt5 (pode demorar)...
python -m pip install PyQt5 PyQtWebEngine

echo.
echo ============================================================
echo Instalacao concluida!
echo ============================================================
echo.
echo Execute: run.bat
echo.
pause
