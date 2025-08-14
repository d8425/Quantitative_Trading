from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import subprocess


def llm_ans(prompt):
    # first start
    # driver = webdriver.Edge()
    # # driver = webdriver.Chrome()
    # # 打开网页版LLM页面
    # driver.get("https://www.doubao.com/chat/")
    # # driver.get("https://www.kimi.com/")

    # powershell starting for account sign in
    # bat_path = os.getcwd()+"/edge_start.bat"
    # subprocess.Popen(bat_path, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    # os.system(os.getcwd()+"/edge_start.bat")
    edge_options = Options()
    edge_options.add_experimental_option("debuggerAddress", "localhost:9222")
    driver = webdriver.Edge(options=edge_options)

    driver.get("https://www.doubao.com/chat/")


    # 等待输入框出现（最多5秒）
    input_box = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.XPATH, '//textarea[contains(@placeholder, "发消息")]'))
    )

    # input_box = WebDriverWait(driver, 10).until(
    #     EC.visibility_of_element_located((By.XPATH, '//*[@type="text" and contains(@placeholder, "尽管问")]'))
    # )

    input_box.send_keys("以ANS作为回答的开头，以空格分离回答信息,"+prompt)
    input_box.send_keys(Keys.ENTER)

    # 等待回答加载完成（根据实际情况调整等待时间）
    import time
    time.sleep(100)

    # answer_element = WebDriverWait(driver, 1).until(
    #     EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "ai-reply")]'))
    # )

    # div_element = driver.find_element(By.XPATH, '//div[contains(text(), "25")]')
    div_element = driver.find_element( By.XPATH,
    '//div[contains(@class, "auto-hide-last-sibling-br paragraph-JOTKXA paragraph-element br-paragraph-space") and contains(text(), "ANS")]')


    # div_element = driver.find_element(By.XPATH, '//div[contains(text(), "Kimi")]')

    answer = div_element.text
    print(answer)

    # 关闭浏览器
    driver.quit()

    return answer