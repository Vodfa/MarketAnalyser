"""
Config Manager Module
Gerenciamento seguro de configurações e credenciais
"""

import json
import os
from typing import Dict, Any
from pathlib import Path
import logging
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Gerenciador de configurações com criptografia de credenciais
    """
    
    def __init__(self, config_dir: str = None):
        """
        Inicializa o gerenciador de configurações
        
        Args:
            config_dir: Diretório para armazenar configurações
        """
        if config_dir is None:
            # Usa diretório do usuário
            self.config_dir = Path.home() / '.market_analyzer'
        else:
            self.config_dir = Path(config_dir)
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / 'config.json'
        self.key_file = self.config_dir / '.key'
        
        self._ensure_key()
        self.cipher = self._load_cipher()
    
    def _ensure_key(self):
        """Garante que existe uma chave de criptografia"""
        if not self.key_file.exists():
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Torna o arquivo oculto no Windows
            if os.name == 'nt':
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(str(self.key_file), 2)
    
    def _load_cipher(self) -> Fernet:
        """Carrega cipher para criptografia"""
        with open(self.key_file, 'rb') as f:
            key = f.read()
        return Fernet(key)
    
    def _encrypt(self, data: str) -> str:
        """Criptografa dados"""
        if not data:
            return ''
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def _decrypt(self, data: str) -> str:
        """Descriptografa dados"""
        if not data:
            return ''
        try:
            decoded = base64.b64decode(data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Erro ao descriptografar: {e}")
            return ''
    
    def save_config(self, config: Dict[str, Any]):
        """
        Salva configurações
        
        Args:
            config: Dicionário com configurações
        """
        try:
            # Criptografa credenciais sensíveis
            safe_config = config.copy()
            
            if 'api_key' in safe_config and safe_config['api_key']:
                safe_config['api_key'] = self._encrypt(safe_config['api_key'])
            
            if 'api_secret' in safe_config and safe_config['api_secret']:
                safe_config['api_secret'] = self._encrypt(safe_config['api_secret'])
            
            # Salva em arquivo
            with open(self.config_file, 'w') as f:
                json.dump(safe_config, f, indent=4)
            
            logger.info("Configurações salvas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            raise
    
    def load_config(self) -> Dict[str, Any]:
        """
        Carrega configurações
        
        Returns:
            Dicionário com configurações
        """
        try:
            if not self.config_file.exists():
                # Retorna configuração padrão
                return self._get_default_config()
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Descriptografa credenciais
            if 'api_key' in config and config['api_key']:
                config['api_key'] = self._decrypt(config['api_key'])
            
            if 'api_secret' in config and config['api_secret']:
                config['api_secret'] = self._decrypt(config['api_secret'])
            
            logger.info("Configurações carregadas com sucesso")
            
            return config
            
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão"""
        return {
            'exchange': 'Binance',
            'exchange_id': 'binance',
            'api_key': '',
            'api_secret': '',
            'favorite_markets': [
                'BTC/USDT',
                'ETH/USDT',
                'BNB/USDT',
                'SOL/USDT',
                'XRP/USDT'
            ],
            'default_timeframe': '5m',
            'auto_analysis_interval': 60,
            'enable_trading': False,
            'max_trades': 3,
            'trade_amount': 100,
            'stop_loss_percent': 2.0,
            'take_profit_percent': 5.0
        }
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor de configuração específico
        
        Args:
            key: Chave da configuração
            default: Valor padrão se não encontrado
            
        Returns:
            Valor da configuração
        """
        config = self.load_config()
        return config.get(key, default)
    
    def set_config_value(self, key: str, value: Any):
        """
        Define valor de configuração específico
        
        Args:
            key: Chave da configuração
            value: Valor a definir
        """
        config = self.load_config()
        config[key] = value
        self.save_config(config)
    
    def clear_credentials(self):
        """Remove credenciais armazenadas"""
        config = self.load_config()
        config['api_key'] = ''
        config['api_secret'] = ''
        self.save_config(config)
        logger.info("Credenciais removidas")
    
    def export_config(self, export_path: str):
        """
        Exporta configurações (sem credenciais) para arquivo
        
        Args:
            export_path: Caminho do arquivo de exportação
        """
        try:
            config = self.load_config()
            
            # Remove credenciais sensíveis
            export_config = config.copy()
            export_config['api_key'] = ''
            export_config['api_secret'] = ''
            
            with open(export_path, 'w') as f:
                json.dump(export_config, f, indent=4)
            
            logger.info(f"Configurações exportadas para {export_path}")
            
        except Exception as e:
            logger.error(f"Erro ao exportar configurações: {e}")
            raise
    
    def import_config(self, import_path: str):
        """
        Importa configurações de arquivo
        
        Args:
            import_path: Caminho do arquivo de importação
        """
        try:
            with open(import_path, 'r') as f:
                config = json.load(f)
            
            # Mantém credenciais existentes
            current_config = self.load_config()
            config['api_key'] = current_config.get('api_key', '')
            config['api_secret'] = current_config.get('api_secret', '')
            
            self.save_config(config)
            
            logger.info(f"Configurações importadas de {import_path}")
            
        except Exception as e:
            logger.error(f"Erro ao importar configurações: {e}")
            raise
