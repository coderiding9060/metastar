from ahk.window import Window
from ahk.daemon import AHKDaemon
from ahk import AHK
from waiting import wait, TimeoutExpired
import subprocess
import webbrowser

from selenium import webdriver
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import logging
# import json
import os

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
file_handler = logging.FileHandler('iros.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class IssueDownloadPDF():

    def __init__(self, userId, passWd, option):
        self.option = option
        self.option.headless = False  # 창이 없음
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.option)
        self.driver.implicitly_wait(10)  # May 06, 2022 : by indigo : 페이지 로딩 완료 시간 설정 [기본값 : 0], 해당 설정을 하면 해당 driver를 사용하는 모든 코드에 적용됨
        self.userId = userId
        self.pwd = passWd

    def wait_for(self, locator):
        return WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(locator)
        )

    def anySignWaitting(self):
        self.wait_for((By.ID, 'AnySign4PCLoad'))
        WebDriverWait(self.driver, 30).until(
            EC.invisibility_of_element_located((By.ID, 'AnySign4PCLoadingImg'))
        )

    # Apr 27, 2022 : by indigo : popupClose 함수 수정
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
        # # 팝업창 있다면 연결해서
        # self.driver.switch_to.window(self.driver.window_handles[1])
        # # 끄기
        # self.driver.close()

        # self.driver.switch_to.window(self.driver.window_handles[0])

    def login(self):
        self.driver.get('http://www.iros.go.kr/PMainJ.jsp')
        # AngSign 로드 대기
        self.anySignWaitting()
        # self.driver.find_element_by_id('id_user_id').send_keys(self.userId)
        # self.driver.find_element_by_id('password').send_keys(self.pwd)
        self.driver.execute_script(
            """
            document.querySelector('#id_user_id').setAttribute('value', '""" + self.userId + """')
            document.querySelector('#password').setAttribute('value', '""" + self.pwd + """')
            """
        )
        self.driver.execute_script(
            """
            f_gosubmit()
            """
        )
        # self.driver.find_element_by_id('password').send_keys(Keys.RETURN)
        sleep(1)
        # self.anySignWaitting()

    ### 발급하기
    def realEstate(self, real_estate_unique, payment, iros_type):

        # Apr 27, 2022 : by indigo : 오토핫키 실행 코드 위치 변경[S]
        # Autohotkey Daemon 실행
        ### Start AutoHotKey Daemon
        ahk = AHKDaemon(executable_path='bin/AutoHotkeyU64.exe')
        ahk.start()

        ### AHK Support Function
        def getWinStrBegin(str, charset='cp949'):
            try:
                return list(filter(lambda win: win.title.startswith(str.encode(charset)), ahk.windows()))[0]
            except:
                return False

        # Apr 19, 2022 : by indigo : 파이썬이 관리자 권한으로 실행하는지 확인하는 코드 추가
        # 오토핫키가 관리자 권한으로 실행되지 않으면 인쇄창에서 아무런 동작이 되지 않음
        # 파이썬을 관리자권한으로 실행시켜야 shell 스크립트에서 taskkill[프로세스 강제 종료]명령어 사용시 정상 적용되므로 확인 필요
        from win32com.shell import shell
        if shell.IsUserAnAdmin():
            print("관리자 권한 O")
        else:
            print("관리자 권한 X")
        # Apr 27, 2022 : by indigo : 오토핫키 실행 코드 위치 변경[E]

        self.real_estate_unique = real_estate_unique
        self.payment = payment
        self.iros_type = iros_type
        print(self.real_estate_unique)

        # 발급하기 - 고유번호로 찾기
        self.popupClose()
        self.driver.get('http://www.iros.go.kr/frontservlet?cmd=RISUWelcomeIsuC')
        sleep(1)

        # alert
        try:
            WebDriverWait(self.driver, 1).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
        except:
            print("no alert")

        # self.anySignWaitting()

        # iframe 내부
        self.driver.switch_to.frame('inputFrame')
        sleep(1)    # 없애지 말기
        # 고유번호로 찾기
        tab2 = self.driver.find_element_by_id('tab2')
        tab2.click()
        # sleep(1)
        self.driver.switch_to.default_content()
        # sleep(1)
        self.driver.switch_to.frame('resultFrame')
        # sleep(1)
        self.driver.switch_to.frame('frmOuterModal')
        # 부동산 고유번호
        self.driver.find_element_by_id('inpPinNo').send_keys(self.real_estate_unique)
        # 검색
        self.driver.find_element_by_id('inpPinNo').send_keys(Keys.RETURN)

        # 집합건물의 전유세대 부동산 소재지번 선택 - 선택

        sleep(1)
        # Apr 21, 2022 : by indigo : 해당주소로 이미 열람/발급 내역이 있는 경우 버튼 구성이 달라져서 '다음'이 아닌 '확인'버튼을 누르도록 코드 수정
        self.driver.execute_script(
            """
            if(document.readyState === "complete") {
                var confirm = document.querySelector('.btn_bg02_action')
                var next = document.querySelector('.btn1_n_bg02_action')
                if(confirm!==null){
                    confirm.click()
                } else {
                    next.click()
                }
            }
            """
        )
        # jsText = "document.querySelector('nav').querySelector('div .is-navigation__main').querySelector('div .is-navigation__main__right').querySelector('span').click()"
        # self.driver.execute_script(jsText)
        sleep(1)
        # 등기기록 유형을 선택하세요. - 다음
        self.driver.execute_script(
            """
            if(document.readyState === "complete") {
                var next = document.querySelector('.btn_bg02_action')
                next.click()
            }
            """
        )

        sleep(1)
        # (주민)등록번호 공개여부 검증
        # Apr 21, 2022 : by indigo : f_continue 함수 실행시 에러가 발생하는 경우가 있어서 버튼 클릭방식으로 코드 수정
        self.driver.execute_script(
            """
            if(document.readyState === "complete") {
                var button = document.querySelector('.btn_bg02_action')
                button.click()
            }
            """
        )

        sleep(1)
        self.driver.execute_script(
            """
                if(document.readyState === "complete") {
                    var button = document.querySelector('.btn_bg02_action')
                    if(button != null) {
                        var button_name = button.innerHTML;
                        if(button_name.includes('다음')) {
                            button.click()
                        }
                    }
                }
            """
        )

        # self.anySignWaitting()
        sleep(1)
        self.driver.switch_to.default_content()
        sleep(1)
        self.driver.switch_to.frame('resultFrame')
        sleep(1)    # 없애지 말기
        # 결제대상 부동산
        self.driver.execute_script(
            """
            if(document.readyState === "complete") {
                var next = document.querySelector('.btn1_up_bg02_action')
                next.click()
            }      
            """
        )
        sleep(4)
        try:
            self.driver.switch_to.window(self.driver.window_handles[1])
            print("=-=-=-=-=-=-=-=-= 0.3성공 =-=-=-=-=-=-=-=-=")
            sleep(1)
            self.driver.execute_script(
                """
                console.log("=========in javascript=========")
                if (document.readyState === "complete") {
                    var next = document.querySelector('.btn_bg02_action')
                    next.click()
                }
                """
            )
            print("=-=-=-=-=-=-=-=-= 0.6성공 =-=-=-=-=-=-=-=-=")
        except:
            print("no alert")

        sleep(1)
        # 선불전자지급수단
        self.anySignWaitting()
        pay = self.driver.find_element_by_id('inpMtdCls3')
        pay.click()
        sleep(0.5)
        # 선불전자지급수단번호 및 비밀번호
        self.driver.execute_script(
            """
            if (document.readyState === "complete") {
                document.querySelector('#inpEMoneyNo1').setAttribute('value', '""" + self.payment[0] + """')
                document.querySelector('#inpEMoneyNo2').setAttribute('value', '""" + self.payment[1] + """')
                document.querySelector('#inpEMoneyPswd').setAttribute('value', '""" + self.payment[2] + """')
            }
            """
        )
        sleep(0.5)
        # 위 내용에 동의합니다.
        # check = self.driver.find_element_by_id('id_check2')
        # check.click()
        # 전체 동의
        term = self.driver.find_element_by_id('chk_term_agree_all_emoney')
        term.click()
        # 결제
        inpComplete = self.driver.find_element_by_name('inpComplete')
        sleep(1)
        inpComplete.click()
        print("=-=-=-=-=-=-=-=-= 결제 성공 =-=-=-=-=-=-=-=-=")
        # 결제 - 확인
        alert = self.driver.switch_to.alert
        alert.accept()
        sleep(3)
        print("=-=-=-=-=-=-=-=-= 결제확인 성공 =-=-=-=-=-=-=-=-=")
        # 결제성공 확인
        self.driver.switch_to.window(self.driver.window_handles[1])
        sleep(1)
        print("=-=-=-=-=-=-=-=-= 결제성공확인 성공 =-=-=-=-=-=-=-=-=")
        # Apr 21, 2022 : by indigo : 해당주소로 이미 열람/발급 내역이 있는 경우 버튼 구성이 다른 팝업창이 뜨는 문제를 해결하는 코드 추가
        self.driver.execute_script(
            """
            if(document.readyState === "complete") {
                var force_payment = document.querySelector('.btn_bg04_action')
                var next = document.querySelector('.btn_bg02_action')
                if(force_payment!==null){
                    force_payment.click()
                } else {
                    next.click()
                }
            }
            """
        )
        print("=-=-=-=-=-=-=-=-= 1성공 =-=-=-=-=-=-=-=-=")
        sleep(3)

        try:
            WebDriverWait(self.driver, 1).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
            sleep(3)
            print("=-=-=-=-=-=-=-=-= 1.3성공 =-=-=-=-=-=-=-=-=")
            self.driver.switch_to.window(self.driver.window_handles[1])
            print("=-=-=-=-=-=-=-=-= 1.6성공 =-=-=-=-=-=-=-=-=")
            sleep(1)
            self.driver.execute_script(
                """
                console.log("=========in javascript=========")
                if (document.readyState === "complete") {
                    var next = document.querySelector('.btn_bg02_action')
                    next.click()
                }
                """
            )

        except:
            print("no alert")

        # sleep(3)
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.anySignWaitting()
        print("=-=-=-=-=-=-=-=-= 2성공 =-=-=-=-=-=-=-=-=")
        # 열람
        # element = self.driver.find_elements_by_class_name('btn1_n_bg02_action')
        element = self.driver.find_elements(By.CLASS_NAME,'btn1_n_bg02_action')
        element[1].click()
        # self.driver.execute_script(
        #     """
        #     if(document.readyState === "complete") {
        #         var button = document.querySelectorAll(".btn1_n_bg02_action");
        #         var button_name = button[1].innerHTML;
        #
        #         if(button_name=='열람'||button_name=='발급'){
        #             button[1].click();
        #         }
        #     }
        #     """
        # )
        print("=-=-=-=-=-=-=-=-= 3성공 =-=-=-=-=-=-=-=-=")
        sleep(3)
        
        print("\n\n====== IROS Macro PoC ======")
        print(
            '1. Loading IROS Main Page and waiting for #Lwrap div to appear...\n   (for Cookies&Auth, can be skipped on prod env. Timeout: 60s)\n   (on prod env, this part should be implemented with auth&input etc.)')
        
        try:
            ### Step 4 - AHK Based Mouse/Keyboard Macro
            print('4. Search & Wait for Printer Selection Dialog...\n   (by Window Title, Timeout: 600s)')
            matchWin = wait(lambda: getWinStrBegin('[대법원 등기 인터넷 서비스] - [인쇄]'), timeout_seconds=600)
            matchWin.activate()
            matchWin.move(x=10, y=10, width=486,
                            height=383)  # Apr 19, 2022 : by indigo : 창 위치를 10, 10위치로 옮겨서 다른 창이 인쇄창을 가리는 것을 방지하는 코드 추가 width, height는 원래 창 크기값 받아서 적용했으므로 사이즈 변동 없음.
            matchWin.to_top()
            matchWin.always_on_top = True
            matchWin.activate()
            matchWinRect = matchWin.rect

            print('4-1. Searching for Dropdown & Click...\n     (by search/1.dropdown.png, Timeout: 120s)')
            ahk.mouse_move(x=20, y=20, speed=10,
                            relative=True)  # Apr 19, 2022 : by indigo : 마우스 커서 위치를 20, 20위치로 이동시킵니다.[정말 희박한 확률이지만 찾고자하는 이미지 위에 마우스커서가 존재하면 이미지를 못찾는 일이 발생하는것을 방지]
            dropdownButton = wait(lambda: ahk.image_search('search/1.dropdown.png'),
                                    timeout_seconds=120)  # 인쇄창의 프린터 선택 드랍다운 메뉴 화살표 버튼을 찾음.
            if dropdownButton:  # 드랍 다운 버튼 이미지를 찾은 경우
                # x, y좌표에 5씩 더하는 이유 : 이미지 서치 성공시 반환받는 좌표는 왼쪽 상단 꼭지점기준의 좌표이므로 이 부분을 클릭시 버튼 안쪽이 아닌 모퉁이 부분을 클릭함으로써 오동작 발생 가능성이 있기 때문
                ahk.mouse_position = (
                    matchWinRect[0] + dropdownButton[0] + 2,
                    matchWinRect[1] + dropdownButton[1] + 2)  # x, y좌표값에 2를 더함
                ahk.click()
                sleep(0.2)
                ahk.send_input('{Home}')
                sleep(0.2)
                ahk.send_input('{Enter}')
                sleep(0.2)
                print(
                    '4-2. Searching for Compatable Printer & Click...\n     (by search/2.printer.png, Interval: 1s)')
                while True:
                    matchPrinter = ahk.image_search('search/2.printer.png')
                    # Apr 18, 2022 : by indigo : 드랍다운 메뉴 삼성 프린터 이미지 추가
                    matchPrinter1 = ahk.image_search('search/2.printer1.png')

                    # Apr 19, 2022 : by indigo : 프린터 선택 시 조건 추가
                    if matchPrinter:  # 프린터 선택 상태[파란 배경]이 확인된 경우
                        print('   * Matching Printer found!')
                        break
                    elif matchPrinter1:  # 드랍다운 메뉴에서 프린터를 찾았을때
                        print('   * Matching Printer found!')
                        ahk.mouse_position = (
                            matchWinRect[0] + matchPrinter[0] + 5, matchWinRect[1] + matchPrinter[1] + 5)
                        sleep(0.2)
                        ahk.click()
                        sleep(0.2)
                        break

                    else:  # 둘다 해당 사항이 없는 경우 드랍 다운 항목을 한칸씩
                        ahk.send_input('{Down}')
                        if matchPrinter:  # 프린터 선택 상태[파란 배경]이 확인된 경우
                            print('   * Matching Printer found!')
                            ahk.mouse_position = (
                                matchWinRect[0] + matchPrinter[0] + 5, matchWinRect[1] + matchPrinter[1] + 5)
                            ahk.click()
                            break

            # print('4-3. Clicking Print Button...\n     (by search/3.print.png)')

            printButton = wait(lambda: ahk.image_search('search/3.print.png'), timeout_seconds=120)  # 출력 버튼 찾기
            if printButton:
                # x, y좌표에 5씩 더하는 이유 : 이미지 서치 성공시 반환받는 좌표는 왼쪽 상단 꼭지점기준의 좌표이므로 이 부분을 클릭시 버튼 안쪽이 아닌 모퉁이 부분을 클릭함으로써 오동작 발생 가능성이 있기 때문
                ahk.mouse_position = (matchWinRect[0] + printButton[0] + 5, matchWinRect[1] + printButton[1] + 5)
                ahk.click()  # 출력 버튼 클릭

            # print('4-4. Waiting for print job to finish...\n     (by search/4.close.png, Timeout: 120s)')
            matchWin = wait(lambda: getWinStrBegin('부동산 등기사항증명서 발급'), timeout_seconds=600)
            while matchWin:
                # print("부동산 등기사항증명서 발급 찾음")
                matchWin.to_top()
                matchWin.always_on_top = True
                matchWin.activate()

                closeButton = ahk.image_search('search/4.close.png')
                if closeButton:
                    matchWinRect = matchWin.rect
                    ahk.mouse_position = (
                        matchWinRect[0] + closeButton[0] + 5, matchWinRect[1] + closeButton[1] + 5)
                    ahk.click()
                    # print("닫기버튼클릭")
                    sleep(1)
                    return 'issue'

            os.system("taskkill /f /im rprtregisterxctrl.xgd")
            sleep(0.5)
            os.system("taskkill /f /im rprtregisterxctrl.xgd")
            sleep(0.5)

        finally:
            print('6. Closing ChromeDriver instance...')
            ahk.stop()
            sleep(2)
            # os._exit(0)
            
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
        #sleep(3)
        self.driver.quit()
