# Market Analyzer - AI Trading Assistant

## 📊 Description

Market Analyzer is an advanced financial market analysis program based on **Freqtrade**, with modern graphical interface, built-in browser for automated trades, and sophisticated time limit system.

## ✨ Features

### 🎯 Market Analysis
- **Advanced Technical Analysis**: Based on Freqtrade indicators
- **Implemented Indicators**:
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

- **Direction Prediction**: UP, DOWN or SIDEWAYS
- **Confidence Level**: Percentage confidence in the prediction
- **Automatic Analysis**: Configure custom intervals

### 🔧 Settings
- **Multiple Exchanges Supported**:
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

- **Secure Credential Management**: Encrypted API Keys
- **Favorite Markets**: Save your preferred pairs
- **Multiple Timeframes**: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w

### 🤖 Automated Trading
- **Trading Bot**: Executes trades based on signals
- **Stop Loss and Take Profit**: Automatic risk management
- **Multiple Simultaneous Trades**: Configure maximum number
- **Trade History**: Track all operations

### 🌐 Built-in Browser
- **Direct Access**: TradingView, Binance, Coinbase
- **Full Navigation**: Back, forward, refresh
- **Custom URLs**: Access any website

### ⏰ Sophisticated Time Limit
- **Duration**: Set maximum execution time (hours, minutes, seconds)
- **Specific Time**: Stop at exact date/time
- **Daily Period**: Operate only during specific hours
- **Automatic Shutdown**: Closes program when limit is reached

## 🚀 Installation

### Requirements
- Windows 10/11 (64-bit)
- 4GB RAM minimum
- Internet connection

### Option 1: Executable (.exe)
1. Download the `MarketAnalyzer.exe` file
2. Run the program
3. Configure your preferences

### Option 2: Source Code
1. Install Python 3.8 or higher
2. Install TA-Lib:
   - Windows: Download wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
   - Linux: sudo apt-get install ta-lib
   - Mac: brew install ta-lib

3. Install dependencies:
pip install -r requirements.txt

4. Run the program:
python gui_main.py

## 📖 How to Use

### 1. Initial Setup
1. Go to **Settings** tab
2. Select your preferred exchange
3. (Optional) Enter your API Keys for automated trading
4. Add favorite markets
5. Click **Save Settings**

### 2. Market Analysis
1. Go to **Analysis** tab
2. Select a symbol (ex: BTC/USDT)
3. Choose timeframe
4. Click **Analyze**
5. View prediction and confidence level

### 3. Automatic Analysis
1. Check **Automatic Analysis**
2. Set interval (in seconds)
3. Program will analyze automatically

### 4. Automated Trading (CAUTION!)
1. Configure your API Keys
2. Go to **Automated Trading** tab
3. Check **Enable Trade Execution**
4. Click **Start Bot**
5. Monitor trades in log

⚠️ WARNING: Automated trading executes REAL operations! Use with caution and only with funds you can afford to lose.

### 5. Time Limit
1. Go to **Time Limit** tab
2. Check **Enable Time Limit**
3. Choose type:
   - Duration: Ex: 2 hours 30 minutes
   - Specific Time: Ex: stop at 18:00
   - Daily Period: Ex: operate 9:00 to 18:00
4. Click **Apply Limit**

## 🔒 Security

- Encryption: API Keys encrypted using Fernet (AES)
- Local Storage: Credentials stay only on your computer
- No Telemetry: No data sent to external servers

## ⚠️ Important Warnings

1. Financial Risk: Cryptocurrency trading involves significant loss risk
2. Not Financial Advice: This software is only an analysis tool
3. Test First: Use simulation mode before real trading
4. API Keys: Never share your API keys
5. Responsibility: You are responsible for your trading decisions

## 🐛 Troubleshooting

### Error connecting to exchange
- Check internet connection
- Confirm exchange is online
- Verify API Keys

### Error installing TA-Lib
- Windows: Use pre-compiled wheel
- Linux/Mac: Install system dependencies first

### Program won't start
- Check all dependencies installed
- Run as administrator (Windows)
- Check logs in ~/.market_analyzer/

## 📝 License

This project is provided "as is", without any warranties.

## 🤝 Support

To report bugs or suggest improvements, create an issue in the repository.

## 📚 Additional Resources

- Freqtrade Documentation: https://www.freqtrade.io/
- CCXT Documentation: https://docs.ccxt.com/
- TA-Lib Indicators: https://mrjbq7.github.io/ta-lib/

---

Developed based on Freqtrade
