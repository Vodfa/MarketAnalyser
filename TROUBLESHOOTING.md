# Guia de Solução de Problemas - Market Analyzer

## 🔴 Erro: "Cannot import 'setuptools.build_meta'"

### Causa
Este erro ocorre quando o setuptools não está instalado ou está desatualizado, especialmente no Python 3.13.

### Solução Rápida
```bash
# Abra CMD como Administrador e execute:
python -m pip install --upgrade pip setuptools wheel
```

Depois execute novamente:
```bash
install.bat
```

---

## 🔴 Erro ao instalar PyQt5

### Solução 1: Instalar versão específica
```bash
python -m pip install PyQt5==5.15.11 PyQtWebEngine==5.15.7
```

### Solução 2: Usar wheel pré-compilado
1. Visite: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt5
2. Baixe o arquivo .whl correspondente à sua versão do Python
3. Instale: `python -m pip install caminho\para\arquivo.whl`

---

## 🔴 Python não encontrado

### Solução
1. Reinstale Python de https://www.python.org/
2. **IMPORTANTE**: Marque "Add Python to PATH" durante instalação
3. Reinicie o computador
4. Teste: `python --version` no CMD

---

## 🔴 Erro: "pip não é reconhecido"

### Solução
```bash
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

---

## 🔴 Instalação muito lenta

### Causa
PyQt5 é um pacote grande (~100MB) e pode demorar.

### Solução
- Seja paciente (pode levar 5-10 minutos)
- Use `install_simple.bat` que mostra progresso
- Verifique sua conexão de internet

---

## 🔴 Erro de permissão

### Solução Windows
Execute o CMD como Administrador:
1. Pressione Win + X
2. Escolha "Prompt de Comando (Admin)" ou "Windows PowerShell (Admin)"
3. Navegue até a pasta do programa
4. Execute `install.bat`

---

## 🔴 Conflito de versões

### Solução: Ambiente Virtual
```bash
# Crie um ambiente virtual limpo
python -m venv venv

# Ative o ambiente
venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute o programa
python gui_main.py
```

---

## 🔴 Programa não inicia

### Diagnóstico
```bash
# Execute com modo verbose para ver erros
python gui_main.py
```

### Verificações
1. Todas as dependências instaladas?
   ```bash
   python -c "import PyQt5, pandas, ccxt, cryptography"
   ```

2. Versão do Python compatível?
   ```bash
   python --version
   # Deve ser 3.8 ou superior
   ```

---

## 🔴 Erro ao conectar com exchange

### Soluções
1. Verifique sua conexão com internet
2. Tente outra exchange (ex: Binance → Coinbase)
3. Verifique se a exchange está online
4. Se usar API keys, verifique se estão corretas

---

## 🔴 Erro de importação

### Exemplo
```
ImportError: cannot import name 'X' from 'Y'
```

### Solução
```bash
# Reinstale o pacote problemático
python -m pip uninstall -y nome_do_pacote
python -m pip install nome_do_pacote
```

---

## 🔴 Antivírus bloqueia instalação

### Solução
1. Adicione exceção para a pasta do programa
2. Temporariamente desative o antivírus durante instalação
3. Use Windows Defender (geralmente não bloqueia)

---

## 🔴 Erro ao compilar para .exe

### Solução 1: Instale PyInstaller
```bash
python -m pip install pyinstaller
```

### Solução 2: Use modo console para debug
```bash
pyinstaller --onefile --console gui_main.py
```

### Solução 3: Limpe cache
```bash
# Delete as pastas:
rmdir /s /q build
rmdir /s /q dist
del *.spec

# Tente novamente
python build.py
```

---

## 🔴 Executável não funciona

### Diagnóstico
1. Compile com `--console` para ver erros
2. Verifique se o programa funciona sem compilar:
   ```bash
   python gui_main.py
   ```
3. Verifique antivírus/firewall

---

## 📋 Checklist de Instalação

Marque cada item conforme completa:

- [ ] Python 3.8+ instalado
- [ ] Python adicionado ao PATH
- [ ] CMD abre e reconhece `python`
- [ ] pip atualizado (`python -m pip install --upgrade pip`)
- [ ] setuptools instalado (`python -m pip install setuptools`)
- [ ] Todas as dependências instaladas
- [ ] Programa executa sem erros

---

## 🆘 Ainda com problemas?

### Opção 1: Instalação Manual
```bash
# Instale cada pacote individualmente
python -m pip install setuptools wheel
python -m pip install numpy
python -m pip install pandas
python -m pip install ccxt
python -m pip install cryptography
python -m pip install requests
python -m pip install python-dateutil
python -m pip install PyQt5
python -m pip install PyQtWebEngine
```

### Opção 2: Use Python mais antigo
Se você tem Python 3.13 e está com problemas, tente:
- Python 3.11 (mais estável)
- Python 3.10 (muito estável)

Baixe em: https://www.python.org/downloads/

### Opção 3: Ambiente Virtual
```bash
# Crie ambiente limpo
python -m venv market_env
market_env\Scripts\activate
pip install -r requirements.txt
python gui_main.py
```

---

## 📞 Informações Úteis

### Verificar instalação
```bash
# Liste pacotes instalados
python -m pip list

# Verifique versões
python -m pip show PyQt5
python -m pip show pandas
python -m pip show ccxt
```

### Logs do programa
- Windows: `C:\Users\SeuUsuario\.market_analyzer\`
- Arquivo de log: `market_analyzer.log`

### Reinstalação completa
```bash
# Desinstale tudo
python -m pip uninstall -y PyQt5 PyQtWebEngine pandas numpy ccxt cryptography requests python-dateutil

# Reinstale
install.bat
```

---

## ✅ Teste Final

Execute este comando para verificar se tudo está OK:
```bash
python test_analyzer.py
```

Se todos os 3 testes passarem, o programa está pronto para uso! 🎉

---

**Última atualização**: 05/02/2026
