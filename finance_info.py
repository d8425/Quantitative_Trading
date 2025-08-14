import talib as ta
from utils import trade_info
from datetime import date, timedelta
import pandas as pd
import numpy as np
import utils.llm_quantization as llm_q


def fin_ind(trade_df, period=15):
    """
    计算多种技术指标

    参数:
    trade_df (pd.DataFrame): 交易数据，应包含['open', 'high', 'low', 'close', 'volume']列
    period (int): 计算指标的周期，默认为15日

    返回:
    pd.DataFrame: 包含原始数据和计算出的技术指标的DataFrame
    """
    # 确保数据包含所需的列
    required_columns = ['开盘', '最高', '最低', '收盘', '成交量']
    if not all(col in trade_df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in trade_df.columns]
        raise ValueError(f"输入数据缺少必要的列: {', '.join(missing)}")

    # 复制原始数据，避免修改原数据
    df = trade_df.copy()
    # fin_ind_data = pd.DataFrame()
    # 1. 计算RSI (相对强弱指数)
    df['RSI'] = ta.RSI(df['收盘'], timeperiod=period).iloc[-1]  # 只取最新值

    # 2. 计算移动平均线 (MA) - 计算收盘价与MA的比值
    ma = ta.MA(df['收盘'], timeperiod=period, matype=0).iloc[-1]
    df['MA_ratio'] = df['收盘'].iloc[-1] / ma if ma != 0 else np.nan

    # 3. 计算MACD (指数平滑异同平均线)
    macd, macd_signal, macd_hist = ta.MACD(df['收盘'],
                                           fastperiod=12,
                                           slowperiod=26,
                                           signalperiod=9)
    df['MACD'] = macd.iloc[-1]
    df['MACD_signal'] = macd_signal.iloc[-1]
    df['MACD_hist'] = macd_hist.iloc[-1]

    # 获取当前和前一个MACD柱状图归一化值
    current_hist = np.clip((macd.iloc[-1] - macd_signal.iloc[-1]) * 5 + 50, 0, 100)
    prev_hist = np.clip((macd.iloc[-2] - macd_signal.iloc[-2]) * 5 + 50, 0, 100)
    # 计算归一化后的柱状图变化
    df['MACD_hist_diff'] = current_hist - prev_hist

    # 4. 计算动量指标 (Momentum)
    df['MOM'] = ta.MOM(df['收盘'], timeperiod=period).iloc[-1]

    # 5. 计算ADX (平均方向指数)
    df['ADX'] = ta.ADX(df['最高'], df['最低'], df['收盘'], timeperiod=period).iloc[-1]

    # 6. 计算布林带 (Bollinger Bands) - 计算收盘价在布林带中的位置
    upper, middle, lower = ta.BBANDS(df['收盘'],
                                     timeperiod=period + 6,
                                     nbdevup=2,
                                     nbdevdn=2,
                                     matype=0)
    df['BB_upper'] = upper.iloc[-1]
    df['BB_middle'] = middle.iloc[-1]
    df['BB_lower'] = lower.iloc[-1]
    df['BB_position'] = (df['收盘'].iloc[-1] - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1]) if (upper.iloc[-1] - lower.iloc[-1]) != 0 else np.nan

    # 7. 计算威廉指标 (Williams %R)
    df['WR'] = ta.WILLR(df['最高'], df['最低'], df['收盘'], timeperiod=period).iloc[-1]

    # 8. 计算顺势指标 (CCI)
    df['CCI'] = ta.CCI(df['最高'], df['最低'], df['收盘'], timeperiod=period).iloc[-1]

    # 9. OBV (能量潮) - 计算OBV的变化率
    obv = ta.OBV(df['收盘'], df['成交量'])
    df['OBV'] = obv.iloc[-1]
    df['OBV_change'] = (obv.iloc[-1] - obv.iloc[-5]) / obv.iloc[-5] if obv.iloc[-5] != 0 else np.nan

    # 计算20日简单移动平均线
    df['MA_20'] = ta.MA(df['收盘'], timeperiod=20, matype=0).iloc[-1]

    # 处理缺失值
    df = df.dropna()

    # 取最后一列
    latest_data = df.iloc[-1].copy()

    return df, latest_data


def bank_cal(symbol, period, days_ago):
    # today
    time = date.today()
    time_s = time.strftime("%Y%m%d")
    time_ago = time-timedelta(days=days_ago)
    time_ago_s = time_ago.strftime("%Y%m%d")
    fin_info = trade_info.get_trade_info(symbol,time_ago_s,time_s)

    # finance calculate
    df, fin_index = fin_ind(fin_info, period=period)

    return df, fin_index


def quantization(symbol, period, days_ago, weights=None):
    df, banking_ind = bank_cal(symbol,period,days_ago)

    # quantization standard
    # 默认权重 - 根据技术分析理论分配权重
    if weights is None:
        weights = {
            'RSI': 15,  # 趋势强度和超买超卖
            'MA_ratio': 10,  # 价格与均线关系
            'MACD': 15,  # 趋势方向和动量
            'ADX': 10,  # 趋势强度
            'BB_position': 10,  # 布林带位置
            'WR': 10,  # 超买超卖
            'CCI': 10,  # 趋势转折点
            'OBV_change': 20  # 成交量与价格关系
        }

    # 标准化各指标并计算得分
    scores = {}

    # RSI评分 (0-100) - 50为中性，接近30为超卖，接近70为超买
    scores['RSI'] = 100 - np.clip(abs(banking_ind['RSI'] - 50) * 2, 0, 100)

    # MA评分 - 价格高于MA得高分
    scores['MA_ratio'] = np.clip(banking_ind['MA_ratio'] * 100, 0, 100) if not np.isnan(
        banking_ind['MA_ratio']) else 50

    # MACD评分 - MACD线高于信号线得高分
    scores['MACD'] = np.clip((banking_ind['MACD'] - banking_ind['MACD_signal']) * 5 + 50, 0, 100)

    # ADX评分 - ADX高于25表示强趋势
    scores['ADX'] = np.clip(banking_ind['ADX'] * 2, 0, 100)

    # 布林带评分 - 价格接近下轨得高分(看涨)，接近上轨得低分(看跌)
    scores['BB_position'] = np.clip((1 - banking_ind['BB_position']) * 100, 0, 100) if not np.isnan(
        banking_ind['BB_position']) else 50

    # 威廉指标评分 - 接近-100为超卖，接近0为超买
    scores['WR'] = np.clip(banking_ind['WR'] * -1, 0, 100)

    # CCI评分 - CCI低于-100为超卖，高于100为超买
    scores['CCI'] = np.clip(50 - banking_ind['CCI'] / 4, 0, 100)

    # OBV评分 - OBV上升得高分
    scores['OBV_change'] = np.clip(banking_ind['OBV_change'] * 500 + 50, 0, 100) if not np.isnan(
        banking_ind['OBV_change']) else 50

    # 计算加权总分
    total_score = sum(scores[indicator] * weight for indicator, weight in weights.items()) / sum(weights.values())


    ##  趋势过滤 (修正)--------------------------------------------------------------------------------------------------------#

    # 1. 趋势因子 - 完全线性计算
    price = df['收盘'].iloc[-1]
    ma20 = df['MA_20'].iloc[-1]
    ma20_prev = df['MA_20'].iloc[-2]
    ma20_slope = (ma20 - ma20_prev) / ma20_prev * 100

    # 计算趋势因子（完全线性）
    slope_factor = 1.0 + ma20_slope * 0.4  # 斜率影响（每1%斜率变动，因子变动0.4）
    price_factor = 1.0 + (price - ma20) / ma20 * 3  # 价格与均线距离影响
    trend_factor = max(0.6, min(1.4, slope_factor * price_factor))

    # 2. 通用平滑评分函数
    def smooth_score(value, low, high, max_score=1.0):
        """使用Sigmoid函数实现平滑评分，避免硬边界"""
        normalized = (value - (low + high) / 2) / ((high - low) / 4)
        return max_score / (1 + np.exp(-normalized))

    # 3. 技术指标评分 - 完全平滑
    rsi_normalized = (scores['RSI'] - 50) / 40
    rsi_score = 0.8 / (1 + np.exp(-rsi_normalized * 3))

    macd_score = smooth_score(scores['MACD'], 0, 30) * (1.0 + smooth_score(banking_ind['MACD_hist_diff'], 0, 10, 0.5))
    wr_score = smooth_score(-scores['WR'], 20, 80)
    cci_score = smooth_score(scores['CCI'], 0, 200)

    strong_buy_score = (
            0.25 * rsi_score +
            0.25 * macd_score +
            0.25 * wr_score +
            0.25 * cci_score
    )

    # 4. 量价关系验证 - 动态调整（消除二元判断）
    price_change = (df['收盘'].iloc[-1] - df['收盘'].iloc[-2]) / df['收盘'].iloc[-2] * 100
    volume_change = banking_ind['OBV_change']
    bb_position = scores['BB_position']

    # 计算价格和成交量变化的相关性（-1到1之间）
    correlation = np.sign(price_change) * np.sign(volume_change)
    # 根据相关性和价格变动幅度动态调整因子
    volume_factor = 1.0 + max(0, correlation * abs(price_change) * 0.2) * (bb_position / 100)
    volume_confirm = min(1.2, volume_factor)  # 限制最大增强幅度

    # 5. 最终得分修正 - 增加基础指标权重
    final_score = total_score * 0.7 + total_score * 0.3 * trend_factor * volume_confirm * (0.5 + strong_buy_score)

    return final_score
