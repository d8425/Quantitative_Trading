from pypushdeer import PushDeer


def communication(my_bank, result):
    pushdeer = PushDeer(pushkey="PDU36046TfIe7SgbaLY1OWrvHnyBF6mMcudbGcVaW")
    message = my_bank.symbol_code
    mess_str = ''
    idx = 0
    for i in message:
        mess_str = mess_str + '\n' +i + ' - ' + str(result[idx])
        idx = idx + 1
    pushdeer.send_text(text='Message', desp=mess_str)