import pandas as pd
import numpy as np
import utils.trade_info as trade_info


def _calculate_financial_metrics(symbol):
    """
    计算公司财务评估指标（基于财务报表数据）

    参数:
    financial_data: 包含财务数据的DataFrame，需包含列:
        'total_assets', 'total_liabilities', 'total_equity', 'current_assets',
        'current_liabilities', 'net_income', 'revenue', 'ebitda', 'cash',
        'interest_expense', 'operating_cash_flow', 'shares_outstanding'

    返回:
    metrics: 包含财务指标的DataFrame
    """

    financial_data = trade_info.get_company_fin_info(symbol)
    metrics = financial_data.copy()

    # 1. 偿债能力指标
    metrics['debt_ratio'] = metrics['total_liabilities'] / metrics['total_assets']  # 资产负债率
    metrics['debt_to_equity'] = metrics['total_liabilities'] / metrics['total_equity']  # 产权比率
    metrics['current_ratio'] = metrics['current_assets'] / metrics['current_liabilities']  # 流动比率
    metrics['quick_ratio'] = (metrics['current_assets'] - metrics.get('inventory', 0)) / metrics[
        'current_liabilities']  # 速动比率
    metrics['cash_ratio'] = metrics['cash'] / metrics['current_liabilities']  # 现金比率
    metrics['interest_coverage'] = metrics['ebitda'] / metrics['interest_expense']  # 利息保障倍数

    # 2. 盈利能力指标
    metrics['gross_margin'] = (metrics['revenue'] - metrics.get('cost_of_goods_sold', 0)) / metrics['revenue']  # 毛利率
    metrics['operating_margin'] = metrics.get('operating_income', metrics['ebitda']) / metrics['revenue']  # 营业利润率
    metrics['net_profit_margin'] = metrics['net_income'] / metrics['revenue']  # 净利润率
    metrics['return_on_assets'] = metrics['net_income'] / metrics['total_assets']  # 资产回报率(ROA)
    metrics['return_on_equity'] = metrics['net_income'] / metrics['total_equity']  # 权益回报率(ROE)
    metrics['return_on_invested_capital'] = metrics.get('ebit', metrics['ebitda']) / (
                metrics['total_assets'] - metrics['current_liabilities'])  # ROIC

    # 3. 运营效率指标
    metrics['asset_turnover'] = metrics['revenue'] / metrics['total_assets']  # 资产周转率
    metrics['inventory_turnover'] = metrics.get('cost_of_goods_sold', metrics['revenue']) / metrics.get('inventory',
                                                                                                        1)  # 存货周转率
    metrics['receivables_turnover'] = metrics['revenue'] / metrics.get('accounts_receivable', 1)  # 应收账款周转率

    # 4. 现金流指标
    metrics['operating_cash_flow_ratio'] = metrics['operating_cash_flow'] / metrics['current_liabilities']  # 经营现金流比率
    metrics['free_cash_flow'] = metrics['operating_cash_flow'] - metrics.get('capital_expenditures', 0)  # 自由现金流
    metrics['fcfe'] = metrics['free_cash_flow'] - metrics.get('interest_expense', 0) * (
                1 - metrics.get('tax_rate', 0.25)) + metrics.get('net_borrowing', 0)  # 股权自由现金流

    # 5. 市场价值指标
    metrics['eps'] = metrics['net_income'] / metrics['shares_outstanding']  # 每股收益(EPS)
    metrics['book_value_per_share'] = metrics['total_equity'] / metrics['shares_outstanding']  # 每股账面价值
    metrics['cash_flow_per_share'] = metrics['operating_cash_flow'] / metrics['shares_outstanding']  # 每股现金流

    return metrics


def _calculate_financial_metrics_new(symbol):
    # 获取原始数据
    financial_data = trade_info.get_company_fin_info(symbol)
    # 复制数据，避免修改原始数据
    metrics = financial_data.copy()

    # 定义必需字段
    REQUIRED_FIELDS = [
        'total_assets', 'total_liabilities', 'current_assets',
        'current_liabilities', 'revenue', 'net_income',
        'shares_outstanding', 'operating_cash_flow'
    ]

    # 检查必需字段
    missing_fields = [field for field in REQUIRED_FIELDS if field not in metrics]
    if missing_fields:
        raise ValueError(f"缺少必要的财务数据: {', '.join(missing_fields)}")

    # 定义默认值字典，用于缺失数据
    DEFAULT_VALUES = {
        'inventory': 0,
        'accounts_receivable': 1,
        'cost_of_goods_sold': 0,
        'interest_expense': 1,
        'ebit': metrics.get('ebitda', 1),
        'ebitda': metrics.get('ebit', 1),
        'operating_income': metrics.get('ebitda', metrics.get('ebit', 1)),
        'capital_expenditures': 0,
        'tax_rate': 0.25,
        'net_borrowing': 0
    }

    # 使用默认值填充缺失数据
    for key, default_value in DEFAULT_VALUES.items():
        if key not in metrics:
            metrics[key] = default_value

    # 辅助函数：安全除法，处理除零错误
    def safe_divide(numerator, denominator, default=np.nan):
        if not isinstance(numerator, (int, float)) or not isinstance(denominator, (int, float)):
            return default
        if denominator == 0:
            return default
        return numerator / denominator

    # 1. 偿债能力指标
    metrics['debt_ratio'] = safe_divide(metrics['total_liabilities'], metrics['total_assets'])  # 资产负债率
    metrics['debt_to_equity'] = safe_divide(metrics['total_liabilities'], metrics.get('total_equity', 1))  # 产权比率
    metrics['current_ratio'] = safe_divide(metrics['current_assets'], metrics['current_liabilities'])  # 流动比率
    metrics['quick_ratio'] = safe_divide(
        metrics['current_assets'] - metrics['inventory'],
        metrics['current_liabilities']
    )  # 速动比率
    metrics['cash_ratio'] = safe_divide(metrics.get('cash', 0), metrics['current_liabilities'])  # 现金比率
    metrics['interest_coverage'] = safe_divide(metrics.get('ebit', metrics['ebitda']),
                                               metrics['interest_expense'])  # 利息保障倍数

    # 2. 盈利能力指标
    metrics['gross_margin'] = safe_divide(
        metrics['revenue'] - metrics['cost_of_goods_sold'],
        metrics['revenue']
    )  # 毛利率
    metrics['operating_margin'] = safe_divide(
        metrics.get('operating_income', metrics['ebitda']),
        metrics['revenue']
    )  # 营业利润率
    metrics['net_profit_margin'] = safe_divide(metrics['net_income'], metrics['revenue'])  # 净利润率
    metrics['return_on_assets'] = safe_divide(metrics['net_income'], metrics['total_assets'])  # 资产回报率(ROA)
    metrics['return_on_equity'] = safe_divide(metrics['net_income'], metrics.get('total_equity', 1))  # 权益回报率(ROE)
    metrics['return_on_invested_capital'] = safe_divide(
        metrics.get('ebit', metrics['ebitda']),
        metrics['total_assets'] - metrics['current_liabilities']
    )  # ROIC

    # 3. 运营效率指标
    metrics['asset_turnover'] = safe_divide(metrics['revenue'], metrics['total_assets'])  # 资产周转率
    metrics['inventory_turnover'] = safe_divide(
        metrics.get('cost_of_goods_sold', metrics['revenue']),
        metrics['inventory'] or 1
    )  # 存货周转率
    metrics['receivables_turnover'] = safe_divide(
        metrics['revenue'],
        metrics['accounts_receivable'] or 1
    )  # 应收账款周转率

    # 4. 现金流指标
    metrics['operating_cash_flow_ratio'] = safe_divide(
        metrics['operating_cash_flow'],
        metrics['current_liabilities']
    )  # 经营现金流比率
    metrics['free_cash_flow'] = metrics['operating_cash_flow'] - metrics['capital_expenditures']  # 自由现金流
    metrics['fcfe'] = metrics['free_cash_flow'] - metrics['interest_expense'] * (1 - metrics['tax_rate']) + metrics[
        'net_borrowing']  # 股权自由现金流

    # 5. 市场价值指标
    metrics['eps'] = safe_divide(metrics['net_income'], metrics['shares_outstanding'])  # 每股收益(EPS)
    metrics['book_value_per_share'] = safe_divide(metrics.get('total_equity', 0),
                                                  metrics['shares_outstanding'])  # 每股账面价值
    metrics['cash_flow_per_share'] = safe_divide(metrics['operating_cash_flow'], metrics['shares_outstanding'])  # 每股现金流

    return metrics




def calculate_financial_health_score(financial_data, industry_benchmarks=None):
    """
    计算公司财务健康评分和投资趋势分析

    参数:
    financial_data (dict): 包含财务指标的字典
    industry_benchmarks (dict, optional): 行业基准值，用于比较

    返回:
    dict: 包含评分和分析结果的字典
    """
    metrics = financial_data.copy()

    # 定义指标权重
    weights = {
        # 偿债能力 (30%)
        'debt_ratio': 0.05,  # 越低越好
        'debt_to_equity': 0.05,  # 越低越好
        'current_ratio': 0.05,  # 1.5-2.5为佳
        'quick_ratio': 0.05,  # 1左右为佳
        'cash_ratio': 0.05,  # 0.5-1为佳
        'interest_coverage': 0.05,  # 越高越好

        # 盈利能力 (30%)
        'gross_margin': 0.05,  # 越高越好
        'operating_margin': 0.05,  # 越高越好
        'net_profit_margin': 0.05,  # 越高越好
        'return_on_assets': 0.05,  # 越高越好
        'return_on_equity': 0.05,  # 越高越好
        'return_on_invested_capital': 0.05,  # 越高越好

        # 运营效率 (20%)
        'asset_turnover': 0.07,  # 越高越好
        'inventory_turnover': 0.07,  # 行业相关，适中为佳
        'receivables_turnover': 0.06,  # 越高越好

        # 现金流 (15%)
        'operating_cash_flow_ratio': 0.05,  # 越高越好
        'free_cash_flow': 0.05,  # 越高越好
        'fcfe': 0.05,  # 越高越好

        # 市场价值 (5%)
        'eps': 0.02,  # 越高越好
        'book_value_per_share': 0.02,  # 越高越好
        'cash_flow_per_share': 0.01  # 越高越好
    }

    # 定义指标评分函数
    def score_debt_ratio(value):
        """资产负债率评分 (越低越好)"""
        if value < 0.4:
            return 90
        elif value < 0.6:
            return 70
        elif value < 0.8:
            return 50
        else:
            return 30

    def score_debt_to_equity(value):
        """产权比率评分 (越低越好)"""
        if value < 1:
            return 90
        elif value < 1.5:
            return 70
        elif value < 2:
            return 50
        else:
            return 30

    def score_current_ratio(value):
        """流动比率评分 (1.5-2.5为佳)"""
        if 1.5 <= value <= 2.5:
            return 90
        elif 1.0 <= value < 1.5 or 2.5 < value <= 3.0:
            return 70
        elif 0.5 <= value < 1.0 or 3.0 < value <= 4.0:
            return 50
        else:
            return 30

    def score_quick_ratio(value):
        """速动比率评分 (1左右为佳)"""
        if 0.8 <= value <= 1.2:
            return 90
        elif 0.5 <= value < 0.8 or 1.2 < value <= 1.5:
            return 70
        elif 0.2 <= value < 0.5 or 1.5 < value <= 2.0:
            return 50
        else:
            return 30

    def score_cash_ratio(value):
        """现金比率评分 (0.5-1为佳)"""
        if 0.5 <= value <= 1.0:
            return 90
        elif 0.3 <= value < 0.5 or 1.0 < value <= 1.5:
            return 70
        elif 0.1 <= value < 0.3 or 1.5 < value <= 2.0:
            return 50
        else:
            return 30

    def score_interest_coverage(value):
        """利息保障倍数评分 (越高越好)"""
        if value > 5:
            return 90
        elif value > 3:
            return 70
        elif value > 1.5:
            return 50
        else:
            return 30

    def score_margin(value):
        """利润率评分 (越高越好)"""
        if value > 0.25:
            return 90
        elif value > 0.15:
            return 70
        elif value > 0.05:
            return 50
        else:
            return 30

    def score_return(value):
        """回报率评分 (越高越好)"""
        if value > 0.15:
            return 90
        elif value > 0.10:
            return 70
        elif value > 0.05:
            return 50
        else:
            return 30

    def score_turnover(value):
        """周转率评分 (越高越好)"""
        if value > 1.5:
            return 90
        elif value > 1.0:
            return 70
        elif value > 0.5:
            return 50
        else:
            return 30

    def score_inventory_turnover(value, industry_avg=5):
        """存货周转率评分 (行业相关，适中为佳)"""
        if industry_avg is None:
            industry_avg = 5  # 默认值
        lower = industry_avg * 0.7
        upper = industry_avg * 1.3
        if lower <= value <= upper:
            return 90
        elif (industry_avg * 0.5 <= value < lower) or (upper < value <= industry_avg * 1.5):
            return 70
        elif (industry_avg * 0.3 <= value < industry_avg * 0.5) or (industry_avg * 1.5 < value <= industry_avg * 2):
            return 50
        else:
            return 30

    def score_cash_flow(value):
        """现金流评分 (越高越好)"""
        if value > 0:
            return 80 + min(value / 10, 20)
        elif value > -5:
            return 40 + min(value / 10, 40)
        else:
            return 20

    def score_market_value(value):
        """市场价值评分 (越高越好)"""
        if value > 5:
            return 90
        elif value > 2:
            return 70
        elif value > 0:
            return 50
        else:
            return 30

    # 为每个指标计算得分
    scores = {}

    # 偿债能力指标
    scores['debt_ratio'] = score_debt_ratio(metrics['debt_ratio'][0])
    scores['debt_to_equity'] = score_debt_to_equity(metrics['debt_to_equity'][0])
    scores['current_ratio'] = score_current_ratio(metrics['current_ratio'][0])
    scores['quick_ratio'] = score_quick_ratio(metrics['quick_ratio'][0])
    scores['cash_ratio'] = score_cash_ratio(metrics['cash_ratio'][0])
    scores['interest_coverage'] = score_interest_coverage(metrics['interest_coverage'][0])

    # 盈利能力指标
    scores['gross_margin'] = score_margin(metrics['gross_margin'][0])
    scores['operating_margin'] = score_margin(metrics['operating_margin'][0])
    scores['net_profit_margin'] = score_margin(metrics['net_profit_margin'][0])
    scores['return_on_assets'] = score_return(metrics['return_on_assets'][0])
    scores['return_on_equity'] = score_return(metrics['return_on_equity'][0])
    scores['return_on_invested_capital'] = score_return(metrics['return_on_invested_capital'][0])

    # 运营效率指标
    scores['asset_turnover'] = score_turnover(metrics['asset_turnover'][0])
    inventory_industry_avg = industry_benchmarks.get('inventory_turnover') if industry_benchmarks else None
    scores['inventory_turnover'] = score_inventory_turnover(metrics['inventory_turnover'][0], inventory_industry_avg)
    scores['receivables_turnover'] = score_turnover(metrics['receivables_turnover'][0])

    # 现金流指标
    scores['operating_cash_flow_ratio'] = score_cash_flow(metrics['operating_cash_flow_ratio'][0])
    scores['free_cash_flow'] = score_cash_flow(metrics['free_cash_flow'][0])
    scores['fcfe'] = score_cash_flow(metrics['fcfe'][0])

    # 市场价值指标
    scores['eps'] = score_market_value(metrics['eps'][0])
    scores['book_value_per_share'] = score_market_value(metrics['book_value_per_share'][0])
    scores['cash_flow_per_share'] = score_market_value(metrics['cash_flow_per_share'][0])

    # 计算加权总分
    total_score = sum(scores[metric] * weights[metric] for metric in scores)

    # 生成投资趋势分析
    def get_investment_trend(score):
        if score >= 85:
            return "强烈推荐买入，财务状况极佳，投资价值高"
        elif score >= 70:
            return "推荐买入，财务状况良好，投资价值较高"
        elif score >= 55:
            return "谨慎买入，财务状况一般，存在一定风险"
        elif score >= 40:
            return "建议观望，财务状况较差，风险较高"
        else:
            return "不建议投资，财务状况不佳，风险很大"

    trend = get_investment_trend(total_score)

    # 生成详细分析报告
    def get_category_score(category_metrics):
        return sum(scores[metric] * weights[metric] for metric in category_metrics) * 100

    category_scores = {
        "偿债能力": get_category_score(
            ['debt_ratio', 'debt_to_equity', 'current_ratio', 'quick_ratio', 'cash_ratio', 'interest_coverage']),
        "盈利能力": get_category_score(
            ['gross_margin', 'operating_margin', 'net_profit_margin', 'return_on_assets', 'return_on_equity',
             'return_on_invested_capital']),
        "运营效率": get_category_score(['asset_turnover', 'inventory_turnover', 'receivables_turnover']),
        "现金流状况": get_category_score(['operating_cash_flow_ratio', 'free_cash_flow', 'fcfe']),
        "市场价值": get_category_score(['eps', 'book_value_per_share', 'cash_flow_per_share'])
    }

    analysis = {
        "总分": round(total_score, 2),
        "投资趋势": trend,
        "分类得分": category_scores,
        "详细得分": {metric: round(scores[metric], 2) for metric in scores},
        "建议": generate_advice(scores, metrics)
    }

    return analysis


def generate_advice(scores, metrics):
    """根据得分生成针对性建议"""
    advice = []

    # 偿债能力建议
    debt_metrics = ['debt_ratio', 'debt_to_equity', 'current_ratio', 'quick_ratio', 'cash_ratio', 'interest_coverage']
    avg_debt_score = sum(scores[m] for m in debt_metrics) / len(debt_metrics)
    if avg_debt_score < 50:
        advice.append("偿债能力较弱，建议关注债务水平，考虑优化资本结构，降低财务风险。")
    elif avg_debt_score < 70:
        advice.append("偿债能力一般，可适当控制负债规模，提高流动性水平。")

    # 盈利能力建议
    profit_metrics = ['gross_margin', 'operating_margin', 'net_profit_margin', 'return_on_assets', 'return_on_equity',
                      'return_on_invested_capital']
    avg_profit_score = sum(scores[m] for m in profit_metrics) / len(profit_metrics)
    if avg_profit_score < 50:
        advice.append("盈利能力较差，建议分析成本结构，寻找提高利润率的途径，如降低成本或提高售价。")
    elif avg_profit_score < 70:
        advice.append("盈利能力有待提高，可以通过优化产品线或提高运营效率来增加利润。")

    # 运营效率建议
    efficiency_metrics = ['asset_turnover', 'inventory_turnover', 'receivables_turnover']
    avg_efficiency_score = sum(scores[m] for m in efficiency_metrics) / len(efficiency_metrics)
    if avg_efficiency_score < 50:
        advice.append("运营效率较低，建议优化供应链管理，减少库存积压，提高资产利用效率。")
    elif avg_efficiency_score < 70:
        advice.append("运营效率一般，可以进一步优化业务流程，提高资产周转速度。")

    # 现金流建议
    cash_metrics = ['operating_cash_flow_ratio', 'free_cash_flow', 'fcfe']
    avg_cash_score = sum(scores[m] for m in cash_metrics) / len(cash_metrics)
    if avg_cash_score < 50:
        advice.append("现金流状况不佳，需加强应收账款管理，提高现金流稳定性，确保有足够资金支持运营。")
    elif avg_cash_score < 70:
        advice.append("现金流状况一般，建议关注经营活动现金流，确保资金能够满足短期债务需求。")

    # 市场价值建议
    market_metrics = ['eps', 'book_value_per_share', 'cash_flow_per_share']
    avg_market_score = sum(scores[m] for m in market_metrics) / len(market_metrics)
    if avg_market_score < 50:
        advice.append("市场价值指标较弱，需提升公司盈利能力和市场表现，增强投资者信心。")
    elif avg_market_score < 70:
        advice.append("市场价值有待提升，可以通过提高盈利水平和分红政策来增强股东回报。")

    # 综合建议
    if not advice:
        advice.append("公司财务状况良好，各方面指标表现均衡，建议继续保持当前经营策略。")
    else:
        advice.insert(0, "综合财务分析，公司存在以下改进空间：")

    return advice


def quantization(symbol):
    metrics = _calculate_financial_metrics(symbol)
    # metrics = _calculate_financial_metrics_new(symbol)

    # 行业基准值示例
    industry_benchmarks = {
        'inventory_turnover': 5.5
    }

    # 计算财务健康评分
    result = calculate_financial_health_score(metrics, industry_benchmarks)
    result_s = result['总分']
    return result_s
