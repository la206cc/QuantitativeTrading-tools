"""
技术指标计算模块
包含常用的技术分析指标
"""

import pandas as pd
import numpy as np
from typing import Union, Tuple

class TechnicalIndicators:
    """技术指标计算器"""
    
    # ==================== 趋势指标 ====================
    
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
    def wma(data: pd.Series, window: int) -> pd.Series:
        """加权移动平均线 (Weighted Moving Average)
        
        Args:
            data: 价格数据
            window: 窗口期
            
        Returns:
            WMA序列
        """
        weights = np.arange(1, window + 1)
        return data.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    
    @staticmethod
    def dema(data: pd.Series, window: int) -> pd.Series:
        """双指数移动平均线 (Double Exponential Moving Average)
        
        Args:
            data: 价格数据
            window: 窗口期
            
        Returns:
            DEMA序列
        """
        ema1 = data.ewm(span=window).mean()
        ema2 = ema1.ewm(span=window).mean()
        return 2 * ema1 - ema2
    
    @staticmethod
    def tema(data: pd.Series, window: int) -> pd.Series:
        """三重指数移动平均线 (Triple Exponential Moving Average)
        
        Args:
            data: 价格数据
            window: 窗口期
            
        Returns:
            TEMA序列
        """
        ema1 = data.ewm(span=window).mean()
        ema2 = ema1.ewm(span=window).mean()
        ema3 = ema2.ewm(span=window).mean()
        return 3 * ema1 - 3 * ema2 + ema3
    
    @staticmethod
    def kama(data: pd.Series, window: int = 10, fast_sc: int = 2, slow_sc: int = 30) -> pd.Series:
        """考夫曼自适应移动平均线 (Kaufman's Adaptive Moving Average)
        
        Args:
            data: 价格数据
            window: 效率比率窗口期
            fast_sc: 快速平滑常数
            slow_sc: 慢速平滑常数
            
        Returns:
            KAMA序列
        """
        change = abs(data - data.shift(window))
        volatility = abs(data.diff()).rolling(window).sum()
        
        # 效率比率
        er = change / volatility
        
        # 平滑常数
        fast_alpha = 2 / (fast_sc + 1)
        slow_alpha = 2 / (slow_sc + 1)
        sc = (er * (fast_alpha - slow_alpha) + slow_alpha) ** 2
        
        # KAMA计算
        kama = pd.Series(index=data.index, dtype=float)
        kama.iloc[window] = data.iloc[window]
        
        for i in range(window + 1, len(data)):
            kama.iloc[i] = kama.iloc[i-1] + sc.iloc[i] * (data.iloc[i] - kama.iloc[i-1])
        
        return kama
    
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
    def adx(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.DataFrame:
        """平均趋向指数 (Average Directional Index)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            window: 窗口期，默认14
            
        Returns:
            包含ADX, +DI, -DI的DataFrame
        """
        # 计算真实波幅
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # 计算方向移动
        dm_plus = np.where((high - high.shift(1)) > (low.shift(1) - low), 
                          np.maximum(high - high.shift(1), 0), 0)
        dm_minus = np.where((low.shift(1) - low) > (high - high.shift(1)), 
                           np.maximum(low.shift(1) - low, 0), 0)
        
        dm_plus = pd.Series(dm_plus, index=high.index)
        dm_minus = pd.Series(dm_minus, index=low.index)
        
        # 平滑处理
        atr = tr.rolling(window).mean()
        di_plus = 100 * (dm_plus.rolling(window).mean() / atr)
        di_minus = 100 * (dm_minus.rolling(window).mean() / atr)
        
        # 计算ADX
        dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
        adx = dx.rolling(window).mean()
        
        return pd.DataFrame({
            'ADX': adx,
            '+DI': di_plus,
            '-DI': di_minus
        })
    
    @staticmethod
    def parabolic_sar(high: pd.Series, low: pd.Series, af_start: float = 0.02, 
                      af_increment: float = 0.02, af_max: float = 0.2) -> pd.Series:
        """抛物线SAR (Parabolic Stop and Reverse)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            af_start: 初始加速因子
            af_increment: 加速因子增量
            af_max: 最大加速因子
            
        Returns:
            SAR序列
        """
        sar = pd.Series(index=high.index, dtype=float)
        trend = pd.Series(index=high.index, dtype=int)  # 1为上升，-1为下降
        af = pd.Series(index=high.index, dtype=float)
        ep = pd.Series(index=high.index, dtype=float)  # 极值点
        
        # 初始化
        sar.iloc[0] = low.iloc[0]
        trend.iloc[0] = 1
        af.iloc[0] = af_start
        ep.iloc[0] = high.iloc[0]
        
        for i in range(1, len(high)):
            if trend.iloc[i-1] == 1:  # 上升趋势
                sar.iloc[i] = sar.iloc[i-1] + af.iloc[i-1] * (ep.iloc[i-1] - sar.iloc[i-1])
                
                if low.iloc[i] <= sar.iloc[i]:  # 趋势反转
                    trend.iloc[i] = -1
                    sar.iloc[i] = ep.iloc[i-1]
                    af.iloc[i] = af_start
                    ep.iloc[i] = low.iloc[i]
                else:
                    trend.iloc[i] = 1
                    if high.iloc[i] > ep.iloc[i-1]:
                        ep.iloc[i] = high.iloc[i]
                        af.iloc[i] = min(af.iloc[i-1] + af_increment, af_max)
                    else:
                        ep.iloc[i] = ep.iloc[i-1]
                        af.iloc[i] = af.iloc[i-1]
            else:  # 下降趋势
                sar.iloc[i] = sar.iloc[i-1] + af.iloc[i-1] * (ep.iloc[i-1] - sar.iloc[i-1])
                
                if high.iloc[i] >= sar.iloc[i]:  # 趋势反转
                    trend.iloc[i] = 1
                    sar.iloc[i] = ep.iloc[i-1]
                    af.iloc[i] = af_start
                    ep.iloc[i] = high.iloc[i]
                else:
                    trend.iloc[i] = -1
                    if low.iloc[i] < ep.iloc[i-1]:
                        ep.iloc[i] = low.iloc[i]
                        af.iloc[i] = min(af.iloc[i-1] + af_increment, af_max)
                    else:
                        ep.iloc[i] = ep.iloc[i-1]
                        af.iloc[i] = af.iloc[i-1]
        
        return sar
    
    # ==================== 动量指标 ====================
    
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
    def roc(data: pd.Series, window: int = 12) -> pd.Series:
        """变动率指标 (Rate of Change)
        
        Args:
            data: 价格数据
            window: 窗口期，默认12
            
        Returns:
            ROC序列
        """
        return ((data - data.shift(window)) / data.shift(window)) * 100
    
    @staticmethod
    def momentum(data: pd.Series, window: int = 10) -> pd.Series:
        """动量指标 (Momentum)
        
        Args:
            data: 价格数据
            window: 窗口期，默认10
            
        Returns:
            动量序列
        """
        return data - data.shift(window)
    
    @staticmethod
    def cci(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 20) -> pd.Series:
        """商品通道指数 (Commodity Channel Index)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            window: 窗口期，默认20
            
        Returns:
            CCI序列
        """
        typical_price = (high + low + close) / 3
        sma_tp = typical_price.rolling(window).mean()
        mad = typical_price.rolling(window).apply(lambda x: np.mean(np.abs(x - x.mean())))
        
        cci = (typical_price - sma_tp) / (0.015 * mad)
        return cci
    
    @staticmethod
    def ultimate_oscillator(high: pd.Series, low: pd.Series, close: pd.Series,
                           period1: int = 7, period2: int = 14, period3: int = 28) -> pd.Series:
        """终极振荡器 (Ultimate Oscillator)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period1: 短期周期，默认7
            period2: 中期周期，默认14
            period3: 长期周期，默认28
            
        Returns:
            UO序列
        """
        prev_close = close.shift(1)
        
        # 买压 = 收盘价 - min(最低价, 前收盘价)
        buying_pressure = close - np.minimum(low, prev_close)
        
        # 真实波幅 = max(最高价, 前收盘价) - min(最低价, 前收盘价)
        true_range = np.maximum(high, prev_close) - np.minimum(low, prev_close)
        
        # 计算各周期的平均值
        bp1 = buying_pressure.rolling(period1).sum()
        tr1 = true_range.rolling(period1).sum()
        
        bp2 = buying_pressure.rolling(period2).sum()
        tr2 = true_range.rolling(period2).sum()
        
        bp3 = buying_pressure.rolling(period3).sum()
        tr3 = true_range.rolling(period3).sum()
        
        # 终极振荡器
        uo = 100 * ((4 * bp1/tr1) + (2 * bp2/tr2) + (bp3/tr3)) / (4 + 2 + 1)
        
        return uo
    
    # ==================== 波动率指标 ====================
    
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
    def keltner_channels(high: pd.Series, low: pd.Series, close: pd.Series, 
                        window: int = 20, multiplier: float = 2) -> pd.DataFrame:
        """肯特纳通道 (Keltner Channels)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            window: 窗口期，默认20
            multiplier: ATR倍数，默认2
            
        Returns:
            包含Upper, Middle, Lower的DataFrame
        """
        middle = close.rolling(window).mean()
        atr_val = TechnicalIndicators.atr(high, low, close, window)
        
        upper = middle + (multiplier * atr_val)
        lower = middle - (multiplier * atr_val)
        
        return pd.DataFrame({
            'Upper': upper,
            'Middle': middle,
            'Lower': lower
        })
    
    @staticmethod
    def donchian_channels(high: pd.Series, low: pd.Series, window: int = 20) -> pd.DataFrame:
        """唐奇安通道 (Donchian Channels)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            window: 窗口期，默认20
            
        Returns:
            包含Upper, Middle, Lower的DataFrame
        """
        upper = high.rolling(window).max()
        lower = low.rolling(window).min()
        middle = (upper + lower) / 2
        
        return pd.DataFrame({
            'Upper': upper,
            'Middle': middle,
            'Lower': lower
        })
    
    @staticmethod
    def volatility(data: pd.Series, window: int = 20) -> pd.Series:
        """历史波动率 (Historical Volatility)
        
        Args:
            data: 价格数据
            window: 窗口期，默认20
            
        Returns:
            波动率序列
        """
        returns = data.pct_change()
        volatility = returns.rolling(window).std() * np.sqrt(252)  # 年化波动率
        return volatility
    
    # ==================== 成交量指标 ====================
    
    @staticmethod
    def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """能量潮指标 (On-Balance Volume)
        
        Args:
            close: 收盘价序列
            volume: 成交量序列
            
        Returns:
            OBV序列
        """
        price_change = close.diff()
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if price_change.iloc[i] > 0:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif price_change.iloc[i] < 0:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    @staticmethod
    def ad_line(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
        """累积/派发线 (Accumulation/Distribution Line)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            volume: 成交量序列
            
        Returns:
            A/D Line序列
        """
        clv = ((close - low) - (high - close)) / (high - low)
        clv = clv.fillna(0)  # 处理high=low的情况
        
        ad_line = (clv * volume).cumsum()
        return ad_line
    
    @staticmethod
    def chaikin_oscillator(high: pd.Series, low: pd.Series, close: pd.Series, 
                          volume: pd.Series, fast: int = 3, slow: int = 10) -> pd.Series:
        """蔡金振荡器 (Chaikin Oscillator)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            volume: 成交量序列
            fast: 快速EMA周期，默认3
            slow: 慢速EMA周期，默认10
            
        Returns:
            蔡金振荡器序列
        """
        ad = TechnicalIndicators.ad_line(high, low, close, volume)
        
        ema_fast = ad.ewm(span=fast).mean()
        ema_slow = ad.ewm(span=slow).mean()
        
        chaikin_osc = ema_fast - ema_slow
        return chaikin_osc
    
    @staticmethod
    def volume_sma(volume: pd.Series, window: int = 20) -> pd.Series:
        """成交量移动平均线 (Volume SMA)
        
        Args:
            volume: 成交量序列
            window: 窗口期，默认20
            
        Returns:
            成交量SMA序列
        """
        return volume.rolling(window).mean()
    
    @staticmethod
    def vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
        """成交量加权平均价 (Volume Weighted Average Price)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            volume: 成交量序列
            
        Returns:
            VWAP序列
        """
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap
    
    # ==================== 市场强度指标 ====================
    
    @staticmethod
    def money_flow_index(high: pd.Series, low: pd.Series, close: pd.Series, 
                        volume: pd.Series, window: int = 14) -> pd.Series:
        """资金流量指数 (Money Flow Index)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            volume: 成交量序列
            window: 窗口期，默认14
            
        Returns:
            MFI序列
        """
        typical_price = (high + low + close) / 3
        money_flow = typical_price * volume
        
        price_change = typical_price.diff()
        
        positive_flow = money_flow.where(price_change > 0, 0).rolling(window).sum()
        negative_flow = money_flow.where(price_change < 0, 0).rolling(window).sum()
        
        money_ratio = positive_flow / abs(negative_flow)
        mfi = 100 - (100 / (1 + money_ratio))
        
        return mfi
    
    @staticmethod
    def ease_of_movement(high: pd.Series, low: pd.Series, volume: pd.Series, 
                        window: int = 14) -> pd.Series:
        """简易波动指标 (Ease of Movement)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            volume: 成交量序列
            window: 窗口期，默认14
            
        Returns:
            EMV序列
        """
        distance_moved = ((high + low) / 2) - ((high.shift(1) + low.shift(1)) / 2)
        box_height = (volume / 100000000) / (high - low)
        
        emv = distance_moved / box_height
        emv_sma = emv.rolling(window).mean()
        
        return emv_sma
    
    # ==================== 综合指标 ====================
    
    @staticmethod
    def ichimoku_cloud(high: pd.Series, low: pd.Series, close: pd.Series,
                      tenkan_period: int = 9, kijun_period: int = 26, 
                      senkou_period: int = 52) -> pd.DataFrame:
        """一目均衡表 (Ichimoku Cloud)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            tenkan_period: 转换线周期，默认9
            kijun_period: 基准线周期，默认26
            senkou_period: 先行带周期，默认52
            
        Returns:
            包含各线的DataFrame
        """
        # 转换线 (Tenkan-sen)
        tenkan_sen = (high.rolling(tenkan_period).max() + low.rolling(tenkan_period).min()) / 2
        
        # 基准线 (Kijun-sen)
        kijun_sen = (high.rolling(kijun_period).max() + low.rolling(kijun_period).min()) / 2
        
        # 先行带A (Senkou Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun_period)
        
        # 先行带B (Senkou Span B)
        senkou_span_b = ((high.rolling(senkou_period).max() + 
                         low.rolling(senkou_period).min()) / 2).shift(kijun_period)
        
        # 滞后线 (Chikou Span)
        chikou_span = close.shift(-kijun_period)
        
        return pd.DataFrame({
            'Tenkan_Sen': tenkan_sen,
            'Kijun_Sen': kijun_sen,
            'Senkou_Span_A': senkou_span_a,
            'Senkou_Span_B': senkou_span_b,
            'Chikou_Span': chikou_span
        })
    
    @staticmethod
    def aroon(high: pd.Series, low: pd.Series, window: int = 14) -> pd.DataFrame:
        """阿隆指标 (Aroon)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            window: 窗口期，默认14
            
        Returns:
            包含Aroon Up, Aroon Down, Aroon Oscillator的DataFrame
        """
        aroon_up = pd.Series(index=high.index, dtype=float)
        aroon_down = pd.Series(index=low.index, dtype=float)
        
        for i in range(window, len(high)):
            high_period = high.iloc[i-window+1:i+1]
            low_period = low.iloc[i-window+1:i+1]
            
            periods_since_high = window - 1 - high_period.argmax()
            periods_since_low = window - 1 - low_period.argmin()
            
            aroon_up.iloc[i] = ((window - periods_since_high) / window) * 100
            aroon_down.iloc[i] = ((window - periods_since_low) / window) * 100
        
        aroon_oscillator = aroon_up - aroon_down
        
        return pd.DataFrame({
            'Aroon_Up': aroon_up,
            'Aroon_Down': aroon_down,
            'Aroon_Oscillator': aroon_oscillator
        })
    
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
        
        # 趋势指标
        df['SMA_5'] = ti.sma(df['Close'], 5)
        df['SMA_10'] = ti.sma(df['Close'], 10)
        df['SMA_20'] = ti.sma(df['Close'], 20)
        df['SMA_50'] = ti.sma(df['Close'], 50)
        
        df['EMA_12'] = ti.ema(df['Close'], 12)
        df['EMA_26'] = ti.ema(df['Close'], 26)
        df['WMA_20'] = ti.wma(df['Close'], 20)
        df['DEMA_20'] = ti.dema(df['Close'], 20)
        df['TEMA_20'] = ti.tema(df['Close'], 20)
        
        # MACD
        macd_data = ti.macd(df['Close'])
        df['MACD'] = macd_data['MACD']
        df['MACD_Signal'] = macd_data['Signal']
        df['MACD_Histogram'] = macd_data['Histogram']
        
        # ADX
        adx_data = ti.adx(df['High'], df['Low'], df['Close'])
        df['ADX'] = adx_data['ADX']
        df['DI_Plus'] = adx_data['+DI']
        df['DI_Minus'] = adx_data['-DI']
        
        # 抛物线SAR
        df['SAR'] = ti.parabolic_sar(df['High'], df['Low'])
        
        # 动量指标
        df['RSI'] = ti.rsi(df['Close'])
        df['ROC'] = ti.roc(df['Close'])
        df['Momentum'] = ti.momentum(df['Close'])
        df['CCI'] = ti.cci(df['High'], df['Low'], df['Close'])
        df['Ultimate_Oscillator'] = ti.ultimate_oscillator(df['High'], df['Low'], df['Close'])
        
        # 随机指标
        stoch_data = ti.stochastic(df['High'], df['Low'], df['Close'])
        df['Stoch_K'] = stoch_data['%K']
        df['Stoch_D'] = stoch_data['%D']
        
        # Williams %R
        df['Williams_R'] = ti.williams_r(df['High'], df['Low'], df['Close'])
        
        # 波动率指标
        df['ATR'] = ti.atr(df['High'], df['Low'], df['Close'])
        df['Volatility'] = ti.volatility(df['Close'])
        
        # 布林带
        bb_data = ti.bollinger_bands(df['Close'])
        df['BB_Upper'] = bb_data['Upper']
        df['BB_Middle'] = bb_data['Middle']
        df['BB_Lower'] = bb_data['Lower']
        
        # 肯特纳通道
        kc_data = ti.keltner_channels(df['High'], df['Low'], df['Close'])
        df['KC_Upper'] = kc_data['Upper']
        df['KC_Middle'] = kc_data['Middle']
        df['KC_Lower'] = kc_data['Lower']
        
        # 唐奇安通道
        dc_data = ti.donchian_channels(df['High'], df['Low'])
        df['DC_Upper'] = dc_data['Upper']
        df['DC_Middle'] = dc_data['Middle']
        df['DC_Lower'] = dc_data['Lower']
        
        # 成交量指标
        df['OBV'] = ti.obv(df['Close'], df['Volume'])
        df['AD_Line'] = ti.ad_line(df['High'], df['Low'], df['Close'], df['Volume'])
        df['Chaikin_Oscillator'] = ti.chaikin_oscillator(df['High'], df['Low'], df['Close'], df['Volume'])
        df['Volume_SMA'] = ti.volume_sma(df['Volume'])
        df['VWAP'] = ti.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        
        # 市场强度指标
        df['MFI'] = ti.money_flow_index(df['High'], df['Low'], df['Close'], df['Volume'])
        df['EMV'] = ti.ease_of_movement(df['High'], df['Low'], df['Volume'])
        
        # 一目均衡表
        ichimoku_data = ti.ichimoku_cloud(df['High'], df['Low'], df['Close'])
        df['Tenkan_Sen'] = ichimoku_data['Tenkan_Sen']
        df['Kijun_Sen'] = ichimoku_data['Kijun_Sen']
        df['Senkou_Span_A'] = ichimoku_data['Senkou_Span_A']
        df['Senkou_Span_B'] = ichimoku_data['Senkou_Span_B']
        df['Chikou_Span'] = ichimoku_data['Chikou_Span']
        
        # 阿隆指标
        aroon_data = ti.aroon(df['High'], df['Low'])
        df['Aroon_Up'] = aroon_data['Aroon_Up']
        df['Aroon_Down'] = aroon_data['Aroon_Down']
        df['Aroon_Oscillator'] = aroon_data['Aroon_Oscillator']
        
        return df