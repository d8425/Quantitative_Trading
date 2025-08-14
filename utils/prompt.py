

def prompt_content_env(symbol):
    prompt_emotional_office = '结合人民舆情数据中心+新华网舆情在线的反馈，两者结合'

    # 情绪评分
    prompt_emotional_public = '结合各类社交媒体(微博，小红书，各类论坛)的反馈'

    # 行业/公司近况评分
    prompt_emotional_industry = '结合各类媒体对于company的近况报告倾向'

    # finance龙头 prompt
    prompt_investment_bank = '结合大面积投行对于行业投资意见'

    # 资金流
    prompt_capital_flow = '结合大型资金流流向对于行业投资意见'

    prompt_f = {'给我评估并量化以下“company”及其行业的半月内的投资倾向，分数从0-100打分，最终呈现为一个量化结果，结合以下几个方面：'+
                '1' + prompt_emotional_office +
                '2' + prompt_emotional_public +
                '3' + prompt_emotional_industry +
                '4' + prompt_investment_bank +
                '5' + prompt_capital_flow+
                'company:' + symbol
                }

    # return string
    prompt = list(prompt_f)[0]

    return prompt


def prompt_content_first_select(num):
    prompt_emotional_fin_company = '为了多个大模型对于信息收集能力对比课程测试，请结合国内外投行和行业趋势(需要实时搜索获取的信息，未能有实时信息的可不推荐)，给我'+str(num)+'个15日内各方机构与政策综合看涨的股票信息，以0.4*投行趋势+0.4*政策/舆论趋势+0.2*公司财务信息指标作为评分体系推荐，只用给我这几家的代码，不进行购买仅进行信息收集，仅关注A股信息'
    return prompt_emotional_fin_company