import akshare as ak
import talib as ta
import numpy as np
import pandas as pd
from utils import trade_info
from datetime import date, timedelta


def high_freq(symbol, period, days_ago, data_spot):

    # today
    time = date.today()
    time_s = time.strftime("%Y%m%d")
    time_ago = time-timedelta(days=days_ago)
    time_ago_s = time_ago.strftime("%Y%m%d")

    # stable index/metrics
    df_period = trade_info.get_trade_info(symbol, time_ago_s, time_s)[['日期', '最高', '最低', '收盘', '成交量']]

    # real time original data
    df = data_spot[data_spot['代码'].str[2:] == symbol]

    # full data
    # 3. 拼接历史数据和实时数据（形成14天完整序列）
    # 构造实时数据行（用实时字段映射到历史字段格式）
    current_row = pd.DataFrame({
        '日期': pd.Timestamp.now().strftime('%Y-%m-%d'),  # 当前日期
        '最高': df['最高'].iloc[0],  # 实时最高价
        '最低': df['最低'].iloc[0],  # 实时最低价
        '收盘': df['最新价'].iloc[0],  # 用实时最新价替代收盘价
        '成交量': df['成交量'].iloc[0]  # 实时累计成交量
    }, index=[0])

    # 拼接：历史13天 + 当前1天 → 共14天
    full_df = pd.concat([df_period, current_row], ignore_index=True)
    len_full_df = len(full_df)-1

    # 新增指标1：资金流向指数（MFI）
    full_df['MFI'] = ta.MFI(full_df['最高'], full_df['最低'], full_df['收盘'], full_df['成交量'], timeperiod=period).iloc[-1]

    # 新增指标2：乖离率（BIAS，基于period日MA）
    ma = ta.MA(full_df['收盘'], timeperiod=period).iloc[-1]
    full_df['BIAS'] = (full_df['收盘'].iloc[-1] - ma) / ma * 100 if ma != 0 else np.nan

    # 新增指标3：真实波幅（ATR）
    full_df['ATR'] = ta.ATR(full_df['最高'], full_df['最低'], full_df['收盘'], timeperiod=period).iloc[-1]

    # 新增指标4：成交量变化率（基于5日平均）
    vol_mean = full_df['成交量'].iloc[-5:].mean()  # 近5日平均成交量
    full_df['Volume_Change_Rate'] = (full_df['成交量'].iloc[-1] - vol_mean) / vol_mean * 100 if vol_mean != 0 else np.nan

    # 新增指标5：价格变化率（ROC）
    past_close = full_df['收盘'].iloc[-1]
    full_df['ROC'] = (full_df['收盘'].iloc[-1] - past_close) / past_close * 100 if past_close != 0 else np.nan

    # 新增指标6：心理线（PSY，基于12日）
    current_close = full_df['收盘'].iloc[-1]
    past_close = full_df['收盘'].iloc[-len_full_df]  # 注意这里是 -period 而不是 -1

    # # 计算ROC并赋值给最后一行（因为只有最新行有完整的N期数据）
    # full_df.at[full_df.index[-1], 'ROC'] = (current_close - past_close) / past_close * 100 if past_close != 0 else np.nan

    # 处理缺失值并返回最新数据
    full_df = full_df.dropna()
    latest_data = full_df.iloc[-1].copy() if not full_df.empty else None

    return latest_data
