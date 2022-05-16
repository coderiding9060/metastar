# from asyncio import wait_for
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
from fake_useragent import UserAgent
from time import sleep
import logging

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
file_handler = logging.FileHandler('gov.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# log 사용
# createLog()
# createLog.logger.info(1)

class CadastralDownloadPDF():

    def __init__(self, userId, passWd, option):
        self.option = option
        self.option.headless = False  # 창이 없음
        # ua = UserAgent()
        # userAgent = ua.random
        # self.option.add_argument("--headless")
        # self.option.add_argument(f'user-agent={userAgent}')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.option)
        self.userId = userId
        self.pwd = passWd

    def wait_for(self, locator):
        return WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(locator)
        )

    def printing(self):
        delay = 10
        # current_handles = self.driver.window_handles
        # 인쇄
        WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(2))
        self.driver.switch_to.window(self.driver.window_handles[1])
        # self.change_window(delay, current_handles, 1)
        # sleep(3)
        # 인쇄 클릭
        # sleep(1)  # 대기시간 조정이 안되서, sleep처리
        # btnPrint = self.driver.find_element_by_id('btnPrint')
        # btnPrint.click()

        # delay = 10
        # locator_type = 'CLASS'
        # locator_name = 'print'

        locator_type = 'ID'
        locator_name = 'btnPrint'

        # locator_type = 'XPATH'
        # locator_name = '//*[@id="btnPrint"]'
        self.element_click(delay, locator_type, locator_name, '')

        # self.driver.execute_script(
        #     """
        #     if(document.readyState === "complete") {
        #         viewer.focus();
        #         viewer.yex.api.print();
        #     }
        #     """
        # )
        sleep(3)  # 10 -> 3
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.close()

    def login(self):
        self.driver.get('https://www.gov.kr/nlogin/?regType=ctab')
        login = self.driver.find_element_by_id('아이디')
        login.click()
        self.driver.find_element_by_id('userId').send_keys(self.userId)
        self.driver.find_element_by_id('pwd').send_keys(self.pwd)
        self.driver.find_element_by_id('pwd').send_keys(Keys.RETURN)

    # 토지대장
    def cadastral(self, cadastral_address, lidong_number_address, address_bun, address_ho):
        print(cadastral_address)
        print(lidong_number_address)
        print(address_bun)
        print(address_ho)

        # 페이지 이동
        self.driver.get(
            'https://www.gov.kr/mw/AA020InfoCappView.do?CappBizCD=13100000026&HighCtgCD=A02001001&Mcode=10207')

        # 발급
        delay = 10
        locator_type = 'CSS'
        locator_name = '#applyBtn a'
        # issued = self.driver.find_element_by_css_selector('#applyBtn a')
        # issued.click()
        self.element_click(delay, locator_type, locator_name, '')

        # 검색
        # btnAddress = self.wait_for((By.ID, 'btnAddress'))
        # btnAddress.click()

        # 검색
        delay = 10
        locator_type = 'ID'
        locator_name = 'btnAddress'
        current_handles = self.driver.window_handles
        self.element_click(delay, locator_type, locator_name, '')

        # self.driver.switch_to.window(self.driver.window_handles[1])
        self.change_window(delay, current_handles, 1)

        ### 대상토지 소재지
        # 지번주소 검색
        # self.driver.find_element_by_id('txtAddr').send_keys(cadastral_address)
        # search_btn = self.driver.find_element_by_css_selector('.ibtn button')
        # search_btn.click()
        locator_type = 'ID'
        locator_name = 'txtAddr'
        self.element_input_text(delay, locator_type, locator_name, cadastral_address)
        self.send_enter(delay, locator_type, locator_name)

        # 행정처리기관 선택
        try:
            land = self.wait_for((By.PARTIAL_LINK_TEXT, lidong_number_address))
        except:
            land = self.wait_for((By.CSS_SELECTOR, '.land a:nth-child(2)'))
        finally:
            land.click()
        self.driver.switch_to.window(self.driver.window_handles[0])

        # 번지&호 입력
        # self.driver.find_element_by_id('토지임야대장신청서_IN-토지임야대장신청서_신청토지소재지_주소정보_상세주소_번지').send_keys(address_bun)
        # self.driver.find_element_by_id('토지임야대장신청서_IN-토지임야대장신청서_신청토지소재지_주소정보_상세주소_호').send_keys(address_ho)

        # 번지&호 입력
        locator_type = 'ID'
        locator_name = '토지임야대장신청서_IN-토지임야대장신청서_신청토지소재지_주소정보_상세주소_번지'
        self.element_input_text(delay, locator_type, locator_name, address_bun)
        locator_name = '토지임야대장신청서_IN-토지임야대장신청서_신청토지소재지_주소정보_상세주소_호'
        self.element_input_text(delay, locator_type, locator_name, address_ho)

        # 민원신청하기
        # btn_end = self.driver.find_element_by_id('btn_end')
        # btn_end.click()

        # 민원신청하기
        locator_type = 'ID'
        locator_name = 'btn_end'
        self.element_click(delay, locator_type, locator_name, '')

        # 문서출력
        try:
            # May 06, 2022 : by indigo : 정상 조회 시
            # 주소 정상 조회 성공시
            ibtn_a = self.wait_for(
                (By.CSS_SELECTOR, 'tbody tr .cs-state .ibtn a'))  # May 06, 2022 : by indigo : wait_for 시간이 길어서 임시 주석 처리
            ibtn_a = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody tr .cs-state .ibtn a')))
            ibtn_a.click()

            # locator_type = 'CLASS'
            # locator_name = '.ibtn'
            # self.element_click(delay, locator_type, locator_name, '')
            # 주소 정상 조회 실패시(요청하신 페이지를 찾을 수 없습니다)

            # error_messages = self.wait_for((By.CLASS_NAME, 'desc'))
            error_messages = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'desc')))

            is_error = False
            # error_message = self.driver.find_elements((By.CLASSNAME, 'desc'))

            for error_message in error_messages:
                if '주소가 잘못' in error_message:
                    is_error = True
                    break
                elif '찾을 수 없' in error_message:
                    is_error = True
                    break

            if is_error == True:
                print("에러 발생")

        except TimeoutError as te:
            print("해당 문서 출력 버튼이 존재 하지 않습니다.")
            print(te)

        except Exception as e:
            print("예외 발생")
            print(e)

        # 인쇄
        self.printing()

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
