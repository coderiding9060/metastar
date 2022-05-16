from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
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
        self.driver.implicitly_wait(30)  # May 05, 2022 : by indigo : 페이지 로딩 완료 시간 설정 [기본값 : 0], 해당 설정을 하면 해당 driver를 사용하는 모든 코드에 적용됨
        self.userId = userId
        self.pwd = passWd

    def wait_for(self, locator):
        return WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(locator)
        )

    def printing(self):
        # 인쇄
        WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(2))
        # 인쇄 클릭
        self.driver.switch_to.window(self.driver.window_handles[1])
        sleep(3) # 대기시간 조정이 안되서, sleep처리
        btnPrint = self.driver.find_element_by_id('btnPrint')
        btnPrint.click()
        sleep(3) # 10 -> 3
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.close()
    
    # May 08, 2022 : by indigo : 기존 login함수 임시 주석 처리[]
    # def login(self):
    #     self.driver.get('https://www.eum.go.kr/web/mb/mbLogin.jsp')
    #     self.driver.find_element_by_id('mbrId').send_keys(self.userId)
    #     self.driver.find_element_by_id('loginFormPw').send_keys(self.pwd)
    #     self.driver.find_element_by_id('loginFormPw').send_keys(Keys.RETURN)

    # 토지이용계획
    def planning(self, address):
        # self.driver.get('https://www.eum.go.kr/web/ar/lu/luLandDet.jsp')
        self.driver.get('https://www.eum.go.kr/web/am/amMain.jsp')
        delay = 10
        locator_type = 'CLASS'
        locator_name = 'addrTxt_back'
        self.element_input_text(delay, locator_type, locator_name, address)
        # sleep(1)
        # locator_type = 'XPATH'
        # locator_name = '//*[@id="recent"]/div[2]/div/ul/li/a'
        # sleep(1)
        # self.element_click(delay, locator_type, locator_name, '')
        # locator_type = 'XPATH'
        # locator_name = '//*[@id="frm"]/fieldset/div[3]/p/span/a'
        
        # self.driver.find_element_by_class_name('addrTxt_back').send_keys(address)
        self.driver.find_element_by_class_name('addrTxt_back').send_keys(Keys.RETURN)
        sleep(3)
        self.driver.execute_script(
            """
            if(document.readyState === "complete") {
                openLandLayer('print_layer');
            }
            """
        )
        locator_name = 'print_bt'
        self.element_click(delay, locator_type, locator_name, '')
        # print_bt = self.driver.find_element_by_class_name('print_bt')
        # print_bt.click()
        # sleep(30)
        WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(3))
        sleep(2)
        print("창뜸")

    # May 08, 2022 : by indigo : 셀레니움 텍스트 입력 이벤트 함수 추가
    def close_alert(self, delay):
        """
        delay : wait할 시간(초)\n
        locator : 엘리멘트 locator ex) 태그 ID 중 'user_id'을 셀렉트 하고자 하는 경우 => (By.ID, 'user_id')으로 선언\n
        [locator_type]\n
        ID : 태그 ID로 검색
        NAME : 태그 name으로 검색
        CLASS : 태그 클래스로 검색
        CSS: 태그 css 속성으로 검색
        TEXT: partial link text로 검색
        locator_name : 엘리멘트 이름
        """
        try:
            WebDriverWait(self.driver, delay).until(
                EC.alert_is_present())  # 페이지에 있는 모든 element(locator로 지정한)를 delay(초)동안 찾습니다.
        except TimeoutError as e:  # delay(초)를 초과한 경우
            print('TimeoutError! ' + str(e))
            return False
        except NoSuchElementException as e:  # 해당 엘리먼트가 존재 하지 않는 경우
            print('NoSuchElementException! ' + str(e))
            return False
        except Exception as e:  # 기타 예외
            print('Exception! ' + str(e))
            return False
        else:  # 예외가 발생하지 않은 경우
            alert = self.driver.switch_to.alert
            alert.accept()
            self.driver.switch_to.window(self.driver.window_handles[0])
            return True

    # May 08, 2022 : by indigo : 셀레니움 텍스트 입력 이벤트 함수 추가
    def change_window(self, delay, current_handles, index_number):
        """
        delay : wait할 시간(초)\n
        locator : 엘리멘트 locator ex) 태그 ID 중 'user_id'을 셀렉트 하고자 하는 경우 => (By.ID, 'user_id')으로 선언\n
        [locator_type]\n
        ID : 태그 ID로 검색
        NAME : 태그 name으로 검색
        CLASS : 태그 클래스로 검색
        CSS: 태그 css 속성으로 검색
        TEXT: partial link text로 검색
        locator_name : 엘리멘트 이름
        """
        try:
            WebDriverWait(self.driver, delay).until(
                EC.new_window_is_opened(current_handles)
            )  # 페이지에 있는 모든 element(locator로 지정한)를 delay(초)동안 찾습니다.
        except TimeoutError as e:  # delay(초)를 초과한 경우
            print('TimeoutError! ' + str(e))
            return False
        except NoSuchElementException as e:  # 해당 엘리먼트가 존재 하지 않는 경우
            print('NoSuchElementException! ' + str(e))
            return False
        except Exception as e:  # 기타 예외
            print('Exception! ' + str(e))
            return False
        else:  # 예외가 발생하지 않은 경우
            print("예외 발생 X")
            index_number = int(index_number)
            self.driver.switch_to.window(self.driver.window_handles[index_number])

            return True

    # May 08, 2022 : by indigo : 셀레니움 클릭 이벤트 함수 추가
    def element_click(self, delay, locator_type, locator_name, index_num):
        """
        delay : wait할 시간(초)\n
        locator : 엘리멘트 locator ex) 태그 ID 중 'user_id'을 셀렉트 하고자 하는 경우 => (By.ID, 'user_id')으로 선언\n
        [locator_type]\n
        ID : 태그 ID로 검색
        NAME : 태그 name으로 검색
        CLASS : 태그 클래스로 검색
        CSS: 태그 css 속성으로 검색
        TEXT: partial link text로 검색
        locator_name : 엘리멘트 이름
        index_num : 선택하고자 하는 엘리먼트의 인덱스 번호
        """
        try:
            locator = ''
            if locator_type == 'ID' or locator_type.upper() == 'ID':
                locator = (By.ID, locator_name)
            if locator_type == 'NAME' or locator_type.upper() == 'NAME':
                locator = (By.NAME, locator_name)
            if locator_type == 'CLASS' or locator_type.upper() == 'CLASS':
                locator = (By.CLASS_NAME, locator_name)
            if locator_type == 'CSS' or locator_type.upper() == 'CSS':
                locator = (By.CSS_SELECTOR, locator_name)
            if locator_type == 'TEXT' or locator_type.upper() == 'TEXT':
                locator = (By.PARTIAL_LINK_TEXT, locator_name)
            if index_num == '':
                WebDriverWait(self.driver, delay).until(
                    EC.presence_of_element_located(locator)
                )  # 페이지에 있는 모든 element(locator로 지정한)를 delay(초)동안 찾습니다.
            else:
                WebDriverWait(self.driver, delay).until(
                    EC.presence_of_all_elements_located(locator)
                )  # 페이지에 있는 모든 element(locator로 지정한)를 delay(초)동안 찾습니다.
        except TimeoutError as e:  # delay(초)를 초과한 경우
            print('TimeoutError! ' + str(e))
            return False
        except NoSuchElementException as e:  # 해당 엘리먼트가 존재 하지 않는 경우
            print('NoSuchElementException! ' + str(e))
            return False
        except Exception as e:  # 기타 예외
            print('Exception! ' + str(e))
            return False

        else:  # 예외가 발생하지 않은 경우
            if locator_type == 'ID' or locator_type.upper() == 'ID':
                locator_type = By.ID
            if locator_type == 'NAME' or locator_type.upper() == 'NAME':
                locator_type = By.NAME
            if locator_type == 'CLASS' or locator_type.upper() == 'CLASS':
                locator_type = By.CLASS_NAME
            if locator_type == 'CSS' or locator_type.upper() == 'CSS':
                locator_type = By.CSS_SELECTOR
            if locator_type == 'TEXT' or locator_type.upper() == 'TEXT':
                locator_type = By.PARTIAL_LINK_TEXT
            try:
                if index_num != '':  # index_num가 공백이 아니고, 숫자인 경우
                    # if index_num != '' and index_num.isdigit() == True:  # index_num가 공백이 아니고, 숫자인 경우
                    element = self.driver.find_elements(locator_type, locator_name)
                    element[index_num].click()  # 해당 인덱스에 해당하는 엘리먼트를 클릭합니다.
                elif index_num == '':  # index_num이 공백이면
                    element = self.driver.find_element(locator_type, locator_name)
                    element.click()  # 가장 첫번째 엘리먼트를 클릭합니다.

                return True
            except IndexError as e:
                print('IndexError! ' + str(e))

    # May 08, 2022 : by indigo : 셀레니움 텍스트 입력 이벤트 함수 추가
    def element_input_text(self, delay, locator_type, locator_name, text):
        """
        delay : wait할 시간(초)\n
        locator : 엘리멘트 locator ex) 태그 ID 중 'user_id'을 셀렉트 하고자 하는 경우 => (By.ID, 'user_id')으로 선언\n
        [locator_type]\n
        ID : 태그 ID로 검색
        NAME : 태그 name으로 검색
        CLASS : 태그 클래스로 검색
        CSS: 태그 css 속성으로 검색
        TEXT: partial link text로 검색
        locator_name : 엘리멘트 이름
        """
        try:
            # self.driver.get("https://www.eum.go.kr/web/mb/mbLogin.jsp")
            locator = ''
            text = str(text)
            if locator_type == 'ID' or locator_type.upper() == 'ID':
                locator = (By.ID, locator_name)
            if locator_type == 'NAME' or locator_type.upper() == 'NAME':
                locator = (By.NAME, locator_name)
            if locator_type == 'CLASS' or locator_type.upper() == 'CLASS':
                locator = (By.CLASS_NAME, locator_name)
            if locator_type == 'CSS' or locator_type.upper() == 'CSS':
                locator = (By.CSS_SELECTOR, locator_name)
            if locator_type == 'TEXT' or locator_type.upper() == 'TEXT':
                locator = (By.PARTIAL_LINK_TEXT, locator_name)
            WebDriverWait(self.driver, delay).until(
                EC.presence_of_all_elements_located(locator)
            )  # 페이지에 있는 모든 element(locator로 지정한)를 delay(초)동안 찾습니다.
        except TimeoutError as e:  # delay(초)를 초과한 경우
            print('TimeoutError! ' + locator_type + ', ' + str(e))
            return False
        except NoSuchElementException as e:  # 해당 엘리먼트가 존재 하지 않는 경우
            print('NoSuchElementException! ' + locator_type + ', ' + str(e))
            return False
        except Exception as e:  # 기타 예외
            print('Exception! ' + locator_type + ', ' + str(e))
            return False
        else:  # 예외가 발생하지 않은 경우
            print("예외 발생 X")
            if locator_type == 'ID' or locator_type.upper() == 'ID':
                locator_type = By.ID
            if locator_type == 'NAME' or locator_type.upper() == 'NAME':
                locator_type = By.NAME
            if locator_type == 'CLASS' or locator_type.upper() == 'CLASS':
                locator_type = By.CLASS_NAME
            if locator_type == 'CSS' or locator_type.upper() == 'CSS':
                locator_type = By.CSS_SELECTOR
            if locator_type == 'TEXT' or locator_type.upper() == 'TEXT':
                locator_type = By.PARTIAL_LINK_TEXT
            element = self.driver.find_element(locator_type, locator_name)
            element.send_keys(text)
            # sleep(3)

            return True

    # May 08, 2022 : by indigo : 셀레니움 텍스트 입력 이벤트 함수 추가
    def send_enter(self, delay, locator_type, locator_name):
        """
        delay : wait할 시간(초)\n
        locator : 엘리멘트 locator ex) 태그 ID 중 'user_id'을 셀렉트 하고자 하는 경우 => (By.ID, 'user_id')으로 선언\n
        [locator_type]\n
        ID : 태그 ID로 검색
        NAME : 태그 name으로 검색
        CLASS : 태그 클래스로 검색
        CSS: 태그 css 속성으로 검색
        TEXT: partial link text로 검색
        locator_name : 엘리멘트 이름
        """
        try:
            # self.driver.get("https://www.eum.go.kr/web/mb/mbLogin.jsp")
            locator = ''
            if locator_type == 'ID' or locator_type.upper() == 'ID':
                locator = (By.ID, locator_name)
            if locator_type == 'NAME' or locator_type.upper() == 'NAME':
                locator = (By.NAME, locator_name)
            if locator_type == 'CLASS' or locator_type.upper() == 'CLASS':
                locator = (By.CLASS_NAME, locator_name)
            if locator_type == 'CSS' or locator_type.upper() == 'CSS':
                locator = (By.CSS_SELECTOR, locator_name)
            if locator_type == 'TEXT' or locator_type.upper() == 'TEXT':
                locator = (By.PARTIAL_LINK_TEXT, locator_name)
            WebDriverWait(self.driver, delay).until(
                EC.presence_of_all_elements_located(locator)
            )  # 페이지에 있는 모든 element(locator로 지정한)를 delay(초)동안 찾습니다.
        except TimeoutError as e:  # delay(초)를 초과한 경우
            print('TimeoutError! ' + locator_type + ', ' + str(e))
            return False
        except NoSuchElementException as e:  # 해당 엘리먼트가 존재 하지 않는 경우
            print('NoSuchElementException! ' + locator_type + ', ' + str(e))
            return False
        except Exception as e:  # 기타 예외
            print('Exception! ' + locator_type + ', ' + str(e))
            return False
        else:  # 예외가 발생하지 않은 경우
            print("예외 발생 X")
            if locator_type == 'ID' or locator_type.upper() == 'ID':
                locator_type = By.ID
            if locator_type == 'NAME' or locator_type.upper() == 'NAME':
                locator_type = By.NAME
            if locator_type == 'CLASS' or locator_type.upper() == 'CLASS':
                locator_type = By.CLASS_NAME
            if locator_type == 'CSS' or locator_type.upper() == 'CSS':
                locator_type = By.CSS_SELECTOR
            if locator_type == 'TEXT' or locator_type.upper() == 'TEXT':
                locator_type = By.PARTIAL_LINK_TEXT
            element = self.driver.find_element(locator_type, locator_name)
            element.send_keys(Keys.RETURN)
            # sleep(3)

            return True
       
    def close(self):
        self.driver.quit()
