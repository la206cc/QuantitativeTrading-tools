#!/usr/bin/env python3
"""
量化交易模拟工具启动脚本
QuantitativeTrading-tools Launcher
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def install_dependencies():
    """安装依赖包"""
    print("📦 正在检查依赖包...")
    
    try:
        # 检查关键依赖
        import streamlit
        import pandas
        import plotly
        import yfinance
        print("✅ 所有依赖包已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("📦 正在安装依赖包...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ])
            print("✅ 依赖包安装完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ 依赖包安装失败")
            print("请手动运行: pip install -r requirements.txt")
            return False

def create_sample_data():
    """创建示例数据"""
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir()
    
    sample_file = data_dir / "sample_data.csv"
    if not sample_file.exists():
        print("📊 创建示例数据...")
        # 示例数据已经在项目创建时生成

def show_menu():
    """显示菜单"""
    print("\n" + "="*50)
    print("📈 量化交易模拟工具 (QuantitativeTrading-tools)")
    print("="*50)
    print("1. 🌐 启动Web界面 (推荐)")
    print("2. 💻 命令行模式")
    print("3. 🧪 运行测试")
    print("4. 📚 查看帮助")
    print("5. 🚪 退出")
    print("="*50)

def start_web_interface():
    """启动Web界面"""
    print("🚀 正在启动Web界面...")
    print("🌐 访问地址: http://localhost:8501")
    print("⏹️  按 Ctrl+C 停止服务")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', '8501',
            '--server.address', 'localhost',
            '--browser.gatherUsageStats', 'false'
        ])
    except KeyboardInterrupt:
        print("\n👋 Web界面已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def start_cli_mode():
    """启动命令行模式"""
    print("💻 命令行模式")
    print("使用 'python main.py --help' 查看可用命令")
    print("\n示例命令:")
    print("  python main.py fetch --symbol AAPL --start 2023-01-01 --end 2024-01-01")
    print("  python main.py list")
    print("  python main.py strategies")

def run_tests():
    """运行测试"""
    print("🧪 正在运行测试...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'])
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")

def show_help():
    """显示帮助信息"""
    print("""
📚 量化交易模拟工具使用指南

🎯 主要功能:
  • 股票数据获取和管理
  • 技术指标计算 (SMA, EMA, RSI, MACD, 布林带等)
  • 交易策略回测 (移动平均交叉, RSI, MACD, 布林带)
  • 策略性能分析和比较
  • 直观的Web界面展示

🚀 快速开始:
  1. 选择 "启动Web界面" 获得最佳体验
  2. 在左侧面板获取或导入股票数据
  3. 在 "数据分析" 标签查看技术图表
  4. 在 "策略回测" 标签测试交易策略
  5. 在 "策略比较" 标签对比不同策略

💡 使用提示:
  • 建议使用至少1年的历史数据进行回测
  • 可以调整策略参数来优化表现
  • 回测结果仅供参考，不构成投资建议

📁 项目结构:
  • src/: 核心源代码
  • data/: 数据存储目录
  • tests/: 测试文件
  • app.py: Web界面
  • main.py: 命令行入口

🔗 更多信息请查看 README.md
    """)

def main():
    """主函数"""
    print("🔍 正在初始化...")
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 安装依赖
    if not install_dependencies():
        return
    
    # 创建示例数据
    create_sample_data()
    
    # 主循环
    while True:
        show_menu()
        
        try:
            choice = input("\n请选择操作 (1-5): ").strip()
            
            if choice == '1':
                start_web_interface()
            elif choice == '2':
                start_cli_mode()
                break
            elif choice == '3':
                run_tests()
            elif choice == '4':
                show_help()
            elif choice == '5':
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请输入 1-5")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main()