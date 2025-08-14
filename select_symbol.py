# select finance: first selection(100) and quantified result for second selection(5)
from utils import llm_quantization
import utils.prompt as prompt
import utils.llm as llm
import numpy as np


# 信息获取api受限，通过llm实现first select
def select_first(num, is_test=False):
    if is_test is True:
        result = 'ANS 000002'
    else:
        prompt_f = prompt.prompt_content_first_select(num)
        result = llm.llm_ans(prompt_f)
    # code sort
    result = result.split(' ')[1::]
    return result


# 在对first select的列表中进行量化后进行second 选择
def select_second(symbol_list, symbol_quantization_result):
    index = np.argsort(symbol_quantization_result)[::-1]
    result = np.array(symbol_list)[index]
    symbol_quantization_result = np.array(symbol_quantization_result)[index]
    return result, symbol_quantization_result
