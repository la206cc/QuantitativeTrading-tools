# 🚀 快速启动指南

## 📋 系统要求

- Python 3.8 或更高版本
- pip 包管理器
- 网络连接（用于获取股票数据）

## ⚡ 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/la206cc/QuantitativeTrading-tools.git
cd QuantitativeTrading-tools
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 启动应用

#### 方式一：Web界面（推荐）
```bash
streamlit run app.py
```
然后在浏览器中访问 `http://localhost:8501`

#### 方式二：命令行工具
```bash
# 查看帮助
python main.py --help

# 获取股票数据
python main.py fetch --symbol AAPL --start 2023-01-01 --end 2024-01-01

# 运行回测
python main.py backtest --symbol AAPL --strategy ma_cross

# 列出可用股票
python main.py list
```

#### 方式三：交互式启动器
```bash
python start.py
```

## 🎯 主要功能

### 📊 数据管理
- **Yahoo Finance API**: 自动获取实时股票数据
- **CSV导入**: 支持自定义数据格式
- **数据验证**: 自动检查数据完整性

### 📈 技术指标
- **趋势指标**: SMA, EMA, WMA, DEMA, TEMA, KAMA, MACD, ADX, 抛物线SAR
- **动量指标**: RSI, 随机指标, Williams %R, ROC, Momentum, CCI, Ultimate Oscillator
- **波动率指标**: 布林带, 肯特纳通道, 唐奇安通道, ATR, 历史波动率
- **成交量指标**: OBV, A/D Line, 蔡金振荡器, VWAP, MFI, EMV
- **综合指标**: 一目均衡表, 阿隆指标

### 🎯 交易策略
- **移动平均交叉**: 经典的趋势跟踪策略
- **RSI超买超卖**: 基于相对强弱指数的反转策略
- **MACD金叉死叉**: 基于MACD指标的信号策略
- **布林带突破**: 基于布林带的突破策略

### 🔄 回测系统
- **历史回测**: 完整的策略历史表现分析
- **性能指标**: 收益率、夏普比率、最大回撤等
- **交易记录**: 详细的买卖信号记录
- **策略比较**: 多策略性能对比

## 📱 Web界面功能

### 数据分析页面
- 📊 实时股票数据展示
- 📈 交互式K线图
- 📋 技术指标图表
- 📁 数据导入导出

### 策略回测页面
- ⚙️ 策略参数配置
- 🚀 一键回测执行
- 📊 详细性能分析
- 📋 交易记录查看

### 策略比较页面
- 🔄 多策略对比
- 📊 性能指标比较
- 📈 收益曲线对比

## 💡 使用示例

### 示例1：获取苹果公司股票数据
```python
from src.data_manager import DataManager

dm = DataManager()
data = dm.fetch_stock_data('AAPL', '2023-01-01', '2024-01-01')
print(f"获取到 {len(data)} 条记录")
```

### 示例2：计算技术指标
```python
from src.indicators import TechnicalIndicators

ti = TechnicalIndicators()
data['SMA_20'] = ti.sma(data['Close'], 20)
data['RSI'] = ti.rsi(data['Close'], 14)
```

### 示例3：运行策略回测
```python
from src.strategy import StrategyFactory
from src.backtest import BacktestEngine

# 创建移动平均交叉策略
strategy = StrategyFactory.get_strategy('ma_cross', short_window=5, long_window=20)

# 运行回测
backtest = BacktestEngine(initial_capital=10000)
result = backtest.run(data, strategy)

print(f"总收益率: {result['metrics']['total_return']:.2%}")
```

## 🛠️ 自定义策略

你可以轻松创建自己的交易策略：

```python
from src.strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def __init__(self, param1=10, param2=0.5):
        super().__init__("我的自定义策略")
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, data):
        # 实现你的策略逻辑
        df = data.copy()
        # ... 策略代码 ...
        return df
```

## 🔧 配置选项

### 回测参数
- `initial_capital`: 初始资金（默认: 10000）
- `commission`: 手续费率（默认: 0.001）

### 策略参数
每个策略都有可配置的参数，可以通过Web界面或代码进行调整。

## 📚 更多资源

- 📖 [完整文档](README.md)
- 🧪 [测试指南](tests/)
- 🐛 [问题反馈](https://github.com/la206cc/QuantitativeTrading-tools/issues)
- 💡 [功能建议](https://github.com/la206cc/QuantitativeTrading-tools/discussions)

## ⚠️ 免责声明

本工具仅用于教育和研究目的，不构成投资建议。实际投资请谨慎决策，风险自负。

---

**🌟 如果这个项目对你有帮助，请给个Star支持一下！**