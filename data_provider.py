"""
Data Provider Module
Módulo para coletar dados de diferentes exchanges e fontes
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import requests
from datetime import datetime, timedelta
import logging
import ccxt

logger = logging.getLogger(__name__)


class DataProvider:
    """
    Provedor de dados de mercado de múltiplas fontes
    """
    
    SUPPORTED_EXCHANGES = {
        'binance': 'Binance',
        'coinbase': 'Coinbase',
        'kraken': 'Kraken',
        'bitfinex': 'Bitfinex',
        'bybit': 'Bybit',
        'okx': 'OKX',
        'kucoin': 'KuCoin',
        'huobi': 'Huobi',
        'gateio': 'Gate.io',
        'mexc': 'MEXC'
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
        
        self._init_exchange()
    
    def _init_exchange(self):
        """Inicializa a conexão com a exchange usando CCXT"""
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            
            config = {
                'enableRateLimit': True,
                'timeout': 30000,
            }
            
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
    
    def get_ohlcv_data(
        self, 
        symbol: str, 
        timeframe: str = '5m', 
        limit: int = 500
    ) -> Optional[pd.DataFrame]:
        """
        Obtém dados OHLCV (Open, High, Low, Close, Volume) de um símbolo
        
        Args:
            symbol: Símbolo do par (ex: 'BTC/USDT')
            timeframe: Timeframe dos candles (1m, 5m, 15m, 1h, etc)
            limit: Número de candles a retornar
            
        Returns:
            DataFrame com colunas: timestamp, open, high, low, close, volume
        """
        try:
            if not self.exchange:
                logger.error("Exchange não inicializada")
                return None
            
            # Busca dados OHLCV
            ohlcv = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit
            )
            
            if not ohlcv:
                logger.warning(f"Nenhum dado retornado para {symbol}")
                return None
            
            # Converte para DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Converte timestamp para datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Garante que os valores são numéricos
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            logger.info(f"Dados obtidos para {symbol}: {len(df)} candles")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao obter dados OHLCV para {symbol}: {e}")
            return None
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """
        Obtém informações de ticker (preço atual, volume, etc)
        
        Args:
            symbol: Símbolo do par (ex: 'BTC/USDT')
            
        Returns:
            Dicionário com informações do ticker
        """
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
                'timestamp': ticker.get('timestamp')
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter ticker para {symbol}: {e}")
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
