# 📈 量化交易模拟工具 (QuantitativeTrading-tools)

一个简单易用的量化交易策略回测和模拟工具，适合初学者学习量化交易概念。

## ✨ 功能特性

- 📊 **股票数据管理** - 支持CSV导入和Yahoo Finance API获取
- 📈 **技术指标计算** - SMA, EMA, RSI, MACD, 布林带等
- 🎯 **交易策略** - 移动平均交叉、RSI超买超卖等经典策略
- 🔄 **回测系统** - 简单直观的策略回测功能
- 🌐 **Web界面** - 基于Streamlit的现代化界面
- 📱 **响应式设计** - 支持桌面和移动端访问

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动Web界面
```bash
streamlit run app.py
```

### 命令行使用
```bash
python main.py --help
```

## 📊 支持的技术指标

- **SMA** - 简单移动平均线
- **EMA** - 指数移动平均线  
- **RSI** - 相对强弱指数
- **MACD** - 移动平均收敛发散
- **布林带** - 布林格带状指标
- **成交量** - 成交量分析

## 🎯 内置交易策略

1. **移动平均交叉策略** - 基于短期和长期均线交叉
2. **RSI超买超卖策略** - 基于RSI指标的反转策略
3. **MACD金叉死叉策略** - 基于MACD信号线交叉
4. **布林带突破策略** - 基于布林带上下轨突破

## 📁 项目结构

```
QuantitativeTrading-tools/
├── README.md              # 项目说明
├── requirements.txt       # 依赖包
├── main.py               # 命令行入口
├── app.py                # Web界面
├── data/                 # 数据目录
├── src/                  # 源代码
└── tests/                # 测试文件
```

## 🔧 使用示例

### 1. 导入股票数据
```python
from src.data_manager import DataManager

dm = DataManager()
# 从Yahoo Finance获取数据
dm.fetch_stock_data('AAPL', '2023-01-01', '2024-01-01')
# 或导入CSV文件
dm.import_csv('data/sample_data.csv', 'AAPL')
```

### 2. 计算技术指标
```python
from src.indicators import TechnicalIndicators

ti = TechnicalIndicators()
data = dm.get_stock_data('AAPL')
data['SMA_20'] = ti.sma(data['close'], 20)
data['RSI'] = ti.rsi(data['close'], 14)
```

### 3. 运行回测
```python
from src.strategy import MovingAverageCrossStrategy
from src.backtest import BacktestEngine

strategy = MovingAverageCrossStrategy(short_window=5, long_window=20)
backtest = BacktestEngine(initial_capital=10000)
result = backtest.run(data, strategy)
```

## 📈 Web界面功能

- 📊 实时股票数据展示
- 📈 交互式K线图和技术指标图表
- ⚙️ 策略参数配置
- 📋 回测结果分析
- 📁 数据导入导出

## 🛠️ 技术栈

- **Python 3.8+** - 核心开发语言
- **Streamlit** - Web界面框架
- **Pandas** - 数据处理
- **NumPy** - 数值计算
- **Plotly** - 交互式图表
- **yfinance** - 股票数据获取

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

## ⚠️ 免责声明

本工具仅用于教育和研究目的，不构成投资建议。实际投资请谨慎决策。

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**