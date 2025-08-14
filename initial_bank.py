# initial my bank

class Bank:
    def __init__(self, total_m=0, symbol_num=0, symbol_code=0, symbol_m=0, profit=0):
        self.total_m = total_m
        self.symbol_num = symbol_num # 已有symbol
        self.symbol_code = symbol_code # 已有code
        self.symbol_m = symbol_m # 已投数额
        self.profit = profit

    def __getitem__(self, item):
        if item == 'total_m':
            return self.symbol_m
        elif item == 'symbol_num':
            return self.symbol_m
        elif item == 'symbol_code':
            return self.symbol_code
        elif item == 'symbol_m':
            return self.symbol_m
        elif item == 'profit':
            return self.profit
        else:
            raise KeyError(f"invalid key: {item}")
