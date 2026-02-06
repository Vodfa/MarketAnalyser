"""
Script de teste para Market Analyzer
Testa funcionalidades básicas sem GUI
"""

import sys
import logging
from data_provider import DataProvider
from market_analysis import MarketAnalyzer

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_data_provider():
    """Testa o provedor de dados"""
    print("\n" + "="*60)
    print("TESTE 1: Data Provider")
    print("="*60)
    
    try:
        # Inicializa provedor
        provider = DataProvider('binance')
        print("✓ Data Provider inicializado")
        
        # Testa obtenção de mercados
        markets = provider.get_available_markets()
        print(f"✓ Mercados disponíveis: {len(markets)}")
        print(f"  Primeiros 5: {markets[:5]}")
        
        # Testa obtenção de dados OHLCV
        symbol = 'BTC/USDT'
        print(f"\n  Obtendo dados de {symbol}...")
        df = provider.get_ohlcv_data(symbol, '5m', limit=100)
        
        if df is not None and len(df) > 0:
            print(f"✓ Dados obtidos: {len(df)} candles")
            print(f"  Último preço: ${df.iloc[-1]['close']:.2f}")
            return True
        else:
            print("✗ Erro ao obter dados")
            return False
            
    except Exception as e:
        print(f"✗ Erro no teste: {e}")
        return False

def test_market_analyzer():
    """Testa o analisador de mercado"""
    print("\n" + "="*60)
    print("TESTE 2: Market Analyzer")
    print("="*60)
    
    try:
        # Inicializa
        provider = DataProvider('binance')
        analyzer = MarketAnalyzer()
        print("✓ Market Analyzer inicializado")
        
        # Obtém dados
        symbol = 'BTC/USDT'
        df = provider.get_ohlcv_data(symbol, '5m', limit=500)
        
        if df is None or len(df) == 0:
            print("✗ Não foi possível obter dados")
            return False
        
        print(f"✓ Dados obtidos: {len(df)} candles")
        
        # Adiciona indicadores
        print("\n  Calculando indicadores...")
        df = analyzer.populate_indicators(df)
        print("✓ Indicadores calculados")
        
        # Verifica indicadores
        indicators = ['rsi', 'macd', 'bb_upperband', 'ema9', 'adx']
        for ind in indicators:
            if ind in df.columns:
                value = df.iloc[-1][ind]
                print(f"  {ind}: {value:.4f}")
        
        # Gera previsão
        print("\n  Gerando previsão...")
        prediction = analyzer.predict_direction(df)
        
        print("\n" + "-"*60)
        print("RESULTADO DA ANÁLISE")
        print("-"*60)
        print(f"Símbolo: {symbol}")
        print(f"Direção: {prediction['direction']}")
        print(f"Confiança: {prediction['confidence']:.2f}%")
        print(f"Decisão: {prediction['details']['decision']}")
        print(f"Preço Atual: ${prediction['details']['current_price']:.2f}")
        print(f"\nSinais:")
        print(f"  RSI: {prediction['details'].get('rsi_signal', 'N/A')}")
        print(f"  MACD: {prediction['details'].get('macd_signal', 'N/A')}")
        print(f"  Bollinger: {prediction['details'].get('bb_signal', 'N/A')}")
        print(f"  EMA: {prediction['details'].get('ema_signal', 'N/A')}")
        print("-"*60)
        
        return True
        
    except Exception as e:
        print(f"✗ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_manager():
    """Testa o gerenciador de configurações"""
    print("\n" + "="*60)
    print("TESTE 3: Config Manager")
    print("="*60)
    
    try:
        from config_manager import ConfigManager
        
        # Inicializa
        config_mgr = ConfigManager()
        print("✓ Config Manager inicializado")
        
        # Testa salvamento
        test_config = {
            'exchange': 'Binance',
            'exchange_id': 'binance',
            'api_key': 'test_key_123',
            'api_secret': 'test_secret_456',
            'favorite_markets': ['BTC/USDT', 'ETH/USDT']
        }
        
        config_mgr.save_config(test_config)
        print("✓ Configuração salva")
        
        # Testa carregamento
        loaded_config = config_mgr.load_config()
        print("✓ Configuração carregada")
        
        # Verifica se credenciais foram criptografadas/descriptografadas
        if loaded_config['api_key'] == test_config['api_key']:
            print("✓ Criptografia/descriptografia funcionando")
        else:
            print("✗ Erro na criptografia")
            return False
        
        # Limpa credenciais de teste
        config_mgr.clear_credentials()
        print("✓ Credenciais limpas")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("MARKET ANALYZER - SUITE DE TESTES")
    print("="*60)
    
    results = []
    
    # Executa testes
    results.append(("Data Provider", test_data_provider()))
    results.append(("Market Analyzer", test_market_analyzer()))
    results.append(("Config Manager", test_config_manager()))
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    for name, result in results:
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    print("="*60)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
