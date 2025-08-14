import finance_qualification_assessment
import finance_info
import env_info
import select_symbol
import initial_bank
import breaker
import info_cluster
import communication_to_moblie
import datetime

# -1.param initial
total = 2000  # money
days_ago = 50  # history data days
period = 14  # fin_ind days
num = 10
symbol_idx = 0
result = []

is_test = True
# is_test = False

# 0.initialization
my_bank = initial_bank.Bank()

# 1.selection first
symbol_list = select_symbol.select_first(num,is_test)

for symbol in symbol_list:
    # 2.finance Qualification assessment3
    result_fq = finance_qualification_assessment.quantization(symbol)

    # 3.banking quantization(1move/day)
    result_bk = finance_info.quantization(symbol, period, days_ago)

    # 4.environment quantization(3move/day) (Public Opinion and Policy)   since first selection has done those, step can be ignored
    # result_env = env_info.quantization(symbol, is_test)

    # 5.final quantization (Industry classification, multi-ind balance) 334:stable 442:long line 235:short line
    result.append(0.3*result_fq+0.7*result_bk)

    symbol_idx = symbol_idx+1

# 6.selection second
second_symbol_list, result = select_symbol.select_second(symbol_list, result)

# 7.info cluster
my_bank = info_cluster.info_cluster_f(my_bank, second_symbol_list, period, days_ago)

# 7.circuit breaker
breaker.bank_breaking(my_bank)

# 8.sell
# by manual

# 9.buy
# by manual

# 10.communication
communication_to_moblie.communication(my_bank, result)

print(datetime.datetime.now(), ' done')
