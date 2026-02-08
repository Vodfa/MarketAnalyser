"""
Data Provider Module
Módulo para coletar dados de diferentes exchanges e fontes.
Suporta: criptomoedas (CCXT), ações e forex (Yahoo Finance).
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import threading
import ccxt

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

logger = logging.getLogger(__name__)

# Tipos de ativo suportados
ASSET_TYPE_CRYPTO = 'crypto'
ASSET_TYPE_STOCK = 'stock'
ASSET_TYPE_FOREX = 'forex'


class DataProvider:
    """
    Provedor de dados de mercado de múltiplas fontes
    """
    
    SUPPORTED_EXCHANGES = {
        'binance': 'Binance',
        'binanceusdm': 'Binance Futures (USDT-M)',
        'coinbase': 'Coinbase',
        'kraken': 'Kraken',
        'bitfinex': 'Bitfinex',
        'bybit': 'Bybit',
        'okx': 'OKX',
        'kucoin': 'KuCoin',
        'huobi': 'Huobi',
        'htx': 'HTX (ex-Huobi)',
        'gateio': 'Gate.io',
        'mexc': 'MEXC',
        'bitstamp': 'Bitstamp',
        'gemini': 'Gemini',
        'bitget': 'Bitget',
        'bitmart': 'BitMart',
        'cryptocom': 'Crypto.com',
        'bitflyer': 'bitFlyer',
        'lbank': 'LBank',
    }
    
    TIMEFRAMES = {
        '1m': '1 minute',
        '5m': '5 minutes',
        '15m': '15 minutes',
        '30m': '30 minutes',
        '1h': '1 hour',
        '4h': '4 hours',
        '1d': '1 day',
        '1w': '1 week'
    }

    # Mapeamento timeframe -> intervalo yfinance (ações/forex)
    YF_INTERVAL_MAP = {
        '1m': '1m',
        '5m': '5m',
        '15m': '15m',
        '30m': '30m',
        '1h': '1h',
        '4h': '1h',   # yfinance não tem 4h; usar 1h
        '1d': '1d',
        '1w': '1wk',
    }
    
    def __init__(self, exchange_name: str = 'binance', api_key: str = None, api_secret: str = None):
        """
        Inicializa o provedor de dados
        
        Args:
            exchange_name: Nome da exchange (binance, coinbase, etc)
            api_key: API key (opcional para dados públicos)
            api_secret: API secret (opcional para dados públicos)
        """
        self.exchange_name = exchange_name.lower()
        self.api_key = api_key
        self.api_secret = api_secret
        self.exchange = None
        self._lock = threading.Lock()
        
        self._init_exchange()
    
    def _init_exchange(self):
        """Inicializa a conexão com a exchange usando CCXT"""
        try:
            if not hasattr(ccxt, self.exchange_name):
                raise ValueError(
                    f"Exchange '{self.exchange_name}' não encontrada no CCXT. "
                    f"IDs válidos incluem: {', '.join(sorted(DataProvider.SUPPORTED_EXCHANGES.keys()))}"
                )
            exchange_class = getattr(ccxt, self.exchange_name)

            config = {
                'enableRateLimit': True,
                'timeout': 30000,
                'rateLimit': 200,
            }

            # Configurações específicas para Binance (spot estável, evita 429)
            if self.exchange_name == 'binance':
                config['options'] = {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True,
                }
                config['rateLimit'] = 100
            elif self.exchange_name == 'binanceusdm':
                config['options'] = {'defaultType': 'future'}
                config['rateLimit'] = 100

            if self.api_key and self.api_secret:
                config['apiKey'] = self.api_key
                config['secret'] = self.api_secret

            self.exchange = exchange_class(config)
            logger.info(f"Exchange {self.exchange_name} inicializada com sucesso")

        except Exception as e:
            logger.error(f"Erro ao inicializar exchange {self.exchange_name}: {e}")
            raise
    
    def get_available_markets(self) -> List[str]:
        """
        Retorna lista de mercados disponíveis na exchange
        
        Returns:
            Lista de símbolos de mercado (ex: ['BTC/USDT', 'ETH/USDT'])
        """
        with self._lock:
            return self._get_available_markets_unsafe()

    def _get_available_markets_unsafe(self) -> List[str]:
        try:
            if not self.exchange:
                return []
            
            markets = self.exchange.load_markets()
            symbols = list(markets.keys())
            
            # Filtra apenas mercados ativos
            active_symbols = [
                symbol for symbol in symbols 
                if markets[symbol].get('active', True)
            ]
            
            return sorted(active_symbols)
            
        except Exception as e:
            logger.error(f"Erro ao obter mercados: {e}")
            return []
    
    @staticmethod
    def detect_asset_type(symbol: str) -> str:
        """
        Detecta o tipo de ativo pelo formato do símbolo.
        - Contém '/' (ex: BTC/USDT, EUR/USD) -> crypto ou forex conforme lista conhecida
        - Forex conhecidos: EUR/USD, GBP/USD, etc. (base/quote em 3 letras)
        - Caso contrário assume crypto
        """
        s = symbol.strip().upper()
        if '/' in s:
            base, quote = s.split('/', 1)
            # Forex: pares com USD, EUR, GBP, JPY (3-4 letras)
            forex_quotes = ('USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD')
            if len(base) <= 4 and len(quote) <= 4 and quote in forex_quotes and base != 'BTC' and base != 'ETH':
                return ASSET_TYPE_FOREX
            return ASSET_TYPE_CRYPTO
        # Símbolo único = ação (ex: AAPL, MSFT)
        return ASSET_TYPE_STOCK

    @staticmethod
    def symbol_to_yf_ticker(symbol: str, asset_type: str) -> str:
        """Converte símbolo interno para ticker do Yahoo Finance."""
        if asset_type == ASSET_TYPE_STOCK:
            return symbol.strip().upper()
        if asset_type == ASSET_TYPE_FOREX:
            # EUR/USD -> EURUSD=X, GBP/JPY -> GBPJPY=X
            pair = symbol.replace('/', '').strip().upper()
            return f"{pair}=X"
        return symbol

    def get_ohlcv_data_yf(
        self,
        symbol: str,
        timeframe: str = '5m',
        limit: int = 500,
        asset_type: str = None,
    ) -> Optional[pd.DataFrame]:
        """
        Obtém dados OHLCV de ações ou forex via Yahoo Finance.
        """
        if not YFINANCE_AVAILABLE:
            logger.error("yfinance não instalado. Use: pip install yfinance")
            return None
        asset_type = asset_type or self.detect_asset_type(symbol)
        if asset_type == ASSET_TYPE_CRYPTO:
            logger.warning("Use get_ohlcv_data para crypto (CCXT)")
            return None
        ticker = self.symbol_to_yf_ticker(symbol, asset_type)
        interval = self.YF_INTERVAL_MAP.get(timeframe, '1d')
        # yfinance 1m só permite ~7 dias; ajustar period
        period_map = {'1m': '7d', '5m': '60d', '15m': '60d', '30m': '60d', '1h': '730d', '1d': 'max', '1wk': 'max'}
        period = period_map.get(interval, '60d')
        try:
            obj = yf.Ticker(ticker)
            df = obj.history(period=period, interval=interval, auto_adjust=True)
            if df is None or len(df) == 0:
                logger.warning(f"Nenhum dado yfinance para {ticker}")
                return None
            df = df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
            df = df[['open', 'high', 'low', 'close', 'volume']].copy()
            df['volume'] = df['volume'].fillna(0)
            df.index.name = 'timestamp'
            df = df.tail(limit)
            logger.info(f"Dados yfinance obtidos para {symbol} ({ticker}): {len(df)} candles")
            return df
        except Exception as e:
            logger.error(f"Erro yfinance para {symbol}: {e}")
            return None

    def get_ohlcv_data(
        self, 
        symbol: str, 
        timeframe: str = '5m', 
        limit: int = 500,
        asset_type: str = None,
    ) -> Optional[pd.DataFrame]:
        """
        Obtém dados OHLCV (Open, High, Low, Close, Volume) de um símbolo.
        Suporta crypto (CCXT), ações e forex (Yahoo Finance).
        
        Args:
            symbol: Símbolo (ex: 'BTC/USDT', 'AAPL', 'EUR/USD')
            timeframe: Timeframe dos candles (1m, 5m, 15m, 1h, etc)
            limit: Número de candles a retornar
            asset_type: 'crypto', 'stock' ou 'forex'. Se None, detecta automaticamente.
            
        Returns:
            DataFrame com colunas: timestamp, open, high, low, close, volume
        """
        with self._lock:
            atype = asset_type or self.detect_asset_type(symbol)
            if atype == ASSET_TYPE_CRYPTO:
                return self._get_ohlcv_ccxt(symbol, timeframe, limit)
            return self.get_ohlcv_data_yf(symbol, timeframe, limit, atype)

    def _get_ohlcv_ccxt(
        self,
        symbol: str,
        timeframe: str = '5m',
        limit: int = 500,
    ) -> Optional[pd.DataFrame]:
        """Obtém OHLCV de cripto via exchange CCXT."""
        try:
            if not self.exchange:
                logger.error("Exchange não inicializada")
                return None
            
            ohlcv = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit
            )
            
            if not ohlcv:
                logger.warning(f"Nenhum dado retornado para {symbol}")
                return None
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            logger.info(f"Dados obtidos para {symbol}: {len(df)} candles")
            return df
        except Exception as e:
            logger.error(f"Erro ao obter dados OHLCV para {symbol}: {e}")
            return None
    
    def get_ticker(self, symbol: str, asset_type: str = None) -> Optional[Dict]:
        """
        Obtém informações de ticker (preço atual, volume, etc).
        Suporta crypto (CCXT) e ações/forex (Yahoo Finance).
        """
        with self._lock:
            atype = asset_type or self.detect_asset_type(symbol)
            if atype == ASSET_TYPE_CRYPTO:
                return self._get_ticker_ccxt(symbol)
            return self._get_ticker_yf(symbol, atype)

    def _get_ticker_ccxt(self, symbol: str) -> Optional[Dict]:
        """Ticker de cripto via exchange."""
        try:
            if not self.exchange:
                return None
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': ticker.get('last'),
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'high': ticker.get('high'),
                'low': ticker.get('low'),
                'volume': ticker.get('volume'),
                'change': ticker.get('change'),
                'percentage': ticker.get('percentage'),
                'timestamp': ticker.get('timestamp'),
            }
        except Exception as e:
            logger.error(f"Erro ao obter ticker para {symbol}: {e}")
            return None

    def _get_ticker_yf(self, symbol: str, asset_type: str) -> Optional[Dict]:
        """Ticker de ação/forex via Yahoo Finance."""
        if not YFINANCE_AVAILABLE:
            return None
        try:
            ticker = self.symbol_to_yf_ticker(symbol, asset_type)
            obj = yf.Ticker(ticker)
            hist = obj.history(period='5d')
            if hist is not None and len(hist) > 0:
                last = float(hist['Close'].iloc[-1])
                return {
                    'symbol': symbol,
                    'last': last,
                    'bid': None,
                    'ask': None,
                    'high': float(hist['High'].max()),
                    'low': float(hist['Low'].min()),
                    'volume': float(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                    'change': None,
                    'percentage': None,
                    'timestamp': None,
                }
            return None
        except Exception as e:
            logger.error(f"Erro ao obter ticker yfinance para {symbol}: {e}")
            return None
    
    def search_symbols(self, query: str) -> List[str]:
        """
        Busca símbolos que correspondem à query
        
        Args:
            query: Texto de busca (ex: 'BTC', 'ETH')
            
        Returns:
            Lista de símbolos correspondentes
        """
        try:
            markets = self.get_available_markets()
            query_upper = query.upper()
            
            # Filtra símbolos que contêm a query
            matching = [
                symbol for symbol in markets 
                if query_upper in symbol.upper()
            ]
            
            return matching
            
        except Exception as e:
            logger.error(f"Erro ao buscar símbolos: {e}")
            return []
    
    def get_market_categories(self) -> Dict[str, List[str]]:
        """
        Retorna mercados organizados por categoria
        
        Returns:
            Dicionário com categorias e seus símbolos
        """
        try:
            markets = self.get_available_markets()
            
            categories = {
                'USDT': [],
                'BTC': [],
                'ETH': [],
                'USD': [],
                'EUR': [],
                'Other': []
            }
            
            for symbol in markets:
                if '/USDT' in symbol:
                    categories['USDT'].append(symbol)
                elif '/BTC' in symbol:
                    categories['BTC'].append(symbol)
                elif '/ETH' in symbol:
                    categories['ETH'].append(symbol)
                elif '/USD' in symbol:
                    categories['USD'].append(symbol)
                elif '/EUR' in symbol:
                    categories['EUR'].append(symbol)
                else:
                    categories['Other'].append(symbol)
            
            return categories
            
        except Exception as e:
            logger.error(f"Erro ao categorizar mercados: {e}")
            return {}
    
    @staticmethod
    def get_supported_exchanges() -> Dict[str, str]:
        """Retorna dicionário de exchanges suportadas"""
        return DataProvider.SUPPORTED_EXCHANGES.copy()
    
    @staticmethod
    def get_supported_timeframes() -> Dict[str, str]:
        """Retorna dicionário de timeframes suportados"""
        return DataProvider.TIMEFRAMES.copy()
