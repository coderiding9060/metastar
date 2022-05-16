from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import logging
import os
import json

# 로그 생성
logger = logging.getLogger()

# 로그의 출력 기준 설정
logger.setLevel(logging.INFO)

# log 출력 형식
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# log 출력
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# log를 파일에 출력
file_handler = logging.FileHandler('eum.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# log 사용
# createLog()
# createLog.logger.info(1)

class eumDownloadPDF():

    def __init__(self, userId, passWd, option):
        self.option = option
        # self.option.headless = True # 창이 없음
        self.option.headless = False # 창이 있음
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.option)
        self.userId = userId
        self.pwd = passWd

    def wait_for(self, locator):
        return WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(locator)
        )

    def printing(self):
        # 인쇄
        WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(2))
        self.driver.switch_to.window(self.driver.window_handles[1])
        # 인쇄 클릭
        sleep(5) # 대기시간 조정이 안되서, sleep처리
        btnPrint = self.driver.find_element_by_id('btnPrint')
        btnPrint.click()
        sleep(5) # 10 -> 5
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def login(self):
        self.driver.get('https://www.eum.go.kr/web/mb/mbLogin.jsp')
        self.driver.find_element_by_id('mbrId').send_keys(self.userId)
        self.driver.find_element_by_id('loginFormPw').send_keys(self.pwd)
        self.driver.find_element_by_id('loginFormPw').send_keys(Keys.RETURN)

    # 토지이용계획
    def planning(self, address):
        self.driver.get('https://www.eum.go.kr/web/am/amMain.jsp')
        self.driver.find_element_by_class_name('addrTxt_back').send_keys(address)
        self.driver.find_element_by_class_name('addrTxt_back').send_keys(Keys.RETURN)
        sleep(3) # 5 -> 3
        self.driver.execute_script(
            """
                openLandLayer('print_layer')
            """
        )
        sleep(1)
        print_bt = self.driver.find_element_by_class_name('print_bt')
        print_bt.click()
        sleep(15) # 20 -> 10

    def close(self):
        sleep(3)
        self.driver.quit()
