Market Analyzer - AI Trading Assistant
📊 Description
Market Analyzer is an advanced financial market analysis program based on Freqtrade, featuring a modern graphical interface, built-in browser for automated trades, and a sophisticated time limit system.

✨ Features
🎯 Market Analysis
Advanced Technical Analysis: Based on Freqtrade indicators

Implemented Indicators:

RSI (Relative Strength Index)

MACD (Moving Average Convergence Divergence)

Bollinger Bands

EMA (Exponential Moving Average)

SMA (Simple Moving Average)

ADX (Average Directional Index)

MFI (Money Flow Index)

Stochastic Fast

SAR (Parabolic SAR)

TEMA (Triple Exponential Moving Average)

ATR (Average True Range)

OBV (On Balance Volume)

Direction Prediction: UP, DOWN, or SIDEWAYS

Confidence Level: Percentage confidence in the prediction

Automatic Analysis: Set custom intervals

🔧 Settings
Multiple Exchanges Supported:

Binance

Coinbase

Kraken

Bitfinex

Bybit

OKX

KuCoin

Huobi

Gate.io

MEXC

Secure Credential Management: Encrypted API Keys

Favorite Markets: Save your preferred pairs

Multiple Timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w

🤖 Automated Trading
Trading Bot: Executes trades based on signals

Stop Loss and Take Profit: Automatic risk management

Multiple Simultaneous Trades: Set the maximum number

Trade History: Track all operations

🌐 Built-in Browser
Direct Access: TradingView, Binance, Coinbase

Full Navigation: Back, forward, refresh

Custom URLs: Access any website

⏰ Sophisticated Time Limit
Duration: Set maximum execution time (hours, minutes, seconds)

Specific Time: Stop at exact date/time

Daily Period: Operate only during specific hours

Automatic Shutdown: Closes the program when limit is reached

🚀 Installation
Requirements
Windows 10/11 (64-bit)

4GB RAM minimum

Internet connection

Option 1: Executable (.exe)
Download the MarketAnalyzer.exe file

Run the program

Configure your preferences

Option 2: Source Code
Install Python 3.8 or higher

Install TA-Lib:

Windows: Download wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

Linux: sudo apt-get install ta-lib

Mac: brew install ta-lib

Install dependencies:

bash
pip install -r requirements.txt
Run the program:

bash
python gui_main.py
📖 How to Use
1. Initial Setup
Go to the Settings tab

Select your preferred exchange

(Optional) Enter your API Keys for automated trading

Add favorite markets

Click Save Settings

2. Market Analysis
Go to the Analysis tab

Select a symbol (e.g., BTC/USDT)

Choose the timeframe

Click Analyze

View the prediction and confidence level

3. Automatic Analysis
Check Automatic Analysis

Set the interval (in seconds)

The program will analyze automatically

4. Automated Trading (CAUTION!)
Configure your API Keys

Go to the Automated Trading tab

Check Enable Trade Execution

Click Start Bot

Monitor trades in the log

⚠️ WARNING: Automated trading executes REAL operations! Use with caution and only with funds you can afford to lose.

5. Time Limit
Go to the Time Limit tab

Check Enable Time Limit

Choose the type:

Duration: E.g., 2 hours and 30 minutes

Specific Time: E.g., stop at 6:00 PM

Daily Period: E.g., operate from 9:00 AM to 6:00 PM

Click Apply Limit

🔒 Security
Encryption: API Keys encrypted using Fernet (AES)

Local Storage: Credentials stay only on your computer

No Telemetry: No data sent to external servers

⚠️ Important Warnings
Financial Risk: Cryptocurrency trading involves significant risk of loss

Not Financial Advice: This software is only an analysis tool

Test First: Use simulation mode before real trading

API Keys: Never share your API keys

Responsibility: You are responsible for your trading decisions

🐛 Troubleshooting
Error connecting to exchange
Check your internet connection

Confirm the exchange is online

Verify your API Keys

Error installing TA-Lib
Windows: Use pre-compiled wheel

Linux/Mac: Install system dependencies first

Program won't start
Check if all dependencies are installed

Run as administrator (Windows)

Check logs in ~/.market_analyzer/

📝 License
This project is provided "as is," without any warranties.

🤝 Support
To report bugs or suggest improvements, create an issue in the repository.

📚 Additional Resources
Freqtrade Documentation

CCXT Documentation

TA-Lib Indicators

Developed based on Freqtrade 🚀
