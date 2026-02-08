"""
Trading Bot Module
Bot de trading automático baseado em sinais de análise.
Suporta múltiplos ativos: criptomoedas, ações e forex.
Pode executar trades via API (simulado) ou via navegador integrado.
"""

import logging
from typing import Dict, Optional, List, Callable, Any
from datetime import datetime, timedelta
import time
from threading import Thread, Event
import pandas as pd

from data_provider import (
    DataProvider,
    ASSET_TYPE_CRYPTO,
    ASSET_TYPE_STOCK,
    ASSET_TYPE_FOREX,
)

logger = logging.getLogger(__name__)


def _build_symbol_list(config: Dict) -> List[tuple]:
    """Constrói lista (symbol, asset_type) a partir da config.
    Usa autotrade_crypto, autotrade_stocks, autotrade_forex quando presentes na config
    (podem ser listas vazias = nenhum ativo); senão usa favorite_markets, stock_symbols, forex_pairs.
    """
    if 'autotrade_crypto' in config:
        crypto = config['autotrade_crypto']
    else:
        crypto = config.get('favorite_markets', [])
    if 'autotrade_stocks' in config:
        stocks = config['autotrade_stocks']
    else:
        stocks = config.get('stock_symbols', [])
    if 'autotrade_forex' in config:
        forex = config['autotrade_forex']
    else:
        forex = config.get('forex_pairs', [])

    out = []
    for s in crypto:
        out.append((s, ASSET_TYPE_CRYPTO))
    for s in stocks:
        out.append((s, ASSET_TYPE_STOCK))
    for s in forex:
        out.append((s, ASSET_TYPE_FOREX))
    return out


class TradingBot:
    """
    Bot de trading automático.
    Executa trades baseado em sinais da análise técnica.
    Suporta crypto, ações e forex; execução via API ou navegador.
    """
    
    def __init__(self, data_provider, analyzer, config: Dict, on_trade_signal: Callable[[Dict], None] = None):
        """
        Inicializa o trading bot.
        
        Args:
            data_provider: Provedor de dados de mercado
            analyzer: Analisador de mercado
            config: Configurações do bot
            on_trade_signal: Callback chamado quando há sinal para executar trade (ex.: para abrir no navegador).
                             Recebe dict: symbol, side, amount, price, asset_type, stop_loss, take_profit, details.
        """
        self.data_provider = data_provider
        self.analyzer = analyzer
        self.config = config
        self.on_trade_signal = on_trade_signal or (lambda _: None)
        
        self.running = False
        self.thread = None
        self.stop_event = Event()
        
        self.active_trades = {}
        self.trade_history = []
        
        self.max_trades = config.get('max_trades', 5)
        self.trade_amount = config.get('trade_amount', 100)
        self.stop_loss_percent = config.get('stop_loss_percent', 2.0)
        self.take_profit_percent = config.get('take_profit_percent', 5.0)
        self.check_interval = config.get('check_interval', 60)
        self.execute_via_browser = config.get('execute_via_browser', False)
        
        self.symbols_with_type = _build_symbol_list(config)
        self.timeframe = config.get('default_timeframe', '5m')
        
        logger.info(
            "Trading bot inicializado (crypto=%d, stocks=%d, forex=%d)",
            sum(1 for _, t in self.symbols_with_type if t == ASSET_TYPE_CRYPTO),
            sum(1 for _, t in self.symbols_with_type if t == ASSET_TYPE_STOCK),
            sum(1 for _, t in self.symbols_with_type if t == ASSET_TYPE_FOREX),
        )
    
    def start(self):
        """Inicia o bot"""
        if self.running:
            logger.warning("Bot já está rodando")
            return
        
        self.running = True
        self.stop_event.clear()
        
        self.thread = Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
        logger.info("Trading bot iniciado")
    
    def stop(self):
        """Para o bot"""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("Trading bot parado")
    
    def _run_loop(self):
        """Loop principal do bot"""
        logger.info("Iniciando loop do trading bot")
        
        while self.running and not self.stop_event.is_set():
            try:
                # Verifica trades ativos
                self._check_active_trades()
                
                # Procura novas oportunidades
                if len(self.active_trades) < self.max_trades:
                    self._scan_opportunities()
                
                # Aguarda próximo ciclo
                self.stop_event.wait(self.check_interval)
                
            except Exception as e:
                logger.error(f"Erro no loop do bot: {e}")
                self.stop_event.wait(10)  # Aguarda 10s antes de tentar novamente
        
        logger.info("Loop do trading bot encerrado")
    
    def _scan_opportunities(self):
        """Escaneia todos os ativos configurados (crypto, ações, forex) em busca de oportunidades."""
        logger.info("Escaneando oportunidades de trade...")
        
        for symbol, asset_type in self.symbols_with_type:
            try:
                if symbol in self.active_trades:
                    continue
                
                df = self.data_provider.get_ohlcv_data(
                    symbol,
                    self.timeframe,
                    limit=500,
                    asset_type=asset_type,
                )
                
                if df is None or len(df) == 0:
                    continue
                
                df = self.analyzer.populate_indicators(df)
                signal, strength, details = self.analyzer.generate_signals(df)
                
                if signal == 1 and strength >= 0.6:
                    self._execute_buy(symbol, asset_type, df, strength, details)
                
            except Exception as e:
                logger.error(f"Erro ao escanear {symbol}: {e}")
    
    def _execute_buy(self, symbol: str, asset_type: str, df: pd.DataFrame, strength: float, details: Dict):
        """
        Executa ordem de compra (simulada ou sinal para execução via navegador).
        """
        try:
            current_price = float(df.iloc[-1]['close'])
            amount = self.trade_amount / current_price if current_price else 0
            
            stop_loss = current_price * (1 - self.stop_loss_percent / 100)
            take_profit = current_price * (1 + self.take_profit_percent / 100)
            
            order = {
                'symbol': symbol,
                'asset_type': asset_type,
                'side': 'buy',
                'type': 'market',
                'amount': amount,
                'price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'timestamp': datetime.now(),
                'signal_strength': strength,
                'details': details,
                'status': 'open',
            }
            
            self.active_trades[symbol] = order
            
            logger.info(f"COMPRA: {symbol} ({asset_type}) @ {current_price:.2f} (força: {strength:.2%})")
            logger.info(f"Stop Loss: {stop_loss:.2f} | Take Profit: {take_profit:.2f}")
            
            self.trade_history.append({
                'action': 'BUY',
                'timestamp': datetime.now(),
                'symbol': symbol,
                'asset_type': asset_type,
                'price': current_price,
                'amount': amount,
                'strength': strength,
            })
            
            # Se execução via navegador, notifica a GUI para abrir no navegador
            if self.execute_via_browser:
                self.on_trade_signal({
                    'symbol': symbol,
                    'asset_type': asset_type,
                    'side': 'buy',
                    'amount': amount,
                    'price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'details': details,
                })
            
        except Exception as e:
            logger.error(f"Erro ao executar compra de {symbol}: {e}")
    
    def _check_active_trades(self):
        """Verifica trades ativos e executa stop loss ou take profit"""
        if not self.active_trades:
            return
        
        logger.info(f"Verificando {len(self.active_trades)} trades ativos...")
        
        symbols_to_close = []
        
        for symbol, trade in self.active_trades.items():
            try:
                asset_type = trade.get('asset_type', ASSET_TYPE_CRYPTO)
                ticker = self.data_provider.get_ticker(symbol, asset_type=asset_type)
                if not ticker or ticker.get('last') is None:
                    continue
                
                current_price = ticker['last']
                entry_price = trade['price']
                stop_loss = trade['stop_loss']
                take_profit = trade['take_profit']
                
                # Calcula P&L
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                
                logger.info(f"{symbol}: Entrada ${entry_price:.2f} | Atual ${current_price:.2f} | P&L: {pnl_percent:+.2f}%")
                
                # Verifica stop loss
                if current_price <= stop_loss:
                    logger.warning(f"STOP LOSS ativado para {symbol}!")
                    self._execute_sell(symbol, asset_type, current_price, 'STOP_LOSS')
                    symbols_to_close.append(symbol)
                
                # Verifica take profit
                elif current_price >= take_profit:
                    logger.info(f"TAKE PROFIT atingido para {symbol}!")
                    self._execute_sell(symbol, asset_type, current_price, 'TAKE_PROFIT')
                    symbols_to_close.append(symbol)
                
                # Verifica sinais de saída
                else:
                    df = self.data_provider.get_ohlcv_data(
                        symbol, self.timeframe, limit=500, asset_type=asset_type
                    )
                    if df is not None and len(df) > 0:
                        df = self.analyzer.populate_indicators(df)
                        signal, strength, details = self.analyzer.generate_signals(df)
                        
                        if signal == -1 and strength >= 0.6:
                            logger.info(f"Sinal de VENDA detectado para {symbol}")
                            self._execute_sell(symbol, asset_type, current_price, 'SIGNAL')
                            symbols_to_close.append(symbol)
                
            except Exception as e:
                logger.error(f"Erro ao verificar trade de {symbol}: {e}")
        
        # Remove trades fechados
        for symbol in symbols_to_close:
            del self.active_trades[symbol]
    
    def _execute_sell(self, symbol: str, asset_type: str, price: float, reason: str):
        """Executa ordem de venda (registro e, se browser, sinal para GUI)."""
        try:
            trade = self.active_trades[symbol]
            entry_price = trade['price']
            amount = trade['amount']
            
            pnl = (price - entry_price) * amount
            pnl_percent = ((price - entry_price) / entry_price) * 100
            
            logger.info(f"VENDA: {symbol} @ {price:.2f} ({reason}) | P&L: {pnl:.2f} ({pnl_percent:+.2f}%)")
            
            self.trade_history.append({
                'action': 'SELL',
                'timestamp': datetime.now(),
                'symbol': symbol,
                'asset_type': asset_type,
                'price': price,
                'amount': amount,
                'reason': reason,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
            })
            
            if self.execute_via_browser:
                self.on_trade_signal({
                    'symbol': symbol,
                    'asset_type': asset_type,
                    'side': 'sell',
                    'amount': amount,
                    'price': price,
                    'reason': reason,
                    'pnl': pnl,
                    'pnl_percent': pnl_percent,
                })
            
        except Exception as e:
            logger.error(f"Erro ao executar venda de {symbol}: {e}")
    
    def get_active_trades(self) -> Dict:
        """Retorna trades ativos"""
        return self.active_trades.copy()
    
    def get_trade_history(self) -> List[Dict]:
        """Retorna histórico de trades"""
        return self.trade_history.copy()
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas de trading"""
        if not self.trade_history:
            return {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_pnl': 0.0
            }
        
        sells = [t for t in self.trade_history if t['action'] == 'SELL']
        
        wins = sum(1 for t in sells if t.get('pnl', 0) > 0)
        losses = sum(1 for t in sells if t.get('pnl', 0) <= 0)
        total_pnl = sum(t.get('pnl', 0) for t in sells)
        
        return {
            'total_trades': len(sells),
            'wins': wins,
            'losses': losses,
            'win_rate': (wins / len(sells) * 100) if sells else 0.0,
            'total_pnl': total_pnl,
            'avg_pnl': (total_pnl / len(sells)) if sells else 0.0
        }
