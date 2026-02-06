"""
Trading Bot Module
Bot de trading automático baseado em sinais de análise
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import time
from threading import Thread, Event
import pandas as pd

logger = logging.getLogger(__name__)


class TradingBot:
    """
    Bot de trading automático
    Executa trades baseado em sinais da análise técnica
    """
    
    def __init__(self, data_provider, analyzer, config: Dict):
        """
        Inicializa o trading bot
        
        Args:
            data_provider: Provedor de dados de mercado
            analyzer: Analisador de mercado
            config: Configurações do bot
        """
        self.data_provider = data_provider
        self.analyzer = analyzer
        self.config = config
        
        self.running = False
        self.thread = None
        self.stop_event = Event()
        
        self.active_trades = {}
        self.trade_history = []
        
        # Configurações
        self.max_trades = config.get('max_trades', 3)
        self.trade_amount = config.get('trade_amount', 100)
        self.stop_loss_percent = config.get('stop_loss_percent', 2.0)
        self.take_profit_percent = config.get('take_profit_percent', 5.0)
        self.check_interval = config.get('check_interval', 60)  # segundos
        
        self.symbols = config.get('favorite_markets', ['BTC/USDT'])
        self.timeframe = config.get('default_timeframe', '5m')
        
        logger.info("Trading bot inicializado")
    
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
        """Escaneia mercados em busca de oportunidades"""
        logger.info("Escaneando oportunidades de trade...")
        
        for symbol in self.symbols:
            try:
                # Já tem trade ativo neste símbolo?
                if symbol in self.active_trades:
                    continue
                
                # Obtém dados
                df = self.data_provider.get_ohlcv_data(
                    symbol,
                    self.timeframe,
                    limit=500
                )
                
                if df is None or len(df) == 0:
                    continue
                
                # Analisa
                df = self.analyzer.populate_indicators(df)
                signal, strength, details = self.analyzer.generate_signals(df)
                
                # Verifica se é um sinal forte de compra
                if signal == 1 and strength >= 0.6:  # 60% de confiança mínima
                    self._execute_buy(symbol, df, strength, details)
                
            except Exception as e:
                logger.error(f"Erro ao escanear {symbol}: {e}")
    
    def _execute_buy(self, symbol: str, df: pd.DataFrame, strength: float, details: Dict):
        """
        Executa ordem de compra
        
        Args:
            symbol: Símbolo do par
            df: DataFrame com dados
            strength: Força do sinal
            details: Detalhes da análise
        """
        try:
            current_price = float(df.iloc[-1]['close'])
            
            # Calcula stop loss e take profit
            stop_loss = current_price * (1 - self.stop_loss_percent / 100)
            take_profit = current_price * (1 + self.take_profit_percent / 100)
            
            # Simula ordem (em produção, usaria self.data_provider.exchange.create_order)
            order = {
                'symbol': symbol,
                'side': 'buy',
                'type': 'market',
                'amount': self.trade_amount / current_price,
                'price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'timestamp': datetime.now(),
                'signal_strength': strength,
                'details': details,
                'status': 'open'
            }
            
            # Adiciona aos trades ativos
            self.active_trades[symbol] = order
            
            logger.info(f"COMPRA executada: {symbol} @ ${current_price:.2f} (força: {strength:.2%})")
            logger.info(f"Stop Loss: ${stop_loss:.2f} | Take Profit: ${take_profit:.2f}")
            
            # Adiciona ao histórico
            self.trade_history.append({
                'action': 'BUY',
                'timestamp': datetime.now(),
                'symbol': symbol,
                'price': current_price,
                'amount': order['amount'],
                'strength': strength
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
                # Obtém preço atual
                ticker = self.data_provider.get_ticker(symbol)
                if not ticker:
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
                    self._execute_sell(symbol, current_price, 'STOP_LOSS')
                    symbols_to_close.append(symbol)
                
                # Verifica take profit
                elif current_price >= take_profit:
                    logger.info(f"TAKE PROFIT atingido para {symbol}!")
                    self._execute_sell(symbol, current_price, 'TAKE_PROFIT')
                    symbols_to_close.append(symbol)
                
                # Verifica sinais de saída
                else:
                    df = self.data_provider.get_ohlcv_data(symbol, self.timeframe, limit=500)
                    if df is not None and len(df) > 0:
                        df = self.analyzer.populate_indicators(df)
                        signal, strength, details = self.analyzer.generate_signals(df)
                        
                        # Sinal forte de venda
                        if signal == -1 and strength >= 0.6:
                            logger.info(f"Sinal de VENDA detectado para {symbol}")
                            self._execute_sell(symbol, current_price, 'SIGNAL')
                            symbols_to_close.append(symbol)
                
            except Exception as e:
                logger.error(f"Erro ao verificar trade de {symbol}: {e}")
        
        # Remove trades fechados
        for symbol in symbols_to_close:
            del self.active_trades[symbol]
    
    def _execute_sell(self, symbol: str, price: float, reason: str):
        """
        Executa ordem de venda
        
        Args:
            symbol: Símbolo do par
            price: Preço de venda
            reason: Motivo da venda
        """
        try:
            trade = self.active_trades[symbol]
            entry_price = trade['price']
            amount = trade['amount']
            
            # Calcula resultado
            pnl = (price - entry_price) * amount
            pnl_percent = ((price - entry_price) / entry_price) * 100
            
            logger.info(f"VENDA executada: {symbol} @ ${price:.2f} ({reason})")
            logger.info(f"P&L: ${pnl:.2f} ({pnl_percent:+.2f}%)")
            
            # Adiciona ao histórico
            self.trade_history.append({
                'action': 'SELL',
                'timestamp': datetime.now(),
                'symbol': symbol,
                'price': price,
                'amount': amount,
                'reason': reason,
                'pnl': pnl,
                'pnl_percent': pnl_percent
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
