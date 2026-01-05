"""
交易策略模块
包含各种经典的量化交易策略
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
from .indicators import TechnicalIndicators

class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.ti = TechnicalIndicators()
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号
        
        Args:
            data: 股票数据
            
        Returns:
            包含信号的DataFrame
        """
        pass
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取策略参数"""
        return {}

class MovingAverageCrossStrategy(BaseStrategy):
    """移动平均交叉策略"""
    
    def __init__(self, short_window: int = 5, long_window: int = 20):
        super().__init__("移动平均交叉策略")
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成移动平均交叉信号"""
        df = data.copy()
        
        # 计算移动平均线
        df['SMA_Short'] = self.ti.sma(df['Close'], self.short_window)
        df['SMA_Long'] = self.ti.sma(df['Close'], self.long_window)
        
        # 生成信号
        df['Signal'] = 0
        df['Position'] = 0
        
        # 当短期均线上穿长期均线时买入
        df.loc[df['SMA_Short'] > df['SMA_Long'], 'Signal'] = 1
        # 当短期均线下穿长期均线时卖出
        df.loc[df['SMA_Short'] < df['SMA_Long'], 'Signal'] = -1
        
        # 计算持仓
        df['Position'] = df['Signal'].replace(to_replace=0, method='ffill').fillna(0)
        
        # 标记买卖点
        df['Buy'] = (df['Signal'] == 1) & (df['Signal'].shift(1) != 1)
        df['Sell'] = (df['Signal'] == -1) & (df['Signal'].shift(1) != -1)
        
        return df
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'short_window': self.short_window,
            'long_window': self.long_window
        }

class RSIStrategy(BaseStrategy):
    """RSI超买超卖策略"""
    
    def __init__(self, rsi_window: int = 14, oversold: float = 30, overbought: float = 70):
        super().__init__("RSI超买超卖策略")
        self.rsi_window = rsi_window
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成RSI信号"""
        df = data.copy()
        
        # 计算RSI
        df['RSI'] = self.ti.rsi(df['Close'], self.rsi_window)
        
        # 生成信号
        df['Signal'] = 0
        df['Position'] = 0
        
        # RSI < 30 时买入（超卖）
        df.loc[df['RSI'] < self.oversold, 'Signal'] = 1
        # RSI > 70 时卖出（超买）
        df.loc[df['RSI'] > self.overbought, 'Signal'] = -1
        
        # 计算持仓
        df['Position'] = df['Signal'].replace(to_replace=0, method='ffill').fillna(0)
        
        # 标记买卖点
        df['Buy'] = (df['Signal'] == 1) & (df['Signal'].shift(1) != 1)
        df['Sell'] = (df['Signal'] == -1) & (df['Signal'].shift(1) != -1)
        
        return df
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'rsi_window': self.rsi_window,
            'oversold': self.oversold,
            'overbought': self.overbought
        }

class MACDStrategy(BaseStrategy):
    """MACD金叉死叉策略"""
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        super().__init__("MACD金叉死叉策略")
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成MACD信号"""
        df = data.copy()
        
        # 计算MACD
        macd_data = self.ti.macd(df['Close'], self.fast, self.slow, self.signal)
        df['MACD'] = macd_data['MACD']
        df['MACD_Signal'] = macd_data['Signal']
        df['MACD_Histogram'] = macd_data['Histogram']
        
        # 生成信号
        df['Signal'] = 0
        df['Position'] = 0
        
        # MACD线上穿信号线时买入（金叉）
        df.loc[df['MACD'] > df['MACD_Signal'], 'Signal'] = 1
        # MACD线下穿信号线时卖出（死叉）
        df.loc[df['MACD'] < df['MACD_Signal'], 'Signal'] = -1
        
        # 计算持仓
        df['Position'] = df['Signal'].replace(to_replace=0, method='ffill').fillna(0)
        
        # 标记买卖点
        df['Buy'] = (df['Signal'] == 1) & (df['Signal'].shift(1) != 1)
        df['Sell'] = (df['Signal'] == -1) & (df['Signal'].shift(1) != -1)
        
        return df
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'fast': self.fast,
            'slow': self.slow,
            'signal': self.signal
        }

class BollingerBandsStrategy(BaseStrategy):
    """布林带突破策略"""
    
    def __init__(self, window: int = 20, std_dev: float = 2):
        super().__init__("布林带突破策略")
        self.window = window
        self.std_dev = std_dev
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成布林带信号"""
        df = data.copy()
        
        # 计算布林带
        bb_data = self.ti.bollinger_bands(df['Close'], self.window, self.std_dev)
        df['BB_Upper'] = bb_data['Upper']
        df['BB_Middle'] = bb_data['Middle']
        df['BB_Lower'] = bb_data['Lower']
        
        # 生成信号
        df['Signal'] = 0
        df['Position'] = 0
        
        # 价格跌破下轨时买入
        df.loc[df['Close'] < df['BB_Lower'], 'Signal'] = 1
        # 价格突破上轨时卖出
        df.loc[df['Close'] > df['BB_Upper'], 'Signal'] = -1
        
        # 计算持仓
        df['Position'] = df['Signal'].replace(to_replace=0, method='ffill').fillna(0)
        
        # 标记买卖点
        df['Buy'] = (df['Signal'] == 1) & (df['Signal'].shift(1) != 1)
        df['Sell'] = (df['Signal'] == -1) & (df['Signal'].shift(1) != -1)
        
        return df
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'window': self.window,
            'std_dev': self.std_dev
        }

class StrategyFactory:
    """策略工厂类"""
    
    @staticmethod
    def get_strategy(strategy_name: str, **kwargs) -> BaseStrategy:
        """获取策略实例
        
        Args:
            strategy_name: 策略名称
            **kwargs: 策略参数
            
        Returns:
            策略实例
        """
        strategies = {
            'ma_cross': MovingAverageCrossStrategy,
            'rsi': RSIStrategy,
            'macd': MACDStrategy,
            'bollinger': BollingerBandsStrategy
        }
        
        if strategy_name not in strategies:
            raise ValueError(f"未知的策略: {strategy_name}")
        
        return strategies[strategy_name](**kwargs)
    
    @staticmethod
    def list_strategies() -> List[str]:
        """列出所有可用策略"""
        return ['ma_cross', 'rsi', 'macd', 'bollinger']
    
    @staticmethod
    def get_strategy_info() -> Dict[str, Dict[str, Any]]:
        """获取所有策略信息"""
        return {
            'ma_cross': {
                'name': '移动平均交叉策略',
                'description': '基于短期和长期移动平均线的交叉信号',
                'parameters': {
                    'short_window': {'type': 'int', 'default': 5, 'description': '短期窗口'},
                    'long_window': {'type': 'int', 'default': 20, 'description': '长期窗口'}
                }
            },
            'rsi': {
                'name': 'RSI超买超卖策略',
                'description': '基于RSI指标的超买超卖信号',
                'parameters': {
                    'rsi_window': {'type': 'int', 'default': 14, 'description': 'RSI窗口'},
                    'oversold': {'type': 'float', 'default': 30, 'description': '超卖阈值'},
                    'overbought': {'type': 'float', 'default': 70, 'description': '超买阈值'}
                }
            },
            'macd': {
                'name': 'MACD金叉死叉策略',
                'description': '基于MACD指标的金叉死叉信号',
                'parameters': {
                    'fast': {'type': 'int', 'default': 12, 'description': '快线周期'},
                    'slow': {'type': 'int', 'default': 26, 'description': '慢线周期'},
                    'signal': {'type': 'int', 'default': 9, 'description': '信号线周期'}
                }
            },
            'bollinger': {
                'name': '布林带突破策略',
                'description': '基于布林带上下轨的突破信号',
                'parameters': {
                    'window': {'type': 'int', 'default': 20, 'description': '窗口期'},
                    'std_dev': {'type': 'float', 'default': 2, 'description': '标准差倍数'}
                }
            }
        }