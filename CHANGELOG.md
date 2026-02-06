# Changelog

## [1.0.2] - 2026-02-05 (CORREÇÃO FINAL)

### 🐛 Correções
- **CRÍTICO**: Corrigido erro `TypeError: setUrl() argument 1 has unexpected type 'str'`
- Adicionado import de `QUrl` do PyQt5.QtCore
- Todas as chamadas `setUrl()` agora usam `QUrl()` corretamente
- Navegador embutido agora funciona perfeitamente

### 📝 Arquivos Modificados
- `gui_main.py`: Corrigido uso de QUrl em 5 locais

---

## [1.0.1] - 2026-02-05 (CORREÇÃO)

### 🐛 Correções
- Corrigido erro `Cannot import 'setuptools.build_meta'` no Python 3.13
- Atualizado `requirements.txt` com versões compatíveis
- Melhorado script `install.bat` para instalar setuptools primeiro

### ✨ Novos Arquivos
- `TROUBLESHOOTING.md` - Guia completo de solução de problemas
- `QUICK_START.md` - Guia de início rápido
- `install_simple.bat` - Instalação simplificada passo-a-passo

### 📦 Dependências Atualizadas
- setuptools>=75.0.0 (NOVO)
- wheel>=0.45.0 (NOVO)
- PyQt5>=5.15.11 (era 5.15.10)
- pandas>=2.2.0 (era 2.0.3)
- numpy>=1.26.0 (era 1.24.3)
- ccxt>=4.4.0 (era 4.2.25)
- cryptography>=43.0.0 (era 41.0.7)

---

## [1.0.0] - 2026-02-05 (LANÇAMENTO INICIAL)

### ✨ Funcionalidades Principais

#### 📊 Análise de Mercado
- Análise técnica avançada baseada no Freqtrade
- 15+ indicadores técnicos implementados
- Previsão de direção (UP/DOWN/SIDEWAYS)
- Nível de confiança percentual
- Análise automática com intervalo configurável
- Suporte a múltiplos timeframes (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)

#### 🔧 Configurações
- Suporte a 10+ exchanges (Binance, Coinbase, Kraken, etc.)
- Gerenciamento seguro de API Keys (criptografia AES)
- Sistema de mercados favoritos
- Configurações persistentes
- Importação/exportação de configurações

#### 🤖 Trading Automático
- Bot de trading com sinais automáticos
- Stop Loss e Take Profit configuráveis
- Gerenciamento de múltiplos trades simultâneos
- Histórico completo de operações
- Estatísticas de performance

#### 🌐 Navegador Embutido
- Navegador web completo integrado
- Acesso rápido a TradingView, Binance, Coinbase
- Navegação completa (voltar, avançar, atualizar)
- URLs personalizadas

#### ⏰ Limite de Tempo Sofisticado
- **Duração**: Define tempo máximo de execução
- **Horário Específico**: Para em data/hora exata
- **Período Diário**: Funciona apenas em horários específicos
- Desligamento automático ao atingir limite
- Display de tempo em tempo real

### 🔒 Segurança
- Criptografia de credenciais (Fernet/AES)
- Armazenamento local seguro
- Sem telemetria ou envio de dados
- Código-fonte aberto

### 📈 Indicadores Técnicos
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- EMA (Exponential Moving Average) - 9, 21, 50, 200
- SMA (Simple Moving Average) - 20, 50, 200
- ADX (Average Directional Index)
- MFI (Money Flow Index)
- Stochastic Oscillator
- Parabolic SAR
- TEMA (Triple Exponential Moving Average)
- ATR (Average True Range)
- NATR (Normalized ATR)
- OBV (On Balance Volume)
- A/D Line (Accumulation/Distribution)

### 🎨 Interface
- Interface gráfica moderna com PyQt5
- 5 abas organizadas
- Tema profissional
- Logs em tempo real
- Indicadores visuais de status

### 🧪 Testes
- Suite de testes automatizados
- Testes de integração
- Validação de indicadores
- Verificação de criptografia

### 📦 Distribuição
- Código-fonte completo
- Scripts de instalação automática (Windows)
- Scripts de compilação para .exe
- Documentação completa
- Guia de build detalhado

---

## Notas de Versão

### Tecnologias Utilizadas
- Python 3.8+
- PyQt5 (Interface)
- CCXT (Conexão com exchanges)
- Pandas/Numpy (Análise de dados)
- Cryptography (Segurança)

### Baseado em
- Freqtrade (estratégias e indicadores)
- CCXT (conectividade)

### Compatibilidade
- Windows 10/11 (testado)
- Windows 7/8 (deve funcionar)
- Linux (código-fonte)
- macOS (código-fonte)
- Python 3.8 - 3.13

---

**Versão Atual**: 1.0.2
**Status**: Estável ✅
**Data**: 05 de Fevereiro de 2026
