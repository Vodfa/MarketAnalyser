# Guia de Compilação - Market Analyzer

## 📋 Pré-requisitos

### Windows
- Windows 10/11 (64-bit)
- Python 3.8 ou superior
- 4GB RAM mínimo
- 2GB espaço em disco

### Instalar Python
1. Baixe Python de https://www.python.org/downloads/
2. **IMPORTANTE**: Marque "Add Python to PATH" durante instalação
3. Verifique: abra CMD e digite `python --version`

## 🚀 Instalação Rápida

### Opção 1: Script Automático (Recomendado)
1. Extraia o arquivo ZIP
2. Execute `install.bat` (duplo clique)
3. Aguarde instalação das dependências
4. Execute `run.bat` para iniciar o programa

### Opção 2: Manual
```bash
# Abra CMD na pasta do programa
cd caminho\para\market_analyzer

# Instale dependências
pip install -r requirements.txt

# Execute o programa
python gui_main.py
```

## 🔨 Compilar para EXE

### Método 1: Script Automático
1. Execute `build.bat` (duplo clique)
2. Aguarde a compilação (pode demorar 5-10 minutos)
3. O executável estará em `dist\MarketAnalyzer.exe`

### Método 2: Manual
```bash
# Instale PyInstaller
pip install pyinstaller

# Execute build
python build.py
```

### Método 3: PyInstaller Direto
```bash
pyinstaller --name MarketAnalyzer ^
    --onefile ^
    --windowed ^
    --hidden-import PyQt5 ^
    --hidden-import PyQt5.QtWebEngineWidgets ^
    --hidden-import ccxt ^
    --hidden-import pandas ^
    --hidden-import numpy ^
    --hidden-import cryptography ^
    --collect-all ccxt ^
    gui_main.py
```

## 📦 Estrutura do Projeto

```
market_analyzer/
├── gui_main.py              # Interface gráfica principal
├── market_analysis.py       # Análise técnica e indicadores
├── data_provider.py         # Conexão com exchanges
├── config_manager.py        # Gerenciamento de configurações
├── trading_bot.py           # Bot de trading automático
├── requirements.txt         # Dependências Python
├── README.md               # Documentação do usuário
├── BUILD_GUIDE.md          # Este arquivo
├── install.bat             # Script de instalação (Windows)
├── build.bat               # Script de compilação (Windows)
├── run.bat                 # Script de execução (Windows)
├── build.py                # Script de build Python
└── test_analyzer.py        # Testes automatizados
```

## 🧪 Testar Antes de Compilar

```bash
# Execute os testes
python test_analyzer.py
```

Todos os testes devem passar antes de compilar.

## ⚠️ Problemas Comuns

### Erro: "Python não encontrado"
**Solução**: Reinstale Python e marque "Add to PATH"

### Erro: "pip não é reconhecido"
**Solução**: 
```bash
python -m pip install --upgrade pip
```

### Erro ao instalar PyQt5
**Solução**: Use versão específica
```bash
pip install PyQt5==5.15.10 PyQtWebEngine==5.15.6
```

### Erro: "Failed to execute script"
**Solução**: Compile com modo console para ver erros
```bash
pyinstaller --onefile --console gui_main.py
```

### Executável muito grande
**Solução**: Normal! Inclui Python + bibliotecas (100-200MB)

### Antivírus bloqueia executável
**Solução**: Adicione exceção ou compile com certificado digital

## 🔧 Opções Avançadas de Compilação

### Compilar com Console (Debug)
```bash
pyinstaller --onefile --console gui_main.py
```

### Compilar com Ícone Personalizado
```bash
pyinstaller --onefile --windowed --icon=icon.ico gui_main.py
```

### Reduzir Tamanho do Executável
```bash
pyinstaller --onefile --windowed --strip gui_main.py
```

### Compilar para Pasta (mais rápido)
```bash
pyinstaller --onedir --windowed gui_main.py
```

## 📊 Tamanhos Esperados

- **Código-fonte**: ~50KB
- **Dependências instaladas**: ~500MB
- **Executável final**: ~150-250MB (normal para PyInstaller)

## 🐛 Debug

### Ver logs de execução
1. Execute pelo CMD: `python gui_main.py`
2. Ou compile com `--console` para ver erros

### Logs do programa
- Windows: `C:\Users\SeuUsuario\.market_analyzer\`
- Arquivo: `market_analyzer.log`

## 📝 Notas

1. **Primeira compilação**: Pode demorar 10-15 minutos
2. **Compilações seguintes**: Mais rápidas (5 minutos)
3. **Antivírus**: Pode dar falso positivo, é normal
4. **Firewall**: Pode pedir permissão para internet
5. **Portabilidade**: O .exe funciona sem instalar Python

## 🆘 Suporte

Se encontrar problemas:
1. Verifique se todos os testes passam: `python test_analyzer.py`
2. Tente executar sem compilar: `python gui_main.py`
3. Verifique logs em `~/.market_analyzer/`
4. Reporte o erro com mensagem completa

## ✅ Checklist de Build

- [ ] Python 3.8+ instalado
- [ ] Todas as dependências instaladas
- [ ] Testes passando (test_analyzer.py)
- [ ] Programa executa normalmente (gui_main.py)
- [ ] PyInstaller instalado
- [ ] Build executado com sucesso
- [ ] Executável testado e funcionando

---

**Boa sorte com a compilação!** 🚀
