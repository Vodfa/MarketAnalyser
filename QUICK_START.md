# 🚀 Guia de Início Rápido - Market Analyzer

## ⚡ Instalação Rápida (5 minutos)

### Passo 1: Verifique o Python
```bash
python --version
```
- Deve mostrar Python 3.8 ou superior
- Se não funcionar, instale de https://www.python.org/

### Passo 2: Atualize ferramentas base
```bash
python -m pip install --upgrade pip setuptools wheel
```
⚠️ **IMPORTANTE**: Execute este comando ANTES de instalar as dependências!

### Passo 3: Instale dependências
```bash
install.bat
```
Ou manualmente:
```bash
python -m pip install -r requirements.txt
```

### Passo 4: Execute o programa
```bash
run.bat
```
Ou:
```bash
python gui_main.py
```

---

## 🔧 Se der erro na instalação

### Erro: "Cannot import setuptools"
```bash
python -m pip install --upgrade setuptools wheel
```

### Erro no PyQt5
```bash
python -m pip install PyQt5==5.15.11 PyQtWebEngine==5.15.7
```

### Outros erros
Consulte: `TROUBLESHOOTING.md`

---

## 📱 Primeiro Uso

1. **Abra o programa**
   - Execute `run.bat` ou `python gui_main.py`

2. **Configure a Exchange**
   - Vá para aba "Configurações"
   - Selecione "Binance" (padrão)
   - Clique em "Salvar Configurações"

3. **Faça sua primeira análise**
   - Vá para aba "Análise"
   - Selecione "BTC/USDT"
   - Escolha timeframe "5m"
   - Clique em "Analisar"

4. **Veja o resultado**
   - Direção: UP, DOWN ou SIDEWAYS
   - Confiança: Percentual de certeza
   - Detalhes: Sinais dos indicadores

---

## 🎯 Funcionalidades Principais

### 📊 Análise de Mercado
- 15+ indicadores técnicos
- Previsão de direção
- Análise automática

### 🔧 Configurações
- 10+ exchanges suportadas
- API keys criptografadas
- Mercados favoritos

### 🤖 Trading Automático
- Bot com sinais automáticos
- Stop Loss / Take Profit
- Histórico de trades

### 🌐 Navegador
- Acesso direto a TradingView
- Navegação completa
- Atalhos rápidos

### ⏰ Limite de Tempo
- Duração máxima
- Horário específico
- Período diário

---

## 🏗️ Compilar para .exe

### Método Rápido
```bash
build.bat
```

### Método Manual
```bash
python -m pip install pyinstaller
python build.py
```

O executável estará em: `dist\MarketAnalyzer.exe`

---

## ⚠️ Avisos Importantes

1. **Trading envolve risco** - Pode perder dinheiro
2. **Não é conselho financeiro** - Apenas ferramenta
3. **Teste antes** - Use modo simulação
4. **API Keys** - Nunca compartilhe
5. **Responsabilidade** - Suas decisões, sua responsabilidade

---

## 📚 Documentação Completa

- `README.md` - Documentação completa
- `BUILD_GUIDE.md` - Guia de compilação
- `TROUBLESHOOTING.md` - Solução de problemas
- `CHANGELOG.md` - Histórico de versões

---

## 🧪 Teste de Funcionamento

Execute:
```bash
python test_analyzer.py
```

Deve mostrar:
```
✓ Data Provider: PASSOU
✓ Market Analyzer: PASSOU
✓ Config Manager: PASSOU

Total: 3/3 testes passaram
```

---

## 🆘 Precisa de Ajuda?

1. Consulte `TROUBLESHOOTING.md`
2. Execute `python test_analyzer.py` para diagnóstico
3. Verifique logs em `~/.market_analyzer/`

---

## ✅ Checklist

- [ ] Python instalado
- [ ] pip, setuptools, wheel atualizados
- [ ] Dependências instaladas
- [ ] Programa executa sem erros
- [ ] Testes passam (test_analyzer.py)

---

**Pronto para começar!** 🎉

Execute `run.bat` e boa sorte com suas análises!
