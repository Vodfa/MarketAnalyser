# Market Analyzer - AI Trading Assistant

## 📊 Descrição

Market Analyzer é um programa avançado de análise de mercado financeiro baseado no **Freqtrade**, com interface gráfica moderna, navegador embutido para trades automáticos e sistema sofisticado de limite de tempo.

## ✨ Funcionalidades

### 🎯 Análise de Mercado
- **Análise Técnica Avançada**: Baseada nos indicadores do Freqtrade
- **Indicadores Implementados**:
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - EMA (Exponential Moving Average)
  - SMA (Simple Moving Average)
  - ADX (Average Directional Index)
  - MFI (Money Flow Index)
  - Stochastic Fast
  - SAR (Parabolic SAR)
  - TEMA (Triple Exponential Moving Average)
  - ATR (Average True Range)
  - OBV (On Balance Volume)

- **Previsão de Direção**: UP, DOWN ou SIDEWAYS
- **Nível de Confiança**: Percentual de confiança na previsão
- **Análise Automática**: Configure intervalos personalizados

### 🔧 Configurações
- **Múltiplas Exchanges Suportadas**:
  - Binance
  - Coinbase
  - Kraken
  - Bitfinex
  - Bybit
  - OKX
  - KuCoin
  - Huobi
  - Gate.io
  - MEXC

- **Gerenciamento Seguro de Credenciais**: API Keys criptografadas
- **Mercados Favoritos**: Salve seus pares preferidos
- **Múltiplos Timeframes**: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w

### 🤖 Trading Automático
- **Bot de Trading**: Executa trades baseado em sinais
- **Stop Loss e Take Profit**: Gerenciamento automático de risco
- **Múltiplos Trades Simultâneos**: Configure o número máximo
- **Histórico de Trades**: Acompanhe todas as operações

### 🌐 Navegador Embutido
- **Acesso Direto**: TradingView, Binance, Coinbase
- **Navegação Completa**: Voltar, avançar, atualizar
- **URLs Personalizadas**: Acesse qualquer site

### ⏰ Limite de Tempo Sofisticado
- **Duração**: Defina tempo máximo de execução (horas, minutos, segundos)
- **Horário Específico**: Pare em data/hora exata
- **Período Diário**: Funcione apenas em horários específicos
- **Desligamento Automático**: Encerra o programa quando o limite é atingido

## 🚀 Instalação

### Requisitos
- Windows 10/11 (64-bit)
- 4GB RAM mínimo
- Conexão com internet

### Opção 1: Executável (.exe)
1. Baixe o arquivo `MarketAnalyzer.exe`
2. Execute o programa
3. Configure suas preferências

### Opção 2: Código Fonte
1. Instale Python 3.8 ou superior
2. Instale TA-Lib:
   - Windows: Baixe wheel de https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
   - Linux: `sudo apt-get install ta-lib`
   - Mac: `brew install ta-lib`

3. Instale dependências:
```bash
pip install -r requirements.txt
```

4. Execute o programa:
```bash
python gui_main.py
```

## 📖 Como Usar

### 1. Configuração Inicial
1. Vá para a aba **Configurações**
2. Selecione sua exchange preferida
3. (Opcional) Insira suas API Keys para trading automático
4. Adicione mercados favoritos
5. Clique em **Salvar Configurações**

### 2. Análise de Mercado
1. Vá para a aba **Análise**
2. Selecione um símbolo (ex: BTC/USDT)
3. Escolha o timeframe
4. Clique em **Analisar**
5. Veja a previsão e nível de confiança

### 3. Análise Automática
1. Marque **Análise Automática**
2. Defina o intervalo (em segundos)
3. O programa analisará automaticamente

### 4. Trading Automático (CUIDADO!)
1. Configure suas API Keys
2. Vá para a aba **Trading Automático**
3. Marque **Habilitar Execução de Trades**
4. Clique em **Iniciar Bot**
5. Acompanhe os trades no log

⚠️ **ATENÇÃO**: Trading automático executa operações REAIS! Use com cautela e apenas com fundos que você pode perder.

### 5. Limite de Tempo
1. Vá para a aba **Limite de Tempo**
2. Marque **Habilitar Limite de Tempo**
3. Escolha o tipo:
   - **Duração**: Ex: 2 horas e 30 minutos
   - **Horário Específico**: Ex: parar às 18:00
   - **Período Diário**: Ex: funcionar das 9:00 às 18:00
4. Clique em **Aplicar Limite**

## 🔒 Segurança

- **Criptografia**: API Keys são criptografadas usando Fernet (AES)
- **Armazenamento Local**: Credenciais ficam apenas no seu computador
- **Sem Telemetria**: Nenhum dado é enviado para servidores externos

## ⚠️ Avisos Importantes

1. **Risco Financeiro**: Trading de criptomoedas envolve risco significativo de perda
2. **Não é Conselho Financeiro**: Este software é apenas uma ferramenta de análise
3. **Teste Primeiro**: Use modo simulação antes de trading real
4. **API Keys**: Nunca compartilhe suas chaves de API
5. **Responsabilidade**: Você é responsável por suas decisões de trading

## 🐛 Solução de Problemas

### Erro ao conectar com exchange
- Verifique sua conexão com internet
- Confirme se a exchange está online
- Verifique suas API Keys

### Erro ao instalar TA-Lib
- Windows: Use wheel pré-compilado
- Linux/Mac: Instale dependências do sistema primeiro

### Programa não inicia
- Verifique se todas as dependências estão instaladas
- Execute como administrador (Windows)
- Verifique logs em `~/.market_analyzer/`

## 📝 Licença

Este projeto é fornecido "como está", sem garantias de qualquer tipo.

## 🤝 Suporte

Para reportar bugs ou sugerir melhorias, crie uma issue no repositório.

## 📚 Recursos Adicionais

- [Documentação Freqtrade](https://www.freqtrade.io/)
- [CCXT Documentation](https://docs.ccxt.com/)
- [TA-Lib Indicators](https://mrjbq7.github.io/ta-lib/)

---

**Desenvolvido com base no Freqtrade** 🚀
