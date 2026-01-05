#!/usr/bin/env python3
"""
量化交易模拟工具 - Streamlit Web界面
QuantitativeTrading-tools Web Interface
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

from src.data_manager import DataManager
from src.strategy import StrategyFactory
from src.backtest import BacktestEngine
from src.indicators import TechnicalIndicators

# 页面配置
st.set_page_config(
    page_title="量化交易模拟工具",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data_manager():
    """加载数据管理器"""
    return DataManager()

@st.cache_data
def get_stock_data(symbol):
    """获取股票数据"""
    dm = load_data_manager()
    return dm.get_stock_data(symbol)

def create_candlestick_chart(data, indicators=None):
    """创建K线图"""
    if data is None or len(data) == 0:
        return None
    
    # 创建子图
    rows = 3 if indicators else 2
    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=('K线图', '成交量', '技术指标') if indicators else ('K线图', '成交量'),
        row_heights=[0.6, 0.2, 0.2] if indicators else [0.7, 0.3]
    )
    
    # K线图
    fig.add_trace(
        go.Candlestick(
            x=data['Date'],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='K线',
            increasing_line_color='red',
            decreasing_line_color='green'
        ),
        row=1, col=1
    )
    
    # 添加技术指标到K线图
    if indicators:
        for indicator, params in indicators.items():
            if indicator in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data['Date'], 
                        y=data[indicator], 
                        name=indicator,
                        line=dict(color=params.get('color', 'blue'), width=1)
                    ),
                    row=1, col=1
                )
    
    # 成交量
    colors = ['red' if close >= open else 'green' 
              for close, open in zip(data['Close'], data['Open'])]
    fig.add_trace(
        go.Bar(x=data['Date'], y=data['Volume'], name='成交量', marker_color=colors),
        row=2, col=1
    )
    
    # 技术指标子图
    if indicators and rows == 3:
        # 这里可以添加RSI、MACD等指标
        if 'RSI' in data.columns:
            fig.add_trace(
                go.Scatter(x=data['Date'], y=data['RSI'], name='RSI', line=dict(color='purple')),
                row=3, col=1
            )
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # 更新布局
    fig.update_layout(
        title='股票技术分析图表',
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
        template='plotly_white'
    )
    
    return fig

def create_backtest_chart(result_data):
    """创建回测结果图表"""
    if result_data is None or len(result_data) == 0:
        return None
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('组合价值', '持仓情况'),
        row_heights=[0.7, 0.3]
    )
    
    # 组合价值曲线
    fig.add_trace(
        go.Scatter(
            x=result_data['Date'],
            y=result_data['Portfolio_Value'],
            name='组合价值',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )
    
    # 买卖点标记
    buy_points = result_data[result_data['Buy'] == True]
    sell_points = result_data[result_data['Sell'] == True]
    
    if len(buy_points) > 0:
        fig.add_trace(
            go.Scatter(
                x=buy_points['Date'],
                y=buy_points['Portfolio_Value'],
                mode='markers',
                name='买入',
                marker=dict(color='red', size=10, symbol='triangle-up')
            ),
            row=1, col=1
        )
    
    if len(sell_points) > 0:
        fig.add_trace(
            go.Scatter(
                x=sell_points['Date'],
                y=sell_points['Portfolio_Value'],
                mode='markers',
                name='卖出',
                marker=dict(color='green', size=10, symbol='triangle-down')
            ),
            row=1, col=1
        )
    
    # 持仓情况
    fig.add_trace(
        go.Scatter(
            x=result_data['Date'],
            y=result_data['Holdings'],
            name='持股数量',
            fill='tonexty',
            line=dict(color='orange')
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title='回测结果分析',
        height=600,
        showlegend=True,
        template='plotly_white'
    )
    
    return fig

def main():
    """主界面"""
    # 标题
    st.markdown('<h1 class="main-header">📈 量化交易模拟工具</h1>', unsafe_allow_html=True)
    
    # 初始化数据管理器
    dm = load_data_manager()
    
    # 侧边栏
    with st.sidebar:
        st.markdown("### 🔧 控制面板")
        
        # 获取可用股票
        available_stocks = dm.list_available_stocks()
        
        if not available_stocks:
            st.warning("没有可用的股票数据")
            st.info("请先添加股票数据")
        else:
            selected_stock = st.selectbox("选择股票", available_stocks)
        
        st.markdown("---")
        
        # 数据获取
        st.markdown("### 📊 数据获取")
        
        # Yahoo Finance数据获取
        with st.expander("从Yahoo Finance获取"):
            symbol = st.text_input("股票代码", value="AAPL")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("开始日期", value=datetime.now() - timedelta(days=365))
            with col2:
                end_date = st.date_input("结束日期", value=datetime.now())
            
            if st.button("获取数据"):
                with st.spinner("正在获取数据..."):
                    data = dm.fetch_stock_data(symbol, start_date.strftime('%Y-%m-%d'), 
                                             end_date.strftime('%Y-%m-%d'))
                    if data is not None:
                        st.success(f"成功获取 {len(data)} 条记录")
                        st.rerun()
                    else:
                        st.error("获取数据失败")
        
        # CSV文件上传
        with st.expander("上传CSV文件"):
            uploaded_file = st.file_uploader("选择CSV文件", type=['csv'])
            if uploaded_file is not None:
                symbol_name = st.text_input("股票代码", value="STOCK")
                if st.button("导入数据"):
                    try:
                        # 保存临时文件
                        temp_path = f"temp_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # 导入数据
                        success = dm.import_csv(temp_path, symbol_name)
                        os.remove(temp_path)  # 清理临时文件
                        
                        if success:
                            st.success(f"成功导入: {symbol_name}")
                            st.rerun()
                        else:
                            st.error("导入失败")
                    except Exception as e:
                        st.error(f"导入失败: {e}")
    
    # 主内容区域
    if available_stocks and 'selected_stock' in locals():
        # 创建标签页
        tab1, tab2, tab3 = st.tabs(["📈 数据分析", "🎯 策略回测", "📊 策略比较"])
        
        with tab1:
            st.subheader(f"📊 {selected_stock} 数据分析")
            
            # 获取股票数据
            stock_data = get_stock_data(selected_stock)
            
            if stock_data is not None:
                # 添加技术指标
                ti = TechnicalIndicators()
                stock_data_with_indicators = ti.add_all_indicators(stock_data)
                
                # 显示基本信息
                col1, col2, col3, col4 = st.columns(4)
                
                latest = stock_data.iloc[-1]
                prev = stock_data.iloc[-2] if len(stock_data) > 1 else latest
                
                price_change = latest['Close'] - prev['Close']
                price_change_pct = (price_change / prev['Close']) * 100
                
                with col1:
                    st.metric("当前价格", f"${latest['Close']:.2f}", 
                             f"{price_change:+.2f} ({price_change_pct:+.2f}%)")
                
                with col2:
                    st.metric("成交量", f"{latest['Volume']:,}")
                
                with col3:
                    st.metric("最高价", f"${stock_data['High'].max():.2f}")
                
                with col4:
                    st.metric("最低价", f"${stock_data['Low'].min():.2f}")
                
                # 技术指标选择
                st.subheader("技术指标")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    show_ma = st.checkbox("移动平均线", value=True)
                with col2:
                    show_bb = st.checkbox("布林带", value=False)
                with col3:
                    show_rsi = st.checkbox("RSI", value=True)
                
                # 创建图表
                indicators = {}
                if show_ma:
                    indicators.update({
                        'SMA_5': {'color': 'orange'},
                        'SMA_20': {'color': 'blue'}
                    })
                if show_bb:
                    indicators.update({
                        'BB_Upper': {'color': 'gray'},
                        'BB_Lower': {'color': 'gray'}
                    })
                
                fig = create_candlestick_chart(stock_data_with_indicators, indicators)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                # 数据表格
                with st.expander("📋 详细数据"):
                    st.dataframe(stock_data.tail(20), use_container_width=True)
            
            else:
                st.error(f"无法加载股票 {selected_stock} 的数据")
        
        with tab2:
            st.subheader("🎯 策略回测")
            
            # 策略选择
            col1, col2 = st.columns([1, 2])
            
            with col1:
                strategy_info = StrategyFactory.get_strategy_info()
                strategy_names = list(strategy_info.keys())
                strategy_display_names = [strategy_info[name]['name'] for name in strategy_names]
                
                selected_strategy_idx = st.selectbox(
                    "选择策略",
                    range(len(strategy_names)),
                    format_func=lambda x: strategy_display_names[x]
                )
                
                selected_strategy_key = strategy_names[selected_strategy_idx]
                selected_strategy_info = strategy_info[selected_strategy_key]
                
                st.write(f"**描述**: {selected_strategy_info['description']}")
            
            with col2:
                st.write("**策略参数**")
                strategy_params = {}
                
                for param_name, param_info in selected_strategy_info['parameters'].items():
                    if param_info['type'] == 'int':
                        strategy_params[param_name] = st.number_input(
                            param_info['description'],
                            value=param_info['default'],
                            min_value=1,
                            key=f"{selected_strategy_key}_{param_name}"
                        )
                    elif param_info['type'] == 'float':
                        strategy_params[param_name] = st.number_input(
                            param_info['description'],
                            value=float(param_info['default']),
                            min_value=0.0,
                            key=f"{selected_strategy_key}_{param_name}"
                        )
            
            # 回测参数
            col1, col2 = st.columns(2)
            with col1:
                initial_capital = st.number_input("初始资金", value=10000, min_value=1000)
            with col2:
                commission = st.number_input("手续费率", value=0.001, min_value=0.0, max_value=0.1, format="%.4f")
            
            # 运行回测
            if st.button("🚀 运行回测", type="primary"):
                stock_data = get_stock_data(selected_stock)
                
                if stock_data is not None:
                    with st.spinner("正在运行回测..."):
                        # 创建策略
                        strategy = StrategyFactory.get_strategy(selected_strategy_key, **strategy_params)
                        
                        # 运行回测
                        backtest = BacktestEngine(initial_capital, commission)
                        result = backtest.run(stock_data, strategy)
                        
                        # 显示结果
                        st.success("回测完成!")
                        
                        # 性能指标
                        metrics = result['metrics']
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("总收益率", f"{metrics.get('total_return', 0):.2%}")
                        with col2:
                            st.metric("年化收益率", f"{metrics.get('annual_return', 0):.2%}")
                        with col3:
                            st.metric("夏普比率", f"{metrics.get('sharpe_ratio', 0):.2f}")
                        with col4:
                            st.metric("最大回撤", f"{metrics.get('max_drawdown', 0):.2%}")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("胜率", f"{metrics.get('win_rate', 0):.2%}")
                        with col2:
                            st.metric("交易次数", f"{metrics.get('total_trades', 0)}")
                        with col3:
                            st.metric("最终资金", f"${result['final_capital']:,.2f}")
                        with col4:
                            profit = result['final_capital'] - initial_capital
                            st.metric("净利润", f"${profit:,.2f}")
                        
                        # 回测图表
                        fig = create_backtest_chart(result['data'])
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # 交易记录
                        if result['trades']:
                            st.subheader("📋 交易记录")
                            trades_df = pd.DataFrame(result['trades'])
                            st.dataframe(trades_df, use_container_width=True)
                
                else:
                    st.error("无法加载股票数据")
        
        with tab3:
            st.subheader("📊 策略比较")
            st.info("选择多个策略进行性能比较")
            
            # 多策略选择
            strategy_info = StrategyFactory.get_strategy_info()
            selected_strategies = st.multiselect(
                "选择要比较的策略",
                list(strategy_info.keys()),
                format_func=lambda x: strategy_info[x]['name']
            )
            
            if len(selected_strategies) >= 2:
                if st.button("🔄 开始比较"):
                    stock_data = get_stock_data(selected_stock)
                    
                    if stock_data is not None:
                        with st.spinner("正在比较策略..."):
                            strategies = []
                            for strategy_key in selected_strategies:
                                strategy = StrategyFactory.get_strategy(strategy_key)
                                strategies.append(strategy)
                            
                            backtest = BacktestEngine(10000, 0.001)
                            comparison_df = backtest.compare_strategies(stock_data, strategies)
                            
                            st.subheader("策略比较结果")
                            st.dataframe(comparison_df, use_container_width=True)
            else:
                st.info("请至少选择2个策略进行比较")
    
    else:
        # 欢迎页面
        st.markdown("""
        ## 🎉 欢迎使用量化交易模拟工具！
        
        ### 🚀 快速开始
        1. **获取数据**: 从Yahoo Finance获取股票数据或上传CSV文件
        2. **分析数据**: 查看K线图和技术指标
        3. **策略回测**: 选择策略并运行历史回测
        4. **比较策略**: 对比不同策略的表现
        
        ### 📊 支持的功能
        - 📈 实时股票数据获取
        - 🔍 技术指标分析 (SMA, EMA, RSI, MACD, 布林带等)
        - 🎯 多种交易策略 (移动平均交叉, RSI, MACD, 布林带)
        - 📊 详细的回测分析
        - 📋 完整的交易记录
        
        ### 💡 使用提示
        - 首次使用请先在左侧面板获取或导入股票数据
        - 建议使用至少1年的历史数据进行回测
        - 可以调整策略参数来优化表现
        """)

if __name__ == "__main__":
    main()