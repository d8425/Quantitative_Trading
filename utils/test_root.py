from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Edge()
# driver = webdriver.Chrome()
# 打开网页版LLM页面
driver.get("https://www.doubao.com/chat/")
# driver.get("https://www.kimi.com/")

# 定位到输入框元素并输入问题

# 等待输入框出现（最多10秒）
input_box = WebDriverWait(driver, 5).until(
    EC.visibility_of_element_located((By.XPATH, '//textarea[contains(@placeholder, "发消息")]'))
)

# input_box = WebDriverWait(driver, 10).until(
#     EC.visibility_of_element_located((By.XPATH, '//*[@type="text" and contains(@placeholder, "尽管问")]'))
# )

input_box.send_keys("以你的模型名字拼音+':'为开头+回答文字少于100，简短介绍下2025年6月的科技新闻")
input_box.send_keys(Keys.ENTER)

# 等待回答加载完成（根据实际情况调整等待时间）
import time
time.sleep(10)

# answer_element = WebDriverWait(driver, 1).until(
#     EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "ai-reply")]'))
# )

div_element = driver.find_element(By.XPATH, '//div[contains(text(), "doubao")]')
# div_element = driver.find_element(By.XPATH, '//div[contains(text(), "Kimi")]')

answer = div_element.text
print(answer)

# 关闭浏览器
driver.quit()