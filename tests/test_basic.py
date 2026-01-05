"""
基础功能测试
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_manager import DataManager
from src.indicators import TechnicalIndicators
from src.strategy import StrategyFactory, MovingAverageCrossStrategy
from src.backtest import BacktestEngine

class TestDataManager:
    """测试数据管理器"""
    
    def test_import_csv(self, tmp_path):
        """测试CSV导入功能"""
        # 创建测试CSV文件
        test_data = pd.DataFrame({
            'Date': pd.date_range('2023-01-01', periods=10),
            'Open': np.random.uniform(100, 110, 10),
            'High': np.random.uniform(110, 120, 10),
            'Low': np.random.uniform(90, 100, 10),
            'Close': np.random.uniform(100, 110, 10),
            'Volume': np.random.randint(1000000, 2000000, 10)
        })
        
        csv_path = tmp_path / "test_stock.csv"
        test_data.to_csv(csv_path, index=False)
        
        # 测试导入
        dm = DataManager(str(tmp_path))
        success = dm.import_csv(str(csv_path), "TEST")
        
        assert success == True
        
        # 验证数据
        imported_data = dm.get_stock_data("TEST")
        assert imported_data is not None
        assert len(imported_data) == 10
        assert 'Symbol' in imported_data.columns

class TestTechnicalIndicators:
    """测试技术指标"""
    
    def setup_method(self):
        """设置测试数据"""
        self.ti = TechnicalIndicators()
        self.test_data = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])
    
    def test_sma(self):
        """测试简单移动平均线"""
        sma = self.ti.sma(self.test_data, 3)
        
        # 检查前两个值是NaN
        assert pd.isna(sma.iloc[0])
        assert pd.isna(sma.iloc[1])
        
        # 检查第三个值
        expected = (100 + 102 + 101) / 3
        assert abs(sma.iloc[2] - expected) < 0.01
    
    def test_rsi(self):
        """测试RSI指标"""
        rsi = self.ti.rsi(self.test_data, 5)
        
        # RSI应该在0-100之间
        valid_rsi = rsi.dropna()
        assert all(valid_rsi >= 0)
        assert all(valid_rsi <= 100)
    
    def test_advanced_indicators(self):
        """测试高级技术指标"""
        # 创建更长的测试数据
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.normal(0, 1, 100))
        high_prices = prices * 1.02
        low_prices = prices * 0.98
        volumes = np.random.randint(1000000, 2000000, 100)
        
        test_data = pd.DataFrame({
            'High': high_prices,
            'Low': low_prices,
            'Close': prices,
            'Volume': volumes
        })
        
        # 测试ADX
        adx_data = self.ti.adx(test_data['High'], test_data['Low'], test_data['Close'])
        assert 'ADX' in adx_data.columns
        assert '+DI' in adx_data.columns
        assert '-DI' in adx_data.columns
        
        # 测试抛物线SAR
        sar = self.ti.parabolic_sar(test_data['High'], test_data['Low'])
        assert len(sar) == len(test_data)
        
        # 测试肯特纳通道
        kc_data = self.ti.keltner_channels(test_data['High'], test_data['Low'], test_data['Close'])
        assert 'Upper' in kc_data.columns
        assert 'Middle' in kc_data.columns
        assert 'Lower' in kc_data.columns
        
        # 测试成交量指标
        obv = self.ti.obv(test_data['Close'], test_data['Volume'])
        assert len(obv) == len(test_data)
        
        # 测试资金流量指数
        mfi = self.ti.money_flow_index(test_data['High'], test_data['Low'], 
                                      test_data['Close'], test_data['Volume'])
        valid_mfi = mfi.dropna()
        assert all(valid_mfi >= 0)
        assert all(valid_mfi <= 100)
        
        # 测试一目均衡表
        ichimoku_data = self.ti.ichimoku_cloud(test_data['High'], test_data['Low'], test_data['Close'])
        assert 'Tenkan_Sen' in ichimoku_data.columns
        assert 'Kijun_Sen' in ichimoku_data.columns
        assert 'Senkou_Span_A' in ichimoku_data.columns
        assert 'Senkou_Span_B' in ichimoku_data.columns
        assert 'Chikou_Span' in ichimoku_data.columns

class TestStrategy:
    """测试交易策略"""
    
    def setup_method(self):
        """设置测试数据"""
        self.test_data = pd.DataFrame({
            'Date': pd.date_range('2023-01-01', periods=50),
            'Open': np.random.uniform(100, 110, 50),
            'High': np.random.uniform(110, 120, 50),
            'Low': np.random.uniform(90, 100, 50),
            'Close': np.random.uniform(100, 110, 50),
            'Volume': np.random.randint(1000000, 2000000, 50)
        })
    
    def test_moving_average_strategy(self):
        """测试移动平均策略"""
        strategy = MovingAverageCrossStrategy(short_window=5, long_window=10)
        result = strategy.generate_signals(self.test_data)
        
        # 检查必要的列
        assert 'Signal' in result.columns
        assert 'Position' in result.columns
        assert 'Buy' in result.columns
        assert 'Sell' in result.columns
        assert 'SMA_Short' in result.columns
        assert 'SMA_Long' in result.columns
    
    def test_strategy_factory(self):
        """测试策略工厂"""
        # 测试获取策略
        strategy = StrategyFactory.get_strategy('ma_cross', short_window=5, long_window=20)
        assert strategy.name == "移动平均交叉策略"
        
        # 测试列出策略
        strategies = StrategyFactory.list_strategies()
        assert 'ma_cross' in strategies
        assert 'rsi' in strategies
        
        # 测试策略信息
        info = StrategyFactory.get_strategy_info()
        assert 'ma_cross' in info
        assert 'name' in info['ma_cross']

class TestBacktest:
    """测试回测引擎"""
    
    def setup_method(self):
        """设置测试数据"""
        # 创建上升趋势的测试数据
        dates = pd.date_range('2023-01-01', periods=100)
        prices = 100 + np.cumsum(np.random.normal(0.1, 1, 100))
        
        self.test_data = pd.DataFrame({
            'Date': dates,
            'Open': prices,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Close': prices,
            'Volume': np.random.randint(1000000, 2000000, 100)
        })
    
    def test_backtest_run(self):
        """测试回测运行"""
        strategy = MovingAverageCrossStrategy(short_window=5, long_window=20)
        backtest = BacktestEngine(initial_capital=10000, commission=0.001)
        
        result = backtest.run(self.test_data, strategy)
        
        # 检查结果结构
        assert 'strategy_name' in result
        assert 'metrics' in result
        assert 'data' in result
        assert 'trades' in result
        assert 'initial_capital' in result
        assert 'final_capital' in result
        
        # 检查指标
        metrics = result['metrics']
        assert 'total_return' in metrics
        assert 'sharpe_ratio' in metrics
        assert 'max_drawdown' in metrics
        
        # 检查数据
        data = result['data']
        assert 'Portfolio_Value' in data.columns
        assert 'Holdings' in data.columns
        assert 'Cash' in data.columns

def test_integration():
    """集成测试"""
    # 创建测试数据
    test_data = pd.DataFrame({
        'Date': pd.date_range('2023-01-01', periods=100),
        'Open': np.random.uniform(100, 110, 100),
        'High': np.random.uniform(110, 120, 100),
        'Low': np.random.uniform(90, 100, 100),
        'Close': np.random.uniform(100, 110, 100),
        'Volume': np.random.randint(1000000, 2000000, 100)
    })
    
    # 创建策略
    strategy = StrategyFactory.get_strategy('ma_cross', short_window=5, long_window=20)
    
    # 运行回测
    backtest = BacktestEngine(10000, 0.001)
    result = backtest.run(test_data, strategy)
    
    # 验证结果
    assert result['initial_capital'] == 10000
    assert result['final_capital'] > 0
    assert isinstance(result['trades'], list)

if __name__ == "__main__":
    pytest.main([__file__])