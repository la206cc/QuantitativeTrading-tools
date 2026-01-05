"""
回测引擎模块
用于执行交易策略的历史回测
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from .strategy import BaseStrategy

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 10000, commission: float = 0.001):
        """初始化回测引擎
        
        Args:
            initial_capital: 初始资金
            commission: 手续费率
        """
        self.initial_capital = initial_capital
        self.commission = commission
    
    def run(self, data: pd.DataFrame, strategy: BaseStrategy) -> Dict[str, Any]:
        """运行回测
        
        Args:
            data: 股票数据
            strategy: 交易策略
            
        Returns:
            回测结果
        """
        # 生成交易信号
        signals_data = strategy.generate_signals(data)
        
        # 计算回测结果
        results = self._calculate_returns(signals_data)
        
        # 计算性能指标
        metrics = self._calculate_metrics(results)
        
        # 获取交易记录
        trades = self._get_trades(signals_data)
        
        return {
            'strategy_name': strategy.name,
            'strategy_params': strategy.get_parameters(),
            'data': results,
            'metrics': metrics,
            'trades': trades,
            'initial_capital': self.initial_capital,
            'final_capital': results['Portfolio_Value'].iloc[-1] if len(results) > 0 else self.initial_capital
        }
    
    def _calculate_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算收益"""
        df = data.copy()
        
        # 初始化
        df['Holdings'] = 0.0  # 持股数量
        df['Cash'] = float(self.initial_capital)  # 现金
        df['Portfolio_Value'] = float(self.initial_capital)  # 组合价值
        df['Returns'] = 0.0  # 收益率
        
        cash = self.initial_capital
        holdings = 0.0
        
        for i in range(len(df)):
            current_price = df['Close'].iloc[i]
            
            # 处理买入信号
            if df['Buy'].iloc[i] and cash > 0:
                # 计算可买入股数（考虑手续费）
                available_cash = cash * (1 - self.commission)
                shares_to_buy = int(available_cash / current_price)
                
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price * (1 + self.commission)
                    cash -= cost
                    holdings += shares_to_buy
            
            # 处理卖出信号
            elif df['Sell'].iloc[i] and holdings > 0:
                # 卖出所有持股
                proceeds = holdings * current_price * (1 - self.commission)
                cash += proceeds
                holdings = 0
            
            # 更新数据
            df.loc[df.index[i], 'Holdings'] = holdings
            df.loc[df.index[i], 'Cash'] = cash
            df.loc[df.index[i], 'Portfolio_Value'] = cash + holdings * current_price
            
            # 计算收益率
            if i > 0:
                prev_value = df['Portfolio_Value'].iloc[i-1]
                current_value = df['Portfolio_Value'].iloc[i]
                df.loc[df.index[i], 'Returns'] = (current_value - prev_value) / prev_value
        
        return df
    
    def _calculate_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """计算性能指标"""
        if len(data) == 0:
            return {}
        
        # 基本指标
        initial_value = self.initial_capital
        final_value = data['Portfolio_Value'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value
        
        # 收益率序列
        returns = data['Returns'].dropna()
        
        if len(returns) == 0:
            return {
                'total_return': total_return,
                'final_value': final_value
            }
        
        # 年化收益率（假设252个交易日）
        trading_days = len(data)
        years = trading_days / 252
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # 波动率
        volatility = returns.std() * np.sqrt(252)
        
        # 夏普比率（假设无风险利率为0）
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        portfolio_values = data['Portfolio_Value']
        peak = portfolio_values.expanding().max()
        drawdown = (portfolio_values - peak) / peak
        max_drawdown = drawdown.min()
        
        # 胜率
        positive_returns = returns[returns > 0]
        win_rate = len(positive_returns) / len(returns) if len(returns) > 0 else 0
        
        # 平均收益
        avg_return = returns.mean()
        avg_positive_return = positive_returns.mean() if len(positive_returns) > 0 else 0
        avg_negative_return = returns[returns < 0].mean() if len(returns[returns < 0]) > 0 else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'avg_return': avg_return,
            'avg_positive_return': avg_positive_return,
            'avg_negative_return': avg_negative_return,
            'final_value': final_value,
            'total_trades': len(self._get_trades(data))
        }
    
    def _get_trades(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """获取交易记录"""
        trades = []
        
        buy_signals = data[data['Buy'] == True]
        sell_signals = data[data['Sell'] == True]
        
        for _, buy_row in buy_signals.iterrows():
            trade = {
                'type': 'BUY',
                'date': buy_row['Date'],
                'price': buy_row['Close'],
                'signal': 'Buy Signal'
            }
            trades.append(trade)
        
        for _, sell_row in sell_signals.iterrows():
            trade = {
                'type': 'SELL',
                'date': sell_row['Date'],
                'price': sell_row['Close'],
                'signal': 'Sell Signal'
            }
            trades.append(trade)
        
        # 按日期排序
        trades.sort(key=lambda x: x['date'])
        
        return trades
    
    def compare_strategies(self, data: pd.DataFrame, strategies: List[BaseStrategy]) -> pd.DataFrame:
        """比较多个策略
        
        Args:
            data: 股票数据
            strategies: 策略列表
            
        Returns:
            策略比较结果DataFrame
        """
        results = []
        
        for strategy in strategies:
            result = self.run(data, strategy)
            metrics = result['metrics']
            
            strategy_result = {
                'Strategy': strategy.name,
                'Total Return': f"{metrics.get('total_return', 0):.2%}",
                'Annual Return': f"{metrics.get('annual_return', 0):.2%}",
                'Volatility': f"{metrics.get('volatility', 0):.2%}",
                'Sharpe Ratio': f"{metrics.get('sharpe_ratio', 0):.2f}",
                'Max Drawdown': f"{metrics.get('max_drawdown', 0):.2%}",
                'Win Rate': f"{metrics.get('win_rate', 0):.2%}",
                'Total Trades': metrics.get('total_trades', 0),
                'Final Value': f"${metrics.get('final_value', 0):,.2f}"
            }
            results.append(strategy_result)
        
        return pd.DataFrame(results)