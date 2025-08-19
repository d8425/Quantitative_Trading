import high_freq_check
import finance_info
import numpy as np
import akshare as ak
from pypushdeer import PushDeer

def score_indicator(indicator_name, value):
    """将单个指标值转换为-1~1的分数（1=强烈看多，-1=强烈看空）"""
    if np.isnan(value):
        return 0  # 缺失值按中性处理

    # 趋势类指标
    if indicator_name == 'ADX':
        # ADX>25有趋势，越大趋势越强（配合方向指标）
        # 此处简化：ADX越高，对现有趋势的强化越强（结合MACD方向）
        return min(value / 50, 1)  # 50以上视为强趋势，得1分

    if indicator_name == 'MACD_hist':
        # 柱状线正值看多，负值看空，绝对值越大信号越强
        return np.clip(value * 10, -1, 1)  # 放大信号（假设MACD_hist范围-0.1~0.1）

    if indicator_name == 'BB_position':
        # 布林带位置：<0.3超卖（看多），>0.7超买（看空），中间线性
        if value < 0.3:
            return 1 - (value / 0.3)
        elif value > 0.7:
            return (0.7 - value) / 0.3
        else:
            return 0

    # 动量类指标
    if indicator_name == 'RSI':
        # RSI<30超卖（1分），>70超买（-1分），中间线性
        if value < 30:
            return (30 - value) / 30
        elif value > 70:
            return (70 - value) / 30
        else:
            return (value - 50) / 20  # 50为中性

    if indicator_name == 'MOM':
        # 动量为正看多，负看空，绝对值越大分越高
        return np.clip(value / 5, -1, 1)  # 假设动量范围-5~5

    if indicator_name == 'ROC':
        # 变化率为正看多，负看空
        return np.clip(value / 10, -1, 1)  # 10%以上视为强上涨

    # 资金类指标
    if indicator_name == 'MFI':
        # MFI<20超卖（1分），>80超买（-1分），中间线性
        if value < 20:
            return (20 - value) / 20
        elif value > 80:
            return (80 - value) / 20
        else:
            return (value - 50) / 30

    if indicator_name == 'OBV_change':
        # 能量潮变化为正看多，负看空
        return np.clip(value, -1, 1)  # 假设变化率范围-1~1

    if indicator_name == 'Volume_Change_Rate':
        # 成交量放大且价格上涨（ROC>0）则加分，反之减分
        # 先获取ROC值（需从数据中传入，此处简化）
        roc = 6.73  # 你的数据中ROC为6.73（正值）
        volume_score = np.clip(value / 200, -1, 1)  # 200%以上视为显著放大
        return volume_score if roc > 0 else -volume_score  # 量价同步才加分

    # 波动/乖离类指标
    if indicator_name == 'BIAS':
        # BIAS<-5%超卖（1分），>5%超买（-1分）
        return np.clip(-value / 5, -1, 1)  # 正值越大（偏离越高）分越低

    if indicator_name == 'WR':
        # WR<-20超买（-1分），>-80超卖（1分）
        return np.clip((value + 50) / 30, -1, 1)  # -50为中性

    if indicator_name == 'ATR':
        # ATR反映波动性，不直接看多空，此处返回0（用于后续调整权重）
        return 0

    return 0  # 未定义的指标按中性处理


def calculate_investment_coefficient(historical_indicators, realtime_indicators):
    """
    结合历史和实时指标计算投资系数并分档
    参数：historical_indicators（历史指标字典）、realtime_indicators（实时指标字典）
    返回：(投资系数, 分档结果)
    """
    # 合并指标字典
    all_indicators = {**historical_indicators, **realtime_indicators}

    # 计算加权总分（投资系数）
    total_score = 0
    for indicator, weight in INDICATOR_WEIGHTS.items():
        if indicator in all_indicators:
            score = score_indicator(indicator, all_indicators[indicator])
            total_score += score * weight

    # 计算波动性调整因子（ATR越大，信号权重降低，避免高波动误判）
    atr = all_indicators.get('ATR', 0.5)
    price = all_indicators.get('收盘', 10)
    volatility_ratio = atr / price  # 波动占价格比例
    adjust_factor = max(1 - volatility_ratio * 10, 0.5)  # 高波动时最低保留50%权重
    final_coefficient = total_score * adjust_factor

    # 分档规则（可根据策略调整）
    if final_coefficient >= 0.6:
        return (final_coefficient, "强烈买入")
    elif 0.2 <= final_coefficient < 0.6:
        return (final_coefficient, "买入")
    elif -0.2 < final_coefficient < 0.2:
        return (final_coefficient, "持有")
    elif -0.6 < final_coefficient <= -0.2:
        return (final_coefficient, "卖出")
    else:
        return (final_coefficient, "强烈卖出")


# 指标分类及权重（可根据策略调整）
INDICATOR_WEIGHTS = {
    # 趋势类（30%）：判断中长期方向
    'ADX': 0.1,
    'MACD_hist': 0.1,
    'BB_position': 0.1,
    # 动量类（25%）：判断短期涨跌动能
    'RSI': 0.08,
    'MOM': 0.07,
    'ROC': 0.1,
    # 资金类（25%）：判断资金流入流出
    'MFI': 0.1,
    'OBV_change': 0.08,
    'Volume_Change_Rate': 0.07,
    # 波动/乖离类（20%）：判断价格偏离程度
    'BIAS': 0.08,
    'WR': 0.07,
    'ATR': 0.05  # ATR本身不直接看多空，用于调整其他信号权重
}

def main_high_freq(symbol_list):
    # symbol_list = ['603163' '300750' '002997' '300724' '300870' '002466' '002460' '002008' '301162' '002353']
    days_ago = 50  # history data days
    period = 17  # fin_ind days


    # twice/days
    # real time metrics
    # real time original data
    data_spot = ak.stock_zh_a_spot()
    str_result = ''
    for symbol in symbol_list:
        # stable index
        df_stable = finance_info.bank_cal(symbol, period, days_ago)

        # real time index
        df_real_time = high_freq_check.high_freq(symbol, period, days_ago, data_spot)

        # 计算结果
        coefficient, grade = calculate_investment_coefficient(df_stable[-1].to_dict(), df_real_time.to_dict())
        str_result = str_result+'\n'+symbol+': '+str(coefficient)+'-'+grade

    pushdeer_ding = PushDeer(pushkey="PDU36046TfIe7SgbaLY1OWrvHnyBF6mMcudbGcVaW")  # ding
    # pushdeer_yi = PushDeer(pushkey="PDU36425TtwSeJJ8zXEfSG4lALYJPIKHsKchLhZAP")  # yi
    #
    # message = my_bank.symbol_code
    # mess_str = ''
    # idx = 0
    # for i in message:
    #     mess_str = mess_str + '\n' + i + ' - ' + str(result[idx])
    #     idx = idx + 1
    pushdeer_ding.send_text(text='Message', desp=str_result)
    # pushdeer_yi.send_text(text='Message', desp=mess_str)

    print(symbol+": "+f"投资系数：{coefficient:.2f}，分档结果：{grade}")

