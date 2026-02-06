@echo off
echo ============================================================
echo Market Analyzer - Build para EXE
echo ============================================================
echo.

REM Verifica se Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Executa script de build
echo Iniciando compilacao...
echo.
python build.py

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha na compilacao!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Build concluido!
echo ============================================================
echo.
echo O executavel esta em: dist\MarketAnalyzer.exe
echo.
pause
