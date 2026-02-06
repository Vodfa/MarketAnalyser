"""
Build Script for Market Analyzer
Compila o programa para executável .exe
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_exe():
    """Compila o programa usando PyInstaller"""
    
    print("=" * 60)
    print("Market Analyzer - Build Script")
    print("=" * 60)
    
    # Verifica se PyInstaller está instalado
    try:
        import PyInstaller
        print("✓ PyInstaller encontrado")
    except ImportError:
        print("✗ PyInstaller não encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller instalado")
    
    # Diretório atual
    current_dir = Path(__file__).parent
    
    # Nome do executável
    exe_name = "MarketAnalyzer"
    
    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--name", exe_name,
        "--onefile",
        "--windowed",
        "--icon=icon.ico" if os.path.exists("icon.ico") else "",
        "--add-data", "README.md;.",
        "--hidden-import", "PyQt5",
        "--hidden-import", "PyQt5.QtWebEngineWidgets",
        "--hidden-import", "ccxt",
        "--hidden-import", "talib",
        "--hidden-import", "pandas",
        "--hidden-import", "numpy",
        "--hidden-import", "cryptography",
        "--collect-all", "ccxt",
        "--collect-all", "talib",
        "gui_main.py"
    ]
    
    # Remove strings vazias
    cmd = [c for c in cmd if c]
    
    print("\nIniciando compilação...")
    print(f"Comando: {' '.join(cmd)}\n")
    
    try:
        # Executa PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        
        print("\n" + "=" * 60)
        print("✓ Compilação concluída com sucesso!")
        print("=" * 60)
        
        # Localização do executável
        dist_dir = current_dir / "dist"
        exe_path = dist_dir / f"{exe_name}.exe"
        
        if exe_path.exists():
            print(f"\nExecutável criado em: {exe_path}")
            print(f"Tamanho: {exe_path.stat().st_size / (1024*1024):.2f} MB")
        else:
            print("\n⚠ Executável não encontrado no diretório esperado")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("✗ Erro durante a compilação!")
        print("=" * 60)
        print(e.stderr)
        return False

def create_icon():
    """Cria um ícone simples para o programa"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Cria imagem 256x256
        img = Image.new('RGB', (256, 256), color='#2196F3')
        draw = ImageDraw.Draw(img)
        
        # Desenha "MA"
        try:
            font = ImageFont.truetype("arial.ttf", 120)
        except:
            font = ImageFont.load_default()
        
        draw.text((128, 128), "MA", fill='white', anchor='mm', font=font)
        
        # Salva como .ico
        img.save('icon.ico', format='ICO')
        print("✓ Ícone criado")
        
    except Exception as e:
        print(f"⚠ Não foi possível criar ícone: {e}")

def clean_build_files():
    """Remove arquivos temporários de build"""
    print("\nLimpando arquivos temporários...")
    
    dirs_to_remove = ['build', '__pycache__']
    files_to_remove = ['*.spec']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ Removido: {dir_name}/")
    
    import glob
    for pattern in files_to_remove:
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"✓ Removido: {file}")

def main():
    """Função principal"""
    print("\n1. Criando ícone...")
    create_icon()
    
    print("\n2. Compilando programa...")
    success = build_exe()
    
    if success:
        print("\n3. Limpando arquivos temporários...")
        clean_build_files()
        
        print("\n" + "=" * 60)
        print("BUILD CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print("\nO executável está em: dist/MarketAnalyzer.exe")
        print("\nVocê pode distribuir este arquivo.")
    else:
        print("\n" + "=" * 60)
        print("BUILD FALHOU!")
        print("=" * 60)
        print("\nVerifique os erros acima e tente novamente.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
