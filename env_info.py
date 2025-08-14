# 政策+舆论+龙头倾向+资金流
from utils import llm_quantization
import utils.prompt as prompt
import utils.llm as llm
import numpy as np

def quantization(symbol, is_test=False):
    if is_test is True:
        # result = "2025-07-19 90"
        result = 90
    else:
        prompt_f = prompt.prompt_content_env(symbol)
        result = llm.llm_ans(prompt_f)
        # result sort
        result = result.split(' ')[1::]
        result = sum(np.double(result))/len(result)
    return result
