"""
数据管理模块
负责股票数据的获取、存储和管理
"""

import pandas as pd
import yfinance as yf
from pathlib import Path
from typing import Optional, Dict, Any
import os

class DataManager:
    """股票数据管理器"""
    
    def __init__(self, data_dir: str = "data"):
        """初始化数据管理器
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.stocks_dir = self.data_dir / "stocks"
        self.stocks_dir.mkdir(exist_ok=True)
    
    def fetch_stock_data(self, symbol: str, start_date: str, end_date: str, 
                        save: bool = True) -> Optional[pd.DataFrame]:
        """从Yahoo Finance获取股票数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            save: 是否保存到本地
            
        Returns:
            股票数据DataFrame
        """
        try:
            # 获取数据
            stock = yf.Ticker(symbol)
            data = stock.history(start=start_date, end=end_date)
            
            if data.empty:
                print(f"未获取到股票 {symbol} 的数据")
                return None
            
            # 重置索引，将日期作为列
            data.reset_index(inplace=True)
            
            # 标准化列名
            data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
            data = data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            
            # 添加股票代码
            data['Symbol'] = symbol
            
            if save:
                # 保存到CSV文件
                file_path = self.stocks_dir / f"{symbol}.csv"
                data.to_csv(file_path, index=False)
                print(f"股票数据已保存到: {file_path}")
            
            return data
            
        except Exception as e:
            print(f"获取股票数据失败: {e}")
            return None
    
    def import_csv(self, file_path: str, symbol: str) -> bool:
        """导入CSV文件
        
        Args:
            file_path: CSV文件路径
            symbol: 股票代码
            
        Returns:
            是否导入成功
        """
        try:
            # 读取CSV文件
            data = pd.read_csv(file_path)
            
            # 验证必需的列
            required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                print(f"CSV文件缺少必需的列: {missing_columns}")
                return False
            
            # 添加股票代码
            data['Symbol'] = symbol
            
            # 保存到stocks目录
            output_path = self.stocks_dir / f"{symbol}.csv"
            data.to_csv(output_path, index=False)
            
            print(f"成功导入股票数据: {symbol}")
            return True
            
        except Exception as e:
            print(f"导入CSV文件失败: {e}")
            return False
    
    def get_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取本地股票数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            股票数据DataFrame
        """
        try:
            file_path = self.stocks_dir / f"{symbol}.csv"
            if not file_path.exists():
                print(f"股票数据文件不存在: {symbol}")
                return None
            
            data = pd.read_csv(file_path)
            data['Date'] = pd.to_datetime(data['Date'])
            return data
            
        except Exception as e:
            print(f"读取股票数据失败: {e}")
            return None
    
    def list_available_stocks(self) -> list:
        """列出所有可用的股票
        
        Returns:
            股票代码列表
        """
        try:
            csv_files = list(self.stocks_dir.glob("*.csv"))
            symbols = [f.stem for f in csv_files]
            return sorted(symbols)
        except Exception as e:
            print(f"列出股票失败: {e}")
            return []
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息
        
        Args:
            symbol: 股票代码
            
        Returns:
            股票信息字典
        """
        data = self.get_stock_data(symbol)
        if data is None:
            return {}
        
        info = {
            'symbol': symbol,
            'total_records': len(data),
            'date_range': (data['Date'].min(), data['Date'].max()),
            'price_range': (data['Close'].min(), data['Close'].max()),
            'avg_volume': data['Volume'].mean(),
            'latest_price': data['Close'].iloc[-1] if len(data) > 0 else 0
        }
        
        return info