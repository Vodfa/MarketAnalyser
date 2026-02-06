"""
Market Analysis Module - Baseado no Freqtrade
Módulo de análise técnica com indicadores para previsão de mercado
Versão sem dependência de TA-Lib (usa apenas pandas e numpy)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """
    Analisador de mercado com indicadores técnicos baseados no Freqtrade
    """
    
    def __init__(self):
        self.indicators = {}
        self.signal_strength = 0.0
    
    @staticmethod
    def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Calcula RSI (Relative Strength Index)"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_ema(series: pd.Series, period: int) -> pd.Series:
        """Calcula EMA (Exponential Moving Average)"""
        return series.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_sma(series: pd.Series, period: int) -> pd.Series:
        """Calcula SMA (Simple Moving Average)"""
        return series.rolling(window=period).mean()
    
    @staticmethod
    def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calcula MACD (Moving Average Convergence Divergence)"""
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist
    
    @staticmethod
    def calculate_bollinger_bands(series: pd.Series, period: int = 20, std: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calcula Bollinger Bands"""
        middle = series.rolling(window=period).mean()
        std_dev = series.rolling(window=period).std()
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        return upper, middle, lower
    
    @staticmethod
    def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Tuple[pd.Series, pd.Series]:
        """Calcula Stochastic Oscillator"""
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        fastk = 100 * (close - lowest_low) / (highest_high - lowest_low)
        fastd = fastk.rolling(window=3).mean()
        
        return fastk, fastd
    
    @staticmethod
    def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calcula ATR (Average True Range)"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    @staticmethod
    def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calcula ADX (Average Directional Index)"""
        # +DM e -DM
        up_move = high.diff()
        down_move = -low.diff()
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        plus_dm = pd.Series(plus_dm, index=high.index)
        minus_dm = pd.Series(minus_dm, index=high.index)
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Smoothed
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # DX e ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    @staticmethod
    def calculate_mfi(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, period: int = 14) -> pd.Series:
        """Calcula MFI (Money Flow Index)"""
        typical_price = (high + low + close) / 3
        money_flow = typical_price * volume
        
        positive_flow = np.where(typical_price > typical_price.shift(1), money_flow, 0)
        negative_flow = np.where(typical_price < typical_price.shift(1), money_flow, 0)
        
        positive_flow = pd.Series(positive_flow, index=high.index)
        negative_flow = pd.Series(negative_flow, index=high.index)
        
        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()
        
        mfi = 100 - (100 / (1 + positive_mf / negative_mf))
        
        return mfi
    
    @staticmethod
    def calculate_sar(high: pd.Series, low: pd.Series, acceleration: float = 0.02, maximum: float = 0.2) -> pd.Series:
        """Calcula Parabolic SAR (versão simplificada)"""
        sar = pd.Series(index=high.index, dtype=float)
        sar.iloc[0] = low.iloc[0]
        
        for i in range(1, len(high)):
            sar.iloc[i] = sar.iloc[i-1] + acceleration * (high.iloc[i-1] - sar.iloc[i-1])
        
        return sar
    
    def populate_indicators(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona indicadores técnicos ao dataframe
        Baseado na estratégia sample_strategy.py do Freqtrade
        """
        if dataframe is None or len(dataframe) == 0:
            return dataframe
        
        df = dataframe.copy()
        
        # Momentum Indicators
        # ------------------------------------
        
        # RSI - Relative Strength Index
        df['rsi'] = self.calculate_rsi(df['close'], 14)
        
        # Stochastic Fast
        df['fastk'], df['fastd'] = self.calculate_stochastic(
            df['high'], df['low'], df['close'], 14
        )
        
        # MACD - Moving Average Convergence Divergence
        df['macd'], df['macdsignal'], df['macdhist'] = self.calculate_macd(df['close'])
        
        # MFI - Money Flow Index
        df['mfi'] = self.calculate_mfi(
            df['high'], df['low'], df['close'], df['volume'], 14
        )
        
        # ADX - Average Directional Index
        df['adx'] = self.calculate_adx(df['high'], df['low'], df['close'], 14)
        
        # Overlap Studies
        # ------------------------------------
        
        # Bollinger Bands
        df['bb_upperband'], df['bb_middleband'], df['bb_lowerband'] = self.calculate_bollinger_bands(
            df['close'], 20, 2
        )
        
        df['bb_percent'] = (
            (df['close'] - df['bb_lowerband']) / 
            (df['bb_upperband'] - df['bb_lowerband'])
        )
        
        df['bb_width'] = (
            (df['bb_upperband'] - df['bb_lowerband']) / 
            df['bb_middleband']
        )
        
        # EMA - Exponential Moving Average
        df['ema9'] = self.calculate_ema(df['close'], 9)
        df['ema21'] = self.calculate_ema(df['close'], 21)
        df['ema50'] = self.calculate_ema(df['close'], 50)
        df['ema200'] = self.calculate_ema(df['close'], 200)
        
        # SMA - Simple Moving Average
        df['sma20'] = self.calculate_sma(df['close'], 20)
        df['sma50'] = self.calculate_sma(df['close'], 50)
        df['sma200'] = self.calculate_sma(df['close'], 200)
        
        # SAR - Parabolic SAR
        df['sar'] = self.calculate_sar(df['high'], df['low'])
        
        # TEMA - Triple Exponential Moving Average
        ema1 = self.calculate_ema(df['close'], 9)
        ema2 = self.calculate_ema(ema1, 9)
        ema3 = self.calculate_ema(ema2, 9)
        df['tema'] = 3 * ema1 - 3 * ema2 + ema3
        
        # Volume Indicators
        # ------------------------------------
        
        # OBV - On Balance Volume
        obv = [0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        df['obv'] = obv
        
        # AD - Accumulation/Distribution
        clv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
        clv = clv.fillna(0)
        df['ad'] = (clv * df['volume']).cumsum()
        
        # Volatility Indicators
        # ------------------------------------
        
        # ATR - Average True Range
        df['atr'] = self.calculate_atr(df['high'], df['low'], df['close'], 14)
        
        # NATR - Normalized Average True Range
        df['natr'] = (df['atr'] / df['close']) * 100
        
        return df
    
    def generate_signals(self, dataframe: pd.DataFrame) -> Tuple[int, float, Dict]:
        """
        Gera sinais de compra/venda baseado nos indicadores
        
        Returns:
            Tuple[int, float, Dict]: (sinal, força, detalhes)
            sinal: 1 (compra), -1 (venda), 0 (neutro)
            força: 0.0 a 1.0 indicando a força do sinal
            detalhes: dicionário com informações detalhadas
        """
        if dataframe is None or len(dataframe) < 2:
            return 0, 0.0, {}
        
        # Pega os últimos valores
        last = dataframe.iloc[-1]
        prev = dataframe.iloc[-2]
        
        buy_signals = 0
        sell_signals = 0
        total_signals = 0
        details = {}
        
        # RSI Signals
        if pd.notna(last['rsi']):
            if last['rsi'] < 30:
                buy_signals += 2  # Oversold - sinal forte de compra
                details['rsi_signal'] = 'STRONG BUY (Oversold)'
            elif last['rsi'] < 40:
                buy_signals += 1
                details['rsi_signal'] = 'BUY'
            elif last['rsi'] > 70:
                sell_signals += 2  # Overbought - sinal forte de venda
                details['rsi_signal'] = 'STRONG SELL (Overbought)'
            elif last['rsi'] > 60:
                sell_signals += 1
                details['rsi_signal'] = 'SELL'
            else:
                details['rsi_signal'] = 'NEUTRAL'
            total_signals += 2
        
        # MACD Signals
        if pd.notna(last['macd']) and pd.notna(last['macdsignal']):
            if last['macd'] > last['macdsignal'] and prev['macd'] <= prev['macdsignal']:
                buy_signals += 2  # Cruzamento bullish
                details['macd_signal'] = 'STRONG BUY (Bullish Cross)'
            elif last['macd'] > last['macdsignal']:
                buy_signals += 1
                details['macd_signal'] = 'BUY'
            elif last['macd'] < last['macdsignal'] and prev['macd'] >= prev['macdsignal']:
                sell_signals += 2  # Cruzamento bearish
                details['macd_signal'] = 'STRONG SELL (Bearish Cross)'
            elif last['macd'] < last['macdsignal']:
                sell_signals += 1
                details['macd_signal'] = 'SELL'
            else:
                details['macd_signal'] = 'NEUTRAL'
            total_signals += 2
        
        # Bollinger Bands Signals
        if pd.notna(last['bb_lowerband']) and pd.notna(last['bb_upperband']):
            if last['close'] < last['bb_lowerband']:
                buy_signals += 2  # Preço abaixo da banda inferior
                details['bb_signal'] = 'STRONG BUY (Below Lower Band)'
            elif pd.notna(last['bb_percent']) and last['bb_percent'] < 0.2:
                buy_signals += 1
                details['bb_signal'] = 'BUY'
            elif last['close'] > last['bb_upperband']:
                sell_signals += 2  # Preço acima da banda superior
                details['bb_signal'] = 'STRONG SELL (Above Upper Band)'
            elif pd.notna(last['bb_percent']) and last['bb_percent'] > 0.8:
                sell_signals += 1
                details['bb_signal'] = 'SELL'
            else:
                details['bb_signal'] = 'NEUTRAL'
            total_signals += 2
        
        # EMA Crossover Signals
        if pd.notna(last['ema9']) and pd.notna(last['ema21']):
            if last['ema9'] > last['ema21'] and prev['ema9'] <= prev['ema21']:
                buy_signals += 2  # Golden cross
                details['ema_signal'] = 'STRONG BUY (Golden Cross)'
            elif last['ema9'] > last['ema21']:
                buy_signals += 1
                details['ema_signal'] = 'BUY'
            elif last['ema9'] < last['ema21'] and prev['ema9'] >= prev['ema21']:
                sell_signals += 2  # Death cross
                details['ema_signal'] = 'STRONG SELL (Death Cross)'
            elif last['ema9'] < last['ema21']:
                sell_signals += 1
                details['ema_signal'] = 'SELL'
            else:
                details['ema_signal'] = 'NEUTRAL'
            total_signals += 2
        
        # MFI Signals (Money Flow Index)
        if pd.notna(last['mfi']):
            if last['mfi'] < 20:
                buy_signals += 1  # Oversold
                details['mfi_signal'] = 'BUY (Oversold)'
            elif last['mfi'] > 80:
                sell_signals += 1  # Overbought
                details['mfi_signal'] = 'SELL (Overbought)'
            else:
                details['mfi_signal'] = 'NEUTRAL'
            total_signals += 1
        
        # ADX Trend Strength
        if pd.notna(last['adx']):
            if last['adx'] > 25:
                details['trend_strength'] = 'STRONG'
            elif last['adx'] > 20:
                details['trend_strength'] = 'MODERATE'
            else:
                details['trend_strength'] = 'WEAK'
        
        # Calcula sinal final e força
        net_signal = buy_signals - sell_signals
        max_possible = total_signals * 2
        
        if net_signal > 0:
            signal = 1  # BUY
            strength = min(net_signal / max_possible, 1.0) if max_possible > 0 else 0.0
            details['decision'] = 'BUY'
        elif net_signal < 0:
            signal = -1  # SELL
            strength = min(abs(net_signal) / max_possible, 1.0) if max_possible > 0 else 0.0
            details['decision'] = 'SELL'
        else:
            signal = 0  # NEUTRAL
            strength = 0.0
            details['decision'] = 'HOLD'
        
        details['buy_signals'] = buy_signals
        details['sell_signals'] = sell_signals
        details['signal_strength'] = f"{strength * 100:.1f}%"
        details['current_price'] = float(last['close'])
        details['rsi_value'] = float(last['rsi']) if pd.notna(last['rsi']) else 0.0
        details['macd_value'] = float(last['macd']) if pd.notna(last['macd']) else 0.0
        details['adx_value'] = float(last['adx']) if pd.notna(last['adx']) else 0.0
        
        return signal, strength, details
    
    def predict_direction(self, dataframe: pd.DataFrame) -> Dict:
        """
        Prediz se o gráfico vai subir ou descer
        
        Returns:
            Dict com previsão e detalhes
        """
        signal, strength, details = self.generate_signals(dataframe)
        
        prediction = {
            'direction': 'UP' if signal == 1 else 'DOWN' if signal == -1 else 'SIDEWAYS',
            'confidence': strength * 100,
            'signal': signal,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        return prediction
