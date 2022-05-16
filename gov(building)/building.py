# from asyncio import wait_for
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
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

class BuildingDownloadPDF():

    def __init__(self, userId, passWd, option):
        self.option = option
        self.option.headless = False  # 창이 없음
        self.option.user = "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.option)
        self.driver.implicitly_wait(10)  # May 05, 2022 : by indigo : 페이지 로딩 완료 시간 설정 [기본값 : 0], 해당 설정을 하면 해당 driver를 사용하는 모든 코드에 적용됨
        self.userId = userId
        self.pwd = passWd

    def wait_for(self, locator):
        return WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(locator)
        )

    def printing(self):
        try:
        # 인쇄
            delay = 10
            WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(2))
            # current_handles = self.driver.window_handles
            # self.change_window(delay, current_handles, 1)
            
            self.driver.switch_to.window(self.driver.window_handles[1])
            sleep(3) # 대기시간 조정이 안되서, sleep처리
            
            # btnPrint = self.driver.find_element_by_id('btnPrint')
            # WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, 'btnPrint')))
            
            # 인쇄 클릭
            locator_type = 'ID'
            locator_name = 'btnPrint'
            self.element_click(delay, locator_type, locator_name, '')
            sleep(5) # 10 -> 5 # 건들지 말 것 (제주시 영평동 2181)
            
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.close()
            
        except Exception as e:
            print(e)
    
    # May 05, 2022 : by indigo : popupClose 함수 추가[민원 신청 버튼 클릭 후 새 탭에 똑같은 페이지 뜨는것 방지]
    def popupClose(self):
        try:
            main = self.driver.window_handles  # 현재 떠있는 창 목록
            for handle in main:
                if handle != main[0]:  # 현재 떠있는 창 목록의 0번째[메인 페이지]와 handle이 다른 경우
                    self.driver.switch_to.window(handle)  # 팝업창으로 전환 후
                    self.driver.close()  # 팝업창 닫기
                    # 원래 브라우저로 돌아가기
                    self.driver.switch_to.window(main[0])
        except:
            print("팝업창 끄기 실패")

    def login(self):
        self.driver.get('https://www.gov.kr/nlogin/?regType=ctab')
        # self.driver.get('https://www.gov.kr/nlogin/?Mcode=10003')
        login = self.driver.find_element_by_id('아이디')
        login.click()
        # self.driver.find_element_by_id('userId').send_keys(self.userId)
        # self.driver.find_element_by_id('pwd').send_keys(self.pwd)
        # self.driver.find_element_by_id('pwd').send_keys(Keys.RETURN)
        print(self.userId)
        self.driver.execute_script(
            """
            if(document.readyState === "complete") {
                document.querySelector('#userId').setAttribute('value', '""" + self.userId + """')
                document.querySelector('#pwd').setAttribute('value', '""" + self.pwd + """')
            }
            """
        )

        self.driver.execute_script(
            """
            if(document.readyState === "complete") {
                document.querySelector('#genLogin').click()
            }
            """
        )

    # 건축물대장
    def building(self, category_type, address, direct_ho, direct_dong, building_road):

        print(category_type)
        print(address)
        print(direct_ho)
        print(direct_dong)
        print(building_road)
        # 페이지 이동
        self.driver.get(
            'https://www.gov.kr/mw/AA020InfoCappView.do?CappBizCD=15000000098&HighCtgCD=A02004002&Mcode=10205')
        
        # 발급
        delay = 10
        locator_type = 'CSS'
        locator_name = '#applyBtn a'
        # issued = self.driver.find_element_by_css_selector('#applyBtn a')
        # issued.click()
        self.element_click(delay, locator_type, locator_name, '')

        try:
            # 건축물소재지 - 검색
            # address_name = self.wait_for((By.ID, '주소검색'))
            # address_name.click()
            locator_type = 'ID'
            locator_name = '주소검색'
            current_handles = self.driver.window_handles
            self.element_click(delay, locator_type, locator_name, '')
            
            # 주소검색
            # self.driver.switch_to.window(self.driver.window_handles[1])
            self.change_window(delay, current_handles, 1)
            
            # self.driver.find_element_by_id('txtRoad').send_keys(building_road)
            # self.driver.find_element_by_id('txtRoad').send_keys(Keys.ENTER)
            locator_type = 'ID'
            locator_name = 'txtRoad'
            self.element_input_text(delay, locator_type, locator_name, building_road)
            self.send_enter(delay, locator_type, locator_name)

            # 검색한 주소 - 첫번째 자식
            # result = self.wait_for((By.CSS_SELECTOR, '.address-result-list a:first-child'))
            locator_type = 'TEXT'
            locator_name = building_road
            if category_type == '집합건물':
                # result = self.driver.find_element_by_partial_link_text(building_road + '(')
                self.element_click(delay, locator_type, locator_name + '(', '')
            else:
                # result = self.driver.find_element_by_partial_link_text(building_road)
                self.element_click(delay, locator_type, locator_name, '')
            # result.click()

            # 행정처리기관 선택
            locator_type = 'CSS'
            locator_name = '.land a:nth-child(2)'
            # land = self.wait_for((By.CSS_SELECTOR, '.land a:nth-child(2)'))
            # land.click()
            self.element_click(delay, locator_type, locator_name, '')
            self.driver.switch_to.window(self.driver.window_handles[0])

            # 대장구분
            if category_type == '집합건물':
                # 집합(아파트,연립주택 등)
                locator_type = 'ID'
                locator_name = '건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장구분_.라디오코드2'
                # category_btn = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장구분_.라디오코드2')
                # category_btn.click()
                self.element_click(delay, locator_type, locator_name, '')
                # 전유부
                locator_name = '건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드13'
                # type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드13')
                # type.click()
                self.element_click(delay, locator_type, locator_name, '')
            else:
                # 일반(단독주택)
                locator_type = 'ID'
                locator_name = '건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장구분_.라디오코드1'
                # category_btn = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장구분_.라디오코드1')
                # category_btn.click()
                self.element_click(delay, locator_type, locator_name, '')
                # 일반
                locator_name = '건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드02'
                # type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드02')
                # type.click()
                self.element_click(delay, locator_type, locator_name, '')

            # 대장종류
            if False:
                # 일반/총괄
                type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드01')
                # 일반/일반
                type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드02')
                # 집합/총괄
                type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드11')
                # 집합/표제부
                type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드12')
                # 집합/전유부
                type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드13')

            # 건물(동)명칭 - 검색
            locator_type = 'ID'
            locator_name = '동명검색'
            # address_dong = self.driver.find_element_by_id('동명검색')
            # address_dong.click()
            self.element_click(delay, locator_type, locator_name, '')

            # 주소검색 - 선택
            print("---------------------1")

            # WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(2))
            # # sleep(1)
            # self.driver.switch_to.window(self.driver.window_handles[1])
            delay = 15
            self.change_window(delay, current_handles, 1)
            
            print("---------------------2")
            
            if category_type == '집합건물' and direct_dong != '동명칭없음':
                delay = 10
                locator_type = 'TEXT'
                locator_name = direct_dong
                # ibtn = self.driver.find_element_by_partial_link_text(direct_dong)
                self.element_click(delay, locator_type, locator_name, '')
            else:
                delay = 10
                locator_type = 'CSS'
                locator_name = '.ibtn button'
                # ibtn = self.driver.find_element_by_css_selector('.ibtn button')
                self.element_click(delay, locator_type, locator_name, '')
            # sleep(2)
            print("---------------------3")
            # ibtn.click()
            self.driver.switch_to.window(self.driver.window_handles[0])

            # sleep(1)

            ho_name = ''
            print("---------------------4")
            if category_type == '집합건물':
                # 호명칭 - 검색
                # sleep(3)
                locator_type = 'ID'
                locator_name = '호명검색'
                self.element_click(delay, locator_type, locator_name, '')

                # May 05, 2022 : by indigo : headless-chrome에서 한글깨짐 문제때문에 버튼 인식못하는 부분 js로 대체[테스트중]
                # self.driver.execute_script(
                #     """
                #         if(document.readyState === "complete") {
                #             var button = document.querySelector('#호명검색')
                #             if(button != null) {
                #                button.click()
                #             }
                #         }
                #     """
                # )
                # 주소검색 - 선택
                # WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(2))
                # self.driver.switch_to.window(self.driver.window_handles[1])
                self.change_window(delay, current_handles, 1)
                
                locator_type = 'TEXT'
                locator_name  = direct_ho
                # ibtn = self.wait_for((By.PARTIAL_LINK_TEXT, direct_ho))
                # ibtn.click()
                self.element_click(delay, locator_type, locator_name, '')
                
                self.driver.switch_to.window(self.driver.window_handles[0])

        except:
            delay = 10
            # 닫기버튼
            try:
                locator_type = 'TEXT'
                locator_name = '닫기'
                # close_btn = self.driver.find_element_by_partial_link_text(('닫기'))
                # close_btn.click()
                self.element_click(delay, locator_type, locator_name, '')
            except:
                category_type = '집합건물'
                address = building_road

            self.driver.switch_to.window(self.driver.window_handles[0])

            # 건축물소재지 - 검색
            # address_name = self.wait_for((By.ID, '주소검색'))
            # address_name.click()
            locator_type = 'ID'
            locator_name = '주소검색'
            current_handles = self.driver.window_handles
            self.element_click(delay, locator_type, locator_name, '')

            # 주소검색
            # self.driver.switch_to.window(self.driver.window_handles[1])
            self.change_window(delay, current_handles, 1)
            # self.driver.find_element_by_id('txtRoad').send_keys(address)
            # self.driver.find_element_by_id('txtRoad').send_keys(Keys.ENTER)
            locator_type = 'ID'
            locator_name = 'txtRoad'
            self.element_input_text(delay, locator_type, locator_name, building_road)
            self.send_enter(delay, locator_type, locator_name)

            # 검색한 주소 - 첫번째 자식
            # result = self.wait_for((By.CSS_SELECTOR, '.address-result-list a:first-child'))
            try:
                locator_type = 'TEXT'
                locator_name = building_road
                if category_type == '집합건물':
                    # result = self.driver.find_element_by_partial_link_text(building_road + '(')
                    self.element_click(delay, locator_type, locator_name + '(', '')
                else:
                    # result = self.driver.find_element_by_partial_link_text(building_road)
                    self.element_click(delay, locator_type, locator_name, '')
            except:
                locator_type = 'CSS'
                locator_name = '.address-result-list a:first-child'
                # result = self.wait_for((By.CSS_SELECTOR, '.address-result-list a:first-child'))
                self.element_click(delay, locator_type, locator_name, '')
            # result.click()

            # 행정처리기관 선택
            locator_type = 'CSS'
            locator_name = '.land a:nth-child(2)'
            # land = self.wait_for((By.CSS_SELECTOR, '.land a:nth-child(2)'))
            # land.click()
            self.element_click(delay, locator_type, locator_name, '')
            self.driver.switch_to.window(self.driver.window_handles[0])

            # 대장구분
            if category_type == '집합건물':
                # 집합(아파트,연립주택 등)
                locator_type = 'ID'
                locator_name = '건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장구분_.라디오코드2'
                # category_btn = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장구분_.라디오코드2')
                # category_btn.click()
                self.element_click(delay, locator_type, locator_name, '')
                # 전유부
                locator_name = '건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드13'
                # type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드13')
                # type.click()
                self.element_click(delay, locator_type, locator_name, '')
            else:
                # 일반(단독주택)
                locator_type = 'ID'
                locator_name = '건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장구분_.라디오코드1'
                # category_btn = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장구분_.라디오코드1')
                # category_btn.click()
                self.element_click(delay, locator_type, locator_name, '')
                # 일반
                locator_name = '건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드02'
                # type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드02')
                # type.click()
                self.element_click(delay, locator_type, locator_name, '')

            # 대장종류
            if False:
                # 일반/총괄
                type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드01')
                # 일반/일반
                type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드02')
                # 집합/총괄
                type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드11')
                # 집합/표제부
                type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드12')
                # 집합/전유부
                type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드13')

            # 건물(동)명칭 - 검색
            locator_type = 'ID'
            locator_name = '동명검색'
            # address_dong = self.driver.find_element_by_id('동명검색')
            # address_dong.click()
            self.element_click(delay, locator_type, locator_name, '')

            # 주소검색 - 선택
            print("---------------------1")
            
            # WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(2))
            # # sleep(1)
            # self.driver.switch_to.window(self.driver.window_handles[1])
            delay = 15
            self.change_window(delay, current_handles, 1)
            
            print("---------------------2")

            if category_type == '집합건물' and direct_dong != '동명칭없음':
                try:
                    delay = 10
                    locator_type = 'TEXT'
                    locator_name = direct_dong
                    # ibtn = self.driver.find_element_by_partial_link_text(direct_dong)
                    self.element_click(delay, locator_type, locator_name, '')
                except:
                    delay = 10
                    locator_type = 'CSS'
                    locator_name = '.ibtn button'
                    # ibtn = self.driver.find_element_by_css_selector('.ibtn button')
                    self.element_click(delay, locator_type, locator_name, '')
            else:
                delay = 10
                locator_type = 'CSS'
                locator_name = '.ibtn button'
                # ibtn = self.driver.find_element_by_css_selector('.ibtn button')
                self.element_click(delay, locator_type, locator_name, '')
            # sleep(2)
            print("---------------------3")
            # ibtn.click()
            self.driver.switch_to.window(self.driver.window_handles[0])

            # sleep(1)

            ho_name = ''
            print("---------------------4")
            if category_type == '집합건물':
                # 호명칭 - 검색
                # sleep(3)
                locator_type = 'ID'
                locator_name = '호명검색'
                self.element_click(delay, locator_type, locator_name, '')

                # May 05, 2022 : by indigo : headless-chrome에서 한글깨짐 문제때문에 버튼 인식못하는 부분 js로 대체[테스트중]
                # self.driver.execute_script(
                #     """
                #         if(document.readyState === "complete") {
                #             var button = document.querySelector('#호명검색')
                #             if(button != null) {
                #                button.click()
                #             }
                #         }
                #     """
                # )
                # 주소검색 - 선택
                # WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(2))
                # self.driver.switch_to.window(self.driver.window_handles[1])
                self.change_window(delay, current_handles, 1)
                
                locator_type = 'TEXT'
                locator_name  = direct_ho
                # ibtn = self.wait_for((By.PARTIAL_LINK_TEXT, direct_ho))
                # ibtn.click()
                self.element_click(delay, locator_type, locator_name, '')
                
                self.driver.switch_to.window(self.driver.window_handles[0])
        # sleep(3)
        # 민원신청하기
        delay = 10
        locator_type = 'ID'
        locator_name = 'btn_end'
        # btn_end = self.driver.find_element_by_id('btn_end')
        # btn_end.click()
        self.element_click(delay, locator_type, locator_name, '')
        print("---------------------5")
        
        # sleep(5)
  
        # 문서출력
        # locator_type = 'CSS'
        # locator_name = 'tbody tr .cs-state .ibtn a'
        ibtn_a = self.wait_for((By.CSS_SELECTOR, 'tbody tr .cs-state .ibtn a'))
        sleep(1)
        while len(self.driver.window_handles)>1:
            self.popupClose
        ibtn_a.click()
        # self.element_click(delay, locator_type, locator_name, '')
        # sleep(3)
        
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
