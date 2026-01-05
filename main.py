#!/usr/bin/env python3
"""
量化交易模拟工具 - 命令行入口
QuantitativeTrading-tools CLI
"""

import argparse
import sys
from pathlib import Path
from src.data_manager import DataManager
from src.strategy import StrategyFactory
from src.backtest import BacktestEngine
from src.indicators import TechnicalIndicators

def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description='量化交易模拟工具 - 简单易用的策略回测平台',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 获取股票数据
  python main.py fetch --symbol AAPL --start 2023-01-01 --end 2024-01-01
  
  # 导入CSV数据
  python main.py import --file data.csv --symbol STOCK
  
  # 运行回测
  python main.py backtest --symbol AAPL --strategy ma_cross
  
  # 列出可用股票
  python main.py list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 获取数据命令
    fetch_parser = subparsers.add_parser('fetch', help='从Yahoo Finance获取股票数据')
    fetch_parser.add_argument('--symbol', '-s', required=True, help='股票代码')
    fetch_parser.add_argument('--start', required=True, help='开始日期 (YYYY-MM-DD)')
    fetch_parser.add_argument('--end', required=True, help='结束日期 (YYYY-MM-DD)')
    
    # 导入数据命令
    import_parser = subparsers.add_parser('import', help='导入CSV数据')
    import_parser.add_argument('--file', '-f', required=True, help='CSV文件路径')
    import_parser.add_argument('--symbol', '-s', required=True, help='股票代码')
    
    # 回测命令
    backtest_parser = subparsers.add_parser('backtest', help='运行策略回测')
    backtest_parser.add_argument('--symbol', '-s', required=True, help='股票代码')
    backtest_parser.add_argument('--strategy', required=True, 
                               choices=StrategyFactory.list_strategies(),
                               help='策略名称')
    backtest_parser.add_argument('--capital', type=float, default=10000, help='初始资金')
    backtest_parser.add_argument('--commission', type=float, default=0.001, help='手续费率')
    
    # 列表命令
    list_parser = subparsers.add_parser('list', help='列出可用股票')
    
    # 策略信息命令
    strategies_parser = subparsers.add_parser('strategies', help='列出可用策略')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        dm = DataManager()
        
        if args.command == 'fetch':
            print(f"正在获取 {args.symbol} 的数据...")
            data = dm.fetch_stock_data(args.symbol, args.start, args.end)
            if data is not None:
                print(f"成功获取 {len(data)} 条记录")
            else:
                print("获取数据失败")
        
        elif args.command == 'import':
            print(f"正在导入 {args.file}...")
            success = dm.import_csv(args.file, args.symbol)
            if success:
                print("导入成功")
            else:
                print("导入失败")
        
        elif args.command == 'backtest':
            print(f"正在运行 {args.symbol} 的 {args.strategy} 策略回测...")
            
            # 获取数据
            data = dm.get_stock_data(args.symbol)
            if data is None:
                print(f"未找到股票 {args.symbol} 的数据")
                return
            
            # 创建策略
            strategy = StrategyFactory.get_strategy(args.strategy)
            
            # 运行回测
            backtest = BacktestEngine(args.capital, args.commission)
            result = backtest.run(data, strategy)
            
            # 显示结果
            print_backtest_results(result)
        
        elif args.command == 'list':
            stocks = dm.list_available_stocks()
            if stocks:
                print("可用股票:")
                for stock in stocks:
                    info = dm.get_stock_info(stock)
                    print(f"  {stock}: {info.get('total_records', 0)} 条记录")
            else:
                print("没有可用的股票数据")
        
        elif args.command == 'strategies':
            strategies = StrategyFactory.get_strategy_info()
            print("可用策略:")
            for key, info in strategies.items():
                print(f"  {key}: {info['name']}")
                print(f"    描述: {info['description']}")
                print(f"    参数: {list(info['parameters'].keys())}")
                print()
    
    except Exception as e:
        print(f"执行失败: {e}")
        sys.exit(1)

def print_backtest_results(result):
    """打印回测结果"""
    print("\n" + "="*50)
    print(f"策略: {result['strategy_name']}")
    print(f"参数: {result['strategy_params']}")
    print("="*50)
    
    metrics = result['metrics']
    print(f"初始资金: ${result['initial_capital']:,.2f}")
    print(f"最终资金: ${result['final_capital']:,.2f}")
    print(f"总收益率: {metrics.get('total_return', 0):.2%}")
    print(f"年化收益率: {metrics.get('annual_return', 0):.2%}")
    print(f"波动率: {metrics.get('volatility', 0):.2%}")
    print(f"夏普比率: {metrics.get('sharpe_ratio', 0):.2f}")
    print(f"最大回撤: {metrics.get('max_drawdown', 0):.2%}")
    print(f"胜率: {metrics.get('win_rate', 0):.2%}")
    print(f"交易次数: {metrics.get('total_trades', 0)}")
    
    # 显示交易记录
    trades = result['trades']
    if trades:
        print(f"\n交易记录 (前10条):")
        for i, trade in enumerate(trades[:10]):
            print(f"  {trade['date'].strftime('%Y-%m-%d')}: {trade['type']} @ ${trade['price']:.2f}")
        if len(trades) > 10:
            print(f"  ... 还有 {len(trades) - 10} 条交易记录")

if __name__ == '__main__':
    main()