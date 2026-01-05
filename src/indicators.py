"""
技术指标计算模块
包含常用的技术分析指标
"""

import pandas as pd
import numpy as np
from typing import Union

class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def sma(data: pd.Series, window: int) -> pd.Series:
        """简单移动平均线 (Simple Moving Average)
        
        Args:
            data: 价格数据
            window: 窗口期
            
        Returns:
            SMA序列
        """
        return data.rolling(window=window).mean()
    
    @staticmethod
    def ema(data: pd.Series, window: int) -> pd.Series:
        """指数移动平均线 (Exponential Moving Average)
        
        Args:
            data: 价格数据
            window: 窗口期
            
        Returns:
            EMA序列
        """
        return data.ewm(span=window).mean()
    
    @staticmethod
    def rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """相对强弱指数 (Relative Strength Index)
        
        Args:
            data: 价格数据
            window: 窗口期，默认14
            
        Returns:
            RSI序列
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """MACD指标 (Moving Average Convergence Divergence)
        
        Args:
            data: 价格数据
            fast: 快线周期，默认12
            slow: 慢线周期，默认26
            signal: 信号线周期，默认9
            
        Returns:
            包含MACD, Signal, Histogram的DataFrame
        """
        ema_fast = data.ewm(span=fast).mean()
        ema_slow = data.ewm(span=slow).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return pd.DataFrame({
            'MACD': macd_line,
            'Signal': signal_line,
            'Histogram': histogram
        })
    
    @staticmethod
    def bollinger_bands(data: pd.Series, window: int = 20, std_dev: float = 2) -> pd.DataFrame:
        """布林带 (Bollinger Bands)
        
        Args:
            data: 价格数据
            window: 窗口期，默认20
            std_dev: 标准差倍数，默认2
            
        Returns:
            包含Upper, Middle, Lower的DataFrame
        """
        middle = data.rolling(window=window).mean()
        std = data.rolling(window=window).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return pd.DataFrame({
            'Upper': upper,
            'Middle': middle,
            'Lower': lower
        })
    
    @staticmethod
    def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
                   k_window: int = 14, d_window: int = 3) -> pd.DataFrame:
        """随机指标 (Stochastic Oscillator)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            k_window: %K窗口期，默认14
            d_window: %D窗口期，默认3
            
        Returns:
            包含%K, %D的DataFrame
        """
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_window).mean()
        
        return pd.DataFrame({
            '%K': k_percent,
            '%D': d_percent
        })
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """平均真实波幅 (Average True Range)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            window: 窗口期，默认14
            
        Returns:
            ATR序列
        """
        prev_close = close.shift(1)
        
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=window).mean()
        
        return atr
    
    @staticmethod
    def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """威廉指标 (Williams %R)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            window: 窗口期，默认14
            
        Returns:
            Williams %R序列
        """
        highest_high = high.rolling(window=window).max()
        lowest_low = low.rolling(window=window).min()
        
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        
        return williams_r
    
    @staticmethod
    def add_all_indicators(data: pd.DataFrame) -> pd.DataFrame:
        """为数据添加所有技术指标
        
        Args:
            data: 包含OHLCV的DataFrame
            
        Returns:
            添加了所有技术指标的DataFrame
        """
        df = data.copy()
        ti = TechnicalIndicators()
        
        # 移动平均线
        df['SMA_5'] = ti.sma(df['Close'], 5)
        df['SMA_10'] = ti.sma(df['Close'], 10)
        df['SMA_20'] = ti.sma(df['Close'], 20)
        df['SMA_50'] = ti.sma(df['Close'], 50)
        
        df['EMA_12'] = ti.ema(df['Close'], 12)
        df['EMA_26'] = ti.ema(df['Close'], 26)
        
        # RSI
        df['RSI'] = ti.rsi(df['Close'])
        
        # MACD
        macd_data = ti.macd(df['Close'])
        df['MACD'] = macd_data['MACD']
        df['MACD_Signal'] = macd_data['Signal']
        df['MACD_Histogram'] = macd_data['Histogram']
        
        # 布林带
        bb_data = ti.bollinger_bands(df['Close'])
        df['BB_Upper'] = bb_data['Upper']
        df['BB_Middle'] = bb_data['Middle']
        df['BB_Lower'] = bb_data['Lower']
        
        # 随机指标
        stoch_data = ti.stochastic(df['High'], df['Low'], df['Close'])
        df['Stoch_K'] = stoch_data['%K']
        df['Stoch_D'] = stoch_data['%D']
        
        # ATR
        df['ATR'] = ti.atr(df['High'], df['Low'], df['Close'])
        
        # Williams %R
        df['Williams_R'] = ti.williams_r(df['High'], df['Low'], df['Close'])
        
        return df