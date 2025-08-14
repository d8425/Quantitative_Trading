import akshare as ak
import pandas as pd
import utils.trade_info as trade_info
from datetime import date, timedelta


def info_cluster_f(bank, second_symbol_list, period=15, days_ago=50):
    # today
    time = date.today()
    time_s = time.strftime("%Y%m%d")
    time_ago = time-timedelta(days=days_ago)
    time_ago_s = time_ago.strftime("%Y%m%d")

    # close info
    # for symbol in second_symbol_list:
    #     info = trade_info.get_trade_info(symbol, time_ago_s, time_s)

    # info cluster into bank
    bank.symbol_code = second_symbol_list
    return bank
