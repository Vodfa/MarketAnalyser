"""
GUI Main Module
Interface gráfica principal do Market Analyzer
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging


# Garante resolução dos módulos locais quando executado como .exe (PyInstaller)
if getattr(sys, 'frozen', False):
    meipass = getattr(sys, '_MEIPASS', '')
    exe_dir = os.path.dirname(sys.executable)
    for candidate in (meipass, exe_dir):
        if candidate and candidate not in sys.path:
            sys.path.insert(0, candidate)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit, QTabWidget,
    QTableWidget, QTableWidgetItem, QGroupBox, QCheckBox, QSpinBox,
    QMessageBox, QProgressBar, QListWidget, QSplitter, QFrame,
    QDateTimeEdit, QTimeEdit
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QDateTime, QTime, QUrl
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtWebEngineWidgets import QWebEngineView

from data_provider import DataProvider
from market_analysis import MarketAnalyzer
from config_manager import ConfigManager
from trading_bot import TradingBot

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnalysisThread(QThread):
    """Thread para análise de mercado em background"""
    
    analysis_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, data_provider, analyzer, symbol, timeframe):
        super().__init__()
        self.data_provider = data_provider
        self.analyzer = analyzer
        self.symbol = symbol
        self.timeframe = timeframe
        self.running = True
    
    def run(self):
        """Executa análise"""
        try:
            # Obtém dados
            df = self.data_provider.get_ohlcv_data(
                self.symbol, 
                self.timeframe, 
                limit=500
            )
            
            if df is None or len(df) == 0:
                self.error_occurred.emit(f"Não foi possível obter dados para {self.symbol}")
                return
            
            # Adiciona indicadores
            df = self.analyzer.populate_indicators(df)
            
            # Gera previsão
            prediction = self.analyzer.predict_direction(df)
            
            # Adiciona dados do ticker
            ticker = self.data_provider.get_ticker(self.symbol)
            if ticker:
                prediction['ticker'] = ticker
            
            self.analysis_complete.emit(prediction)
            
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            self.error_occurred.emit(str(e))
    
    def stop(self):
        """Para a thread"""
        self.running = False


class MarketAnalyzerGUI(QMainWindow):
    """Interface gráfica principal do Market Analyzer"""
    
    def __init__(self):
        super().__init__()
        
        self.config_manager = ConfigManager()
        self.data_provider = None
        self.analyzer = MarketAnalyzer()
        self.trading_bot = None
        self.analysis_thread = None
        
        # Timer para análise automática
        self.auto_analysis_timer = QTimer()
        self.auto_analysis_timer.timeout.connect(self.run_analysis)
        
        # Timer para verificar limite de tempo
        self.time_limit_timer = QTimer()
        self.time_limit_timer.timeout.connect(self.check_time_limit)
        self.time_limit_timer.start(1000)  # Verifica a cada segundo
        
        self.start_time = datetime.now()
        self.time_limit_enabled = False
        self.time_limit_end = None
        
        self.init_ui()
        self.load_config()
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Market Analyzer - AI Trading Assistant")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Aba 1: Análise
        self.create_analysis_tab()
        
        # Aba 2: Configurações
        self.create_config_tab()
        
        # Aba 3: Trading Automático
        self.create_trading_tab()
        
        # Aba 4: Navegador
        self.create_browser_tab()
        
        # Aba 5: Limite de Tempo
        self.create_time_limit_tab()
        
        # Barra de status
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Pronto")
        
        # Aplicar estilo
        self.apply_style()
    
    def create_analysis_tab(self):
        """Cria aba de análise"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Controles superiores
        controls_layout = QHBoxLayout()
        
        # Seleção de símbolo
        controls_layout.addWidget(QLabel("Símbolo:"))
        self.symbol_combo = QComboBox()
        self.symbol_combo.setEditable(True)
        self.symbol_combo.setMinimumWidth(150)
        controls_layout.addWidget(self.symbol_combo)
        
        # Botão de busca
        self.search_btn = QPushButton("Buscar Símbolos")
        self.search_btn.clicked.connect(self.search_symbols)
        controls_layout.addWidget(self.search_btn)
        
        # Timeframe
        controls_layout.addWidget(QLabel("Timeframe:"))
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w'])
        self.timeframe_combo.setCurrentText('5m')
        controls_layout.addWidget(self.timeframe_combo)
        
        # Botão de análise
        self.analyze_btn = QPushButton("Analisar")
        self.analyze_btn.clicked.connect(self.run_analysis)
        self.analyze_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        controls_layout.addWidget(self.analyze_btn)
        
        # Análise automática
        self.auto_analysis_check = QCheckBox("Análise Automática")
        self.auto_analysis_check.stateChanged.connect(self.toggle_auto_analysis)
        controls_layout.addWidget(self.auto_analysis_check)
        
        self.auto_interval_spin = QSpinBox()
        self.auto_interval_spin.setMinimum(5)
        self.auto_interval_spin.setMaximum(3600)
        self.auto_interval_spin.setValue(60)
        self.auto_interval_spin.setSuffix(" seg")
        controls_layout.addWidget(self.auto_interval_spin)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Splitter para dividir resultado e log
        splitter = QSplitter(Qt.Vertical)
        
        # Área de resultado
        result_group = QGroupBox("Resultado da Análise")
        result_layout = QVBoxLayout()
        
        # Indicador de direção
        direction_layout = QHBoxLayout()
        direction_layout.addWidget(QLabel("PREVISÃO:"))
        self.direction_label = QLabel("---")
        self.direction_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.direction_label.setAlignment(Qt.AlignCenter)
        direction_layout.addWidget(self.direction_label)
        result_layout.addLayout(direction_layout)
        
        # Confiança
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("Confiança:"))
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setMinimum(0)
        self.confidence_bar.setMaximum(100)
        confidence_layout.addWidget(self.confidence_bar)
        self.confidence_label = QLabel("0%")
        confidence_layout.addWidget(self.confidence_label)
        result_layout.addLayout(confidence_layout)
        
        # Detalhes
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        result_layout.addWidget(self.details_text)
        
        result_group.setLayout(result_layout)
        splitter.addWidget(result_group)
        
        # Log
        log_group = QGroupBox("Log de Atividades")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        splitter.addWidget(log_group)
        
        layout.addWidget(splitter)
        
        self.tabs.addTab(tab, "Análise")
    
    def create_config_tab(self):
        """Cria aba de configurações"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Exchange
        exchange_group = QGroupBox("Configurações da Exchange")
        exchange_layout = QVBoxLayout()
        
        ex_layout = QHBoxLayout()
        ex_layout.addWidget(QLabel("Exchange:"))
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItems(list(DataProvider.get_supported_exchanges().values()))
        ex_layout.addWidget(self.exchange_combo)
        exchange_layout.addLayout(ex_layout)
        
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        api_key_layout.addWidget(self.api_key_input)
        exchange_layout.addLayout(api_key_layout)
        
        api_secret_layout = QHBoxLayout()
        api_secret_layout.addWidget(QLabel("API Secret:"))
        self.api_secret_input = QLineEdit()
        self.api_secret_input.setEchoMode(QLineEdit.Password)
        api_secret_layout.addWidget(self.api_secret_input)
        exchange_layout.addLayout(api_secret_layout)
        
        exchange_group.setLayout(exchange_layout)
        layout.addWidget(exchange_group)
        
        # Mercados favoritos
        markets_group = QGroupBox("Mercados Favoritos")
        markets_layout = QVBoxLayout()
        
        self.markets_list = QListWidget()
        markets_layout.addWidget(self.markets_list)
        
        markets_btn_layout = QHBoxLayout()
        add_market_btn = QPushButton("Adicionar")
        add_market_btn.clicked.connect(self.add_favorite_market)
        markets_btn_layout.addWidget(add_market_btn)
        
        remove_market_btn = QPushButton("Remover")
        remove_market_btn.clicked.connect(self.remove_favorite_market)
        markets_btn_layout.addWidget(remove_market_btn)
        markets_layout.addLayout(markets_btn_layout)
        
        markets_group.setLayout(markets_layout)
        layout.addWidget(markets_group)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Salvar Configurações")
        save_btn.clicked.connect(self.save_config)
        save_btn.setStyleSheet("background-color: #2196F3; color: white;")
        btn_layout.addWidget(save_btn)
        
        load_btn = QPushButton("Recarregar Configurações")
        load_btn.clicked.connect(self.load_config)
        btn_layout.addWidget(load_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "Configurações")
    
    def create_trading_tab(self):
        """Cria aba de trading automático"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Status
        status_group = QGroupBox("Status do Trading Bot")
        status_layout = QVBoxLayout()
        
        self.bot_status_label = QLabel("Status: Parado")
        self.bot_status_label.setFont(QFont("Arial", 12, QFont.Bold))
        status_layout.addWidget(self.bot_status_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Controles
        controls_group = QGroupBox("Controles")
        controls_layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        
        self.start_bot_btn = QPushButton("Iniciar Bot")
        self.start_bot_btn.clicked.connect(self.start_trading_bot)
        self.start_bot_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_layout.addWidget(self.start_bot_btn)
        
        self.stop_bot_btn = QPushButton("Parar Bot")
        self.stop_bot_btn.clicked.connect(self.stop_trading_bot)
        self.stop_bot_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_bot_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_bot_btn)
        
        controls_layout.addLayout(btn_layout)
        
        # Configurações do bot
        self.enable_trading_check = QCheckBox("Habilitar Execução de Trades (CUIDADO!)")
        controls_layout.addWidget(self.enable_trading_check)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Log de trades
        trades_group = QGroupBox("Histórico de Trades")
        trades_layout = QVBoxLayout()
        
        self.trades_text = QTextEdit()
        self.trades_text.setReadOnly(True)
        trades_layout.addWidget(self.trades_text)
        
        trades_group.setLayout(trades_layout)
        layout.addWidget(trades_group)
        
        self.tabs.addTab(tab, "Trading Automático")
    
    def create_browser_tab(self):
        """Cria aba com navegador embutido"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Barra de navegação
        nav_layout = QHBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Digite a URL...")
        self.url_input.returnPressed.connect(self.navigate_to_url)
        nav_layout.addWidget(self.url_input)
        
        go_btn = QPushButton("Ir")
        go_btn.clicked.connect(self.navigate_to_url)
        nav_layout.addWidget(go_btn)
        
        back_btn = QPushButton("←")
        back_btn.clicked.connect(self.browser_back)
        nav_layout.addWidget(back_btn)
        
        forward_btn = QPushButton("→")
        forward_btn.clicked.connect(self.browser_forward)
        nav_layout.addWidget(forward_btn)
        
        refresh_btn = QPushButton("↻")
        refresh_btn.clicked.connect(self.browser_refresh)
        nav_layout.addWidget(refresh_btn)
        
        layout.addLayout(nav_layout)
        
        # Navegador web
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.tradingview.com"))
        self.browser.urlChanged.connect(self.update_url_bar)
        layout.addWidget(self.browser)
        
        # Botões rápidos
        quick_links_layout = QHBoxLayout()
        
        tv_btn = QPushButton("TradingView")
        tv_btn.clicked.connect(lambda: self.browser.setUrl(QUrl("https://www.tradingview.com")))
        quick_links_layout.addWidget(tv_btn)
        
        binance_btn = QPushButton("Binance")
        binance_btn.clicked.connect(lambda: self.browser.setUrl(QUrl("https://www.binance.com")))
        quick_links_layout.addWidget(binance_btn)
        
        coinbase_btn = QPushButton("Coinbase")
        coinbase_btn.clicked.connect(lambda: self.browser.setUrl(QUrl("https://www.coinbase.com")))
        quick_links_layout.addWidget(coinbase_btn)
        
        kraken_btn = QPushButton("Kraken")
        kraken_btn.clicked.connect(lambda: self.browser.setUrl(QUrl("https://www.kraken.com")))
        quick_links_layout.addWidget(kraken_btn)
        
        bybit_btn = QPushButton("Bybit")
        bybit_btn.clicked.connect(lambda: self.browser.setUrl(QUrl("https://www.bybit.com")))
        quick_links_layout.addWidget(bybit_btn)
        
        okx_btn = QPushButton("OKX")
        okx_btn.clicked.connect(lambda: self.browser.setUrl(QUrl("https://www.okx.com")))
        quick_links_layout.addWidget(okx_btn)
        
        bitget_btn = QPushButton("Bitget")
        bitget_btn.clicked.connect(lambda: self.browser.setUrl(QUrl("https://www.bitget.com")))
        quick_links_layout.addWidget(bitget_btn)
        
        quick_links_layout.addStretch()
        layout.addLayout(quick_links_layout)
        
        self.tabs.addTab(tab, "Navegador")
    
    def create_time_limit_tab(self):
        """Cria aba de limite de tempo"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Status
        status_group = QGroupBox("Status do Tempo")
        status_layout = QVBoxLayout()
        
        self.time_status_label = QLabel("Tempo de execução: 00:00:00")
        self.time_status_label.setFont(QFont("Arial", 14))
        status_layout.addWidget(self.time_status_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Configurações de limite
        limit_group = QGroupBox("Configurações de Limite de Tempo")
        limit_layout = QVBoxLayout()
        
        self.enable_time_limit_check = QCheckBox("Habilitar Limite de Tempo")
        self.enable_time_limit_check.stateChanged.connect(self.toggle_time_limit)
        limit_layout.addWidget(self.enable_time_limit_check)
        
        # Tipo de limite
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Tipo de Limite:"))
        self.limit_type_combo = QComboBox()
        self.limit_type_combo.addItems([
            "Duração (tempo de execução)",
            "Horário Específico",
            "Período Diário"
        ])
        self.limit_type_combo.currentIndexChanged.connect(self.update_time_limit_controls)
        type_layout.addWidget(self.limit_type_combo)
        limit_layout.addLayout(type_layout)
        
        # Controles de duração
        self.duration_widget = QWidget()
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duração:"))
        self.duration_hours = QSpinBox()
        self.duration_hours.setMaximum(999)
        self.duration_hours.setSuffix(" h")
        duration_layout.addWidget(self.duration_hours)
        self.duration_minutes = QSpinBox()
        self.duration_minutes.setMaximum(59)
        self.duration_minutes.setSuffix(" min")
        duration_layout.addWidget(self.duration_minutes)
        self.duration_seconds = QSpinBox()
        self.duration_seconds.setMaximum(59)
        self.duration_seconds.setSuffix(" seg")
        duration_layout.addWidget(self.duration_seconds)
        duration_layout.addStretch()
        self.duration_widget.setLayout(duration_layout)
        limit_layout.addWidget(self.duration_widget)
        
        # Controles de horário específico
        self.specific_time_widget = QWidget()
        specific_layout = QHBoxLayout()
        specific_layout.addWidget(QLabel("Parar em:"))
        self.specific_datetime = QDateTimeEdit()
        self.specific_datetime.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        self.specific_datetime.setCalendarPopup(True)
        specific_layout.addWidget(self.specific_datetime)
        specific_layout.addStretch()
        self.specific_time_widget.setLayout(specific_layout)
        self.specific_time_widget.hide()
        limit_layout.addWidget(self.specific_time_widget)
        
        # Controles de período diário
        self.daily_period_widget = QWidget()
        daily_layout = QVBoxLayout()
        
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Horário de Início:"))
        self.daily_start_time = QTimeEdit()
        self.daily_start_time.setTime(QTime(9, 0))
        start_layout.addWidget(self.daily_start_time)
        start_layout.addStretch()
        daily_layout.addLayout(start_layout)
        
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("Horário de Término:"))
        self.daily_end_time = QTimeEdit()
        self.daily_end_time.setTime(QTime(18, 0))
        end_layout.addWidget(self.daily_end_time)
        end_layout.addStretch()
        daily_layout.addLayout(end_layout)
        
        self.daily_period_widget.setLayout(daily_layout)
        self.daily_period_widget.hide()
        limit_layout.addWidget(self.daily_period_widget)
        
        # Botão aplicar
        apply_btn = QPushButton("Aplicar Limite")
        apply_btn.clicked.connect(self.apply_time_limit)
        apply_btn.setStyleSheet("background-color: #2196F3; color: white;")
        limit_layout.addWidget(apply_btn)
        
        limit_group.setLayout(limit_layout)
        layout.addWidget(limit_group)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "Limite de Tempo")
        
        # Timer para atualizar display de tempo
        self.time_display_timer = QTimer()
        self.time_display_timer.timeout.connect(self.update_time_display)
        self.time_display_timer.start(1000)
    
    def apply_style(self):
        """Aplica estilo à interface"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
        """)
    
    # Métodos de funcionalidade
    
    def load_config(self):
        """Carrega configurações"""
        try:
            config = self.config_manager.load_config()
            
            # Exchange
            exchange_name = config.get('exchange', 'Binance')
            index = self.exchange_combo.findText(exchange_name)
            if index >= 0:
                self.exchange_combo.setCurrentIndex(index)
            
            # API credentials
            self.api_key_input.setText(config.get('api_key', ''))
            self.api_secret_input.setText(config.get('api_secret', ''))
            
            # Mercados favoritos
            favorites = config.get('favorite_markets', [])
            self.markets_list.clear()
            self.markets_list.addItems(favorites)
            
            # Inicializa data provider
            self.init_data_provider()
            
            self.log("Configurações carregadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao carregar configurações: {e}")
    
    def save_config(self):
        """Salva configurações"""
        try:
            # Obtém exchange ID
            exchange_name = self.exchange_combo.currentText()
            exchange_id = None
            for eid, ename in DataProvider.get_supported_exchanges().items():
                if ename == exchange_name:
                    exchange_id = eid
                    break
            
            config = {
                'exchange': exchange_name,
                'exchange_id': exchange_id or 'binance',
                'api_key': self.api_key_input.text(),
                'api_secret': self.api_secret_input.text(),
                'favorite_markets': [
                    self.markets_list.item(i).text() 
                    for i in range(self.markets_list.count())
                ]
            }
            
            self.config_manager.save_config(config)
            
            # Reinicializa data provider
            self.init_data_provider()
            
            QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
            self.log("Configurações salvas")
            
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao salvar configurações: {e}")
    
    def init_data_provider(self):
        """Inicializa o provedor de dados"""
        try:
            config = self.config_manager.load_config()
            exchange_id = config.get('exchange_id', 'binance')
            api_key = config.get('api_key', '')
            api_secret = config.get('api_secret', '')
            
            self.data_provider = DataProvider(
                exchange_name=exchange_id,
                api_key=api_key if api_key else None,
                api_secret=api_secret if api_secret else None
            )
            
            # Carrega símbolos
            self.load_symbols()
            
            self.log(f"Conectado à exchange: {exchange_id}")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar data provider: {e}")
            self.log(f"ERRO: {e}")
    
    def load_symbols(self):
        """Carrega símbolos disponíveis"""
        try:
            if not self.data_provider:
                return
            
            markets = self.data_provider.get_available_markets()
            
            # Adiciona ao combo
            self.symbol_combo.clear()
            
            # Adiciona favoritos primeiro
            favorites = [
                self.markets_list.item(i).text() 
                for i in range(self.markets_list.count())
            ]
            
            if favorites:
                self.symbol_combo.addItems(favorites)
                self.symbol_combo.insertSeparator(len(favorites))
            
            # Adiciona todos os mercados
            self.symbol_combo.addItems(markets[:500])  # Limita a 500 para performance
            
            self.log(f"Carregados {len(markets)} mercados")
            
        except Exception as e:
            logger.error(f"Erro ao carregar símbolos: {e}")
    
    def search_symbols(self):
        """Busca símbolos"""
        try:
            if not self.data_provider:
                QMessageBox.warning(self, "Aviso", "Configure a exchange primeiro!")
                return
            
            query = self.symbol_combo.currentText()
            if not query:
                return
            
            results = self.data_provider.search_symbols(query)
            
            if results:
                self.symbol_combo.clear()
                self.symbol_combo.addItems(results)
                self.log(f"Encontrados {len(results)} símbolos para '{query}'")
            else:
                QMessageBox.information(self, "Busca", f"Nenhum símbolo encontrado para '{query}'")
                
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            QMessageBox.critical(self, "Erro", f"Erro na busca: {e}")
    
    def add_favorite_market(self):
        """Adiciona mercado aos favoritos"""
        symbol = self.symbol_combo.currentText()
        if symbol and not self.markets_list.findItems(symbol, Qt.MatchExactly):
            self.markets_list.addItem(symbol)
            self.log(f"Adicionado aos favoritos: {symbol}")
    
    def remove_favorite_market(self):
        """Remove mercado dos favoritos"""
        current_item = self.markets_list.currentItem()
        if current_item:
            symbol = current_item.text()
            self.markets_list.takeItem(self.markets_list.row(current_item))
            self.log(f"Removido dos favoritos: {symbol}")
    
    def run_analysis(self):
        """Executa análise de mercado"""
        try:
            if not self.data_provider:
                QMessageBox.warning(self, "Aviso", "Configure a exchange primeiro!")
                return
            
            symbol = self.symbol_combo.currentText()
            timeframe = self.timeframe_combo.currentText()
            
            if not symbol:
                QMessageBox.warning(self, "Aviso", "Selecione um símbolo!")
                return
            
            self.log(f"Iniciando análise: {symbol} ({timeframe})")
            self.analyze_btn.setEnabled(False)
            self.status_bar.showMessage(f"Analisando {symbol}...")
            
            # Inicia thread de análise
            self.analysis_thread = AnalysisThread(
                self.data_provider,
                self.analyzer,
                symbol,
                timeframe
            )
            self.analysis_thread.analysis_complete.connect(self.on_analysis_complete)
            self.analysis_thread.error_occurred.connect(self.on_analysis_error)
            self.analysis_thread.start()
            
        except Exception as e:
            logger.error(f"Erro ao iniciar análise: {e}")
            self.log(f"ERRO: {e}")
            self.analyze_btn.setEnabled(True)
    
    def on_analysis_complete(self, prediction):
        """Callback quando análise é completada"""
        try:
            direction = prediction['direction']
            confidence = prediction['confidence']
            details = prediction['details']
            
            # Atualiza UI
            self.direction_label.setText(direction)
            
            # Define cor baseado na direção
            if direction == 'UP':
                self.direction_label.setStyleSheet("color: #4CAF50;")  # Verde
            elif direction == 'DOWN':
                self.direction_label.setStyleSheet("color: #f44336;")  # Vermelho
            else:
                self.direction_label.setStyleSheet("color: #FF9800;")  # Laranja
            
            self.confidence_bar.setValue(int(confidence))
            self.confidence_label.setText(f"{confidence:.1f}%")
            
            # Formata detalhes
            details_text = f"""
=== ANÁLISE COMPLETA ===
Decisão: {details.get('decision', 'N/A')}
Força do Sinal: {details.get('signal_strength', 'N/A')}

Preço Atual: ${details.get('current_price', 0):.2f}

--- INDICADORES ---
RSI: {details.get('rsi_value', 0):.2f} - {details.get('rsi_signal', 'N/A')}
MACD: {details.get('macd_value', 0):.4f} - {details.get('macd_signal', 'N/A')}
ADX: {details.get('adx_value', 0):.2f} - Tendência {details.get('trend_strength', 'N/A')}
Bollinger Bands: {details.get('bb_signal', 'N/A')}
EMA: {details.get('ema_signal', 'N/A')}
MFI: {details.get('mfi_signal', 'N/A')}

--- SINAIS ---
Sinais de Compra: {details.get('buy_signals', 0)}
Sinais de Venda: {details.get('sell_signals', 0)}

Timestamp: {prediction.get('timestamp', '')}
            """
            
            self.details_text.setText(details_text)
            
            self.log(f"Análise concluída: {direction} (confiança: {confidence:.1f}%)")
            self.status_bar.showMessage(f"Análise concluída: {direction}")
            
        except Exception as e:
            logger.error(f"Erro ao processar resultado: {e}")
            self.log(f"ERRO ao processar resultado: {e}")
        
        finally:
            self.analyze_btn.setEnabled(True)
    
    def on_analysis_error(self, error_msg):
        """Callback quando ocorre erro na análise"""
        self.log(f"ERRO na análise: {error_msg}")
        self.status_bar.showMessage("Erro na análise")
        self.analyze_btn.setEnabled(True)
        QMessageBox.critical(self, "Erro", f"Erro na análise: {error_msg}")
    
    def toggle_auto_analysis(self, state):
        """Ativa/desativa análise automática"""
        if state == Qt.Checked:
            interval = self.auto_interval_spin.value() * 1000  # Converte para ms
            self.auto_analysis_timer.start(interval)
            self.log(f"Análise automática ativada (intervalo: {self.auto_interval_spin.value()}s)")
        else:
            self.auto_analysis_timer.stop()
            self.log("Análise automática desativada")
    
    def start_trading_bot(self):
        """Inicia o bot de trading"""
        try:
            if not self.enable_trading_check.isChecked():
                QMessageBox.warning(
                    self,
                    "Aviso",
                    "Habilite a execução de trades primeiro!\n\nATENÇÃO: Isso executará trades reais!"
                )
                return
            
            reply = QMessageBox.question(
                self,
                "Confirmação",
                "Tem certeza que deseja iniciar o bot de trading?\n\nIsso executará trades REAIS!",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
            
            # Inicializa trading bot
            config = self.config_manager.load_config()
            self.trading_bot = TradingBot(
                data_provider=self.data_provider,
                analyzer=self.analyzer,
                config=config
            )
            
            self.trading_bot.start()
            
            self.bot_status_label.setText("Status: ATIVO")
            self.bot_status_label.setStyleSheet("color: #4CAF50;")
            self.start_bot_btn.setEnabled(False)
            self.stop_bot_btn.setEnabled(True)
            
            self.log("Bot de trading iniciado")
            self.trades_text.append(f"[{datetime.now()}] Bot iniciado\n")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar bot: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao iniciar bot: {e}")
    
    def stop_trading_bot(self):
        """Para o bot de trading"""
        try:
            if self.trading_bot:
                self.trading_bot.stop()
                self.trading_bot = None
            
            self.bot_status_label.setText("Status: Parado")
            self.bot_status_label.setStyleSheet("color: #f44336;")
            self.start_bot_btn.setEnabled(True)
            self.stop_bot_btn.setEnabled(False)
            
            self.log("Bot de trading parado")
            self.trades_text.append(f"[{datetime.now()}] Bot parado\n")
            
        except Exception as e:
            logger.error(f"Erro ao parar bot: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao parar bot: {e}")
    
    def navigate_to_url(self):
        """Navega para URL"""
        url = self.url_input.text()
        if not url.startswith('http'):
            url = 'https://' + url
        self.browser.setUrl(QUrl(url))
    
    def browser_back(self):
        """Volta no navegador"""
        self.browser.back()
    
    def browser_forward(self):
        """Avança no navegador"""
        self.browser.forward()
    
    def browser_refresh(self):
        """Atualiza navegador"""
        self.browser.reload()
    
    def update_url_bar(self, url):
        """Atualiza barra de URL"""
        self.url_input.setText(url.toString())
    
    def toggle_time_limit(self, state):
        """Ativa/desativa limite de tempo"""
        self.time_limit_enabled = (state == Qt.Checked)
        if not self.time_limit_enabled:
            self.time_limit_end = None
            self.log("Limite de tempo desativado")
    
    def update_time_limit_controls(self):
        """Atualiza controles de limite de tempo"""
        limit_type = self.limit_type_combo.currentIndex()
        
        self.duration_widget.setVisible(limit_type == 0)
        self.specific_time_widget.setVisible(limit_type == 1)
        self.daily_period_widget.setVisible(limit_type == 2)
    
    def apply_time_limit(self):
        """Aplica configurações de limite de tempo"""
        try:
            if not self.enable_time_limit_check.isChecked():
                QMessageBox.warning(self, "Aviso", "Habilite o limite de tempo primeiro!")
                return
            
            limit_type = self.limit_type_combo.currentIndex()
            
            if limit_type == 0:  # Duração
                hours = self.duration_hours.value()
                minutes = self.duration_minutes.value()
                seconds = self.duration_seconds.value()
                
                duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                self.time_limit_end = datetime.now() + duration
                
                self.log(f"Limite de tempo configurado: {hours}h {minutes}m {seconds}s")
                QMessageBox.information(
                    self,
                    "Sucesso",
                    f"Programa será encerrado em {hours}h {minutes}m {seconds}s"
                )
                
            elif limit_type == 1:  # Horário específico
                target_datetime = self.specific_datetime.dateTime().toPyDateTime()
                self.time_limit_end = target_datetime
                
                self.log(f"Limite de tempo configurado: até {target_datetime}")
                QMessageBox.information(
                    self,
                    "Sucesso",
                    f"Programa será encerrado em {target_datetime}"
                )
                
            elif limit_type == 2:  # Período diário
                # Implementação simplificada - verifica se está no período
                start_time = self.daily_start_time.time().toPyTime()
                end_time = self.daily_end_time.time().toPyTime()
                
                self.log(f"Período diário configurado: {start_time} - {end_time}")
                QMessageBox.information(
                    self,
                    "Sucesso",
                    f"Programa funcionará apenas entre {start_time} e {end_time}"
                )
            
        except Exception as e:
            logger.error(f"Erro ao aplicar limite: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao aplicar limite: {e}")
    
    def check_time_limit(self):
        """Verifica se o limite de tempo foi atingido"""
        if not self.time_limit_enabled or not self.time_limit_end:
            return
        
        if datetime.now() >= self.time_limit_end:
            self.log("Limite de tempo atingido! Encerrando programa...")
            
            QMessageBox.information(
                self,
                "Limite de Tempo",
                "O limite de tempo foi atingido. O programa será encerrado."
            )
            
            # Para o bot se estiver rodando
            if self.trading_bot:
                self.stop_trading_bot()
            
            # Fecha o programa
            QApplication.quit()
    
    def update_time_display(self):
        """Atualiza display de tempo de execução"""
        elapsed = datetime.now() - self.start_time
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        time_str = f"Tempo de execução: {hours:02d}:{minutes:02d}:{seconds:02d}"
        
        if self.time_limit_enabled and self.time_limit_end:
            remaining = self.time_limit_end - datetime.now()
            if remaining.total_seconds() > 0:
                r_hours, r_remainder = divmod(int(remaining.total_seconds()), 3600)
                r_minutes, r_seconds = divmod(r_remainder, 60)
                time_str += f" | Tempo restante: {r_hours:02d}:{r_minutes:02d}:{r_seconds:02d}"
            else:
                time_str += " | Tempo restante: 00:00:00"
        
        self.time_status_label.setText(time_str)
    
    def log(self, message):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        logger.info(message)
    
    def closeEvent(self, event):
        """Evento de fechamento da janela"""
        # Para o bot se estiver rodando
        if self.trading_bot:
            self.stop_trading_bot()
        
        # Para timers
        self.auto_analysis_timer.stop()
        self.time_limit_timer.stop()
        self.time_display_timer.stop()
        
        event.accept()


def main():
    """Função principal"""
    app = QApplication(sys.argv)
    app.setApplicationName("Market Analyzer")
    
    window = MarketAnalyzerGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
