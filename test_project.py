#!/usr/bin/env python3
"""
项目结构测试脚本
"""

import os
import sys
from pathlib import Path

def test_project_structure():
    """测试项目结构"""
    print("🔍 检查项目结构...")
    
    required_files = [
        'README.md',
        'requirements.txt',
        'main.py',
        'app.py',
        'start.py',
        'LICENSE',
        '.gitignore',
        'src/__init__.py',
        'src/data_manager.py',
        'src/indicators.py',
        'src/strategy.py',
        'src/backtest.py',
        'data/sample_data.csv',
        'tests/test_basic.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少文件: {missing_files}")
        return False
    else:
        print("✅ 所有必需文件都存在")
        return True

def test_imports():
    """测试模块导入"""
    print("🔍 检查模块导入...")
    
    try:
        sys.path.insert(0, '.')
        
        from src.data_manager import DataManager
        from src.indicators import TechnicalIndicators
        from src.strategy import StrategyFactory
        from src.backtest import BacktestEngine
        
        print("✅ 所有核心模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("🔍 测试基本功能...")
    
    try:
        # 测试数据管理器
        dm = DataManager()
        print("✅ DataManager 初始化成功")
        
        # 测试技术指标
        ti = TechnicalIndicators()
        import pandas as pd
        import numpy as np
        
        test_data = pd.Series([100, 102, 101, 103, 105])
        sma = ti.sma(test_data, 3)
        print("✅ 技术指标计算成功")
        
        # 测试策略工厂
        strategies = StrategyFactory.list_strategies()
        print(f"✅ 策略工厂工作正常，可用策略: {strategies}")
        
        # 测试回测引擎
        backtest = BacktestEngine()
        print("✅ 回测引擎初始化成功")
        
        return True
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

def main():
    """主函数"""
    print("="*50)
    print("📈 量化交易模拟工具 - 项目测试")
    print("="*50)
    
    tests = [
        test_project_structure,
        test_imports,
        test_basic_functionality
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("="*50)
    if passed == len(tests):
        print("🎉 所有测试通过！项目结构正确")
        print("🚀 可以开始使用量化交易模拟工具了")
        print("\n📚 使用方法:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 启动Web界面: streamlit run app.py")
        print("3. 或使用命令行: python main.py --help")
    else:
        print(f"❌ {len(tests) - passed} 个测试失败")
    print("="*50)

if __name__ == "__main__":
    main()