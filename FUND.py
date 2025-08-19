import utils.prompt as prompt
import utils.llm as llm
# import communication_to_moblie
from pypushdeer import PushDeer

prompt = prompt.FUND_select_from_Investment_Bank()
result = llm.llm_ans(prompt)

pushdeer_ding = PushDeer(pushkey="PDU36046TfIe7SgbaLY1OWrvHnyBF6mMcudbGcVaW")
pushdeer_yi = PushDeer(pushkey="PDU36425TtwSeJJ8zXEfSG4lALYJPIKHsKchLhZAP")  # yi

# message = my_bank.symbol_code
# mess_str = ''
# idx = 0
# for i in message:
#     mess_str = mess_str + '\n' + i + ' - ' + str(result[idx])
#     idx = idx + 1
# pushdeer_ding.send_text(text='Message', desp=mess_str)
pushdeer_yi.send_text(text='Message', desp=result)
pushdeer_ding.send_text(text='Message', desp=result)


