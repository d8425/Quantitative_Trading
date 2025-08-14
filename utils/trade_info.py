import akshare as ak
import pandas as pd

def get_trade_info(symbol,start_time,end_time):  # 股市信息
    # stock_info_a_code_name = ak.stock_info_a_code_name()
    # print(stock_info_a_code_name.head())

    # history data
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=symbol, period="daily",
                                             start_date=str(start_time), end_date=str(end_time), adjust="qfq")

    # latest data
    spot_df = ak.stock_zh_a_spot()
    latest_data = spot_df[spot_df["代码"].str[2:] == symbol].iloc[0]

    # update
    new_row = pd.DataFrame({
        "日期": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "开盘价": latest_data["今开"],
        "最高价": latest_data["最高"],
        "最低价": latest_data["最低"],
        "收盘价": latest_data["最新价"],
        "成交量": latest_data["成交量"],
        # 其他字段按需补充
    }, index=[0])

    stock_zh_a_hist_df_new = pd.concat([stock_zh_a_hist_df.iloc[:-1], new_row], ignore_index=True)

    return stock_zh_a_hist_df_new



def get_company_fin_info(stock_code: str, year: str = "2025") -> pd.DataFrame:
    """
    获取公司财务数据，包含指定列。

    Args:
        stock_code (str): 股票代码，例如 "600519"（贵州茅台）
        year (str): 财务报表年份，默认为 "2024"

    Returns:
        pd.DataFrame: 包含指定财务字段的 DataFrame
    """
    # 初始化 DataFrame
    columns = [
        'total_assets', 'total_liabilities', 'total_equity', 'current_assets',
        'current_liabilities', 'net_income', 'revenue', 'ebitda', 'cash',
        'interest_expense', 'operating_cash_flow', 'shares_outstanding'
    ]
    financial_data = pd.DataFrame(columns=columns, index=[0])

    try:
        # 获取资产负债表
        balance_sheet = ak.stock_financial_report_sina(stock=stock_code, symbol="资产负债表")
        # 获取利润表
        income_statement = ak.stock_financial_report_sina(stock=stock_code, symbol="利润表")
        # 获取现金流量表
        cash_flow = ak.stock_financial_report_sina(stock=stock_code, symbol="现金流量表")

        # 获取最近一年的数据（假设最新报告为指定年份）
        balance_sheet = balance_sheet[balance_sheet['报告日'].str.contains(year)]
        income_statement = income_statement[income_statement['报告日'].str.contains(year)]
        cash_flow = cash_flow[cash_flow['报告日'].str.contains(year)]

        # 从资产负债表提取数据
        if not balance_sheet.empty:
            financial_data['total_assets'] = balance_sheet.get('资产总计', pd.Series([None])).iloc[0]
            financial_data['total_liabilities'] = balance_sheet.get('负债合计', pd.Series([None])).iloc[0]
            financial_data['total_equity'] = balance_sheet.get('所有者权益(或股东权益)合计', pd.Series([None])).iloc[0]
            financial_data['current_assets'] = balance_sheet.get('流动资产合计', pd.Series([None])).iloc[0]
            financial_data['current_liabilities'] = balance_sheet.get('流动负债合计', pd.Series([None])).iloc[0]
            financial_data['cash'] = balance_sheet.get('货币资金', pd.Series([None])).iloc[0]

        # 从利润表提取数据
        if not income_statement.empty:
            financial_data['net_income'] = income_statement.get('净利润', pd.Series([None])).iloc[0]
            financial_data['revenue'] = income_statement.get('营业收入', pd.Series([None])).iloc[0]
            financial_data['interest_expense'] = income_statement.get('财务费用', pd.Series([None])).iloc[0]
            # EBITDA 需计算：营业利润 + 折旧与摊销（AKShare 未直接提供折旧摊销，设为 None 或需其他接口）
            financial_data['ebitda'] = None  # 需额外数据源或假设

        # 从现金流量表提取数据
        if not cash_flow.empty:
            financial_data['operating_cash_flow'] = cash_flow.get('经营活动产生的现金流量净额', pd.Series([None])).iloc[0]

        # 获取总股本（流通股本或总股本）
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        financial_data['shares_outstanding'] = stock_info.get('总股本', pd.Series([None])).iloc[0]

        # 数据清洗：将缺失值替换为 None 或 0（根据需求）
        financial_data.fillna(0, inplace=True)

        return financial_data

    except Exception as e:
        print(f"Error fetching financial data: {e}")
        return pd.DataFrame(columns=columns)