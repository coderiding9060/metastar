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


class BrowseDownloadPDF():

    def __init__(self, userId, passWd, option):
        self.option = option
        self.option.headless = False  # 창이 없음
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.option)
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
        self.anySignWaitting()

    def browse(self, address):
        self.address = address
        print(self.address)
        # 열람하기 - 간편 검색
        self.driver.get('http://www.iros.go.kr/frontservlet?cmd=RISUWelcomeViewC')
        self.popupClose()
        self.driver.get('http://www.iros.go.kr/frontservlet?cmd=RISUWelcomeViewC')

        # alert
        try:
            WebDriverWait(self.driver, 1).until(EC.alert_is_present())
        except UnexpectedAlertPresentException:
            alert = self.driver.switch_to.alert
            alert.accept()
        except:
            print("no alert")

        self.anySignWaitting()
        # iframe 내부
        self.driver.switch_to.frame('inputFrame')
        # self.driver.find_element_by_id('txt_simple_address').send_keys(self.address)
        # 주소
        self.driver.execute_script(
            """
            document.querySelector('#txt_simple_address').setAttribute('value', '""" + self.address + """')
            """
        )
        # 검색
        # search = self.driver.find_element_by_id('btnSrchSojae')
        # search.click()
        self.driver.find_element_by_id('btnSrchSojae').send_keys(Keys.RETURN)
        # alert
        try:
            WebDriverWait(self.driver, 1).until(EC.alert_is_present())
        except UnexpectedAlertPresentException:
            alert = self.driver.switch_to.alert
            alert.accept()
        except:
            print("no alert")

        # sleep(1)
        self.driver.switch_to.default_content()
        # sleep(1)
        self.driver.switch_to.frame('resultFrame')
        # sleep(1)
        self.driver.switch_to.frame('frmOuterModal')
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        elements = soup.select('.list_table table tbody tr')

        address_list = []
        for result in elements[1:]:
            real_estate_number = result.select_one(".tx_ct:first-child").get_text().strip()
            real_estate_category = result.select_one("td:nth-child(2)").get_text().strip()
            real_estate_address = result.select_one("td:nth-child(3)").get_text().strip()
            real_estate_status = result.select_one("td:nth-child(5)").find('img')['alt'].strip()
            address_list.append([real_estate_number, real_estate_category, real_estate_address, real_estate_status])
        address_list.reverse()
        print(address_list)
        return address_list

    ### 열람하기
    def realEstate(self, real_estate_unique, payment, iros_type):

        # 모드 확인 변수 mode [테스트 : 'test', 일반 열람 : 'browse', 에러 : 'error']
        mode = None

        # 진행 단계 확인 변수 step [기본값 : 1]
        step = 1

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

        # 열람하기 - 고유번호로 찾기
        self.popupClose()
        self.driver.get('http://www.iros.go.kr/frontservlet?cmd=RISUWelcomeViewC')
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
        # 결제대상 부동산
        self.driver.execute_script(
            """
            if(document.readyState === "complete") {
                var next = document.querySelector('.btn1_up_bg02_action')
                next.click()
            }      
            """
        )
        sleep(3)
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

        sleep(2)
        # 선불전자지급수단
        self.anySignWaitting()
        pay = self.driver.find_element_by_id('inpMtdCls3')
        pay.click()
        sleep(0.5)
        # 선불전자지급수단번호 및 비밀번호
        self.driver.execute_script(
            """
            document.querySelector('#inpEMoneyNo1').setAttribute('value', '""" + self.payment[0] + """')
            document.querySelector('#inpEMoneyNo2').setAttribute('value', '""" + self.payment[1] + """')
            document.querySelector('#inpEMoneyPswd').setAttribute('value', '""" + self.payment[2] + """')
            """
        )
        sleep(0.5)
        # 위 내용에 동의합니다.
        check = self.driver.find_element_by_id('id_check2')
        check.click()

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
            sleep(5)
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

        sleep(3)
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
        sleep(1)

        # Apr 27, 2022 : by indigo : 열람 -> 테스트 화면 출력 팝업창 출력시 팝업창의 테스트 출력 버튼 클릭하는 코드 수정
        try:
            print("핸들값 : " + self.driver.window_handles[1])
            if self.driver.window_handles[1] is not None:  # 테스트 팝업창이 있는 경우
                print("1핸들 null아님")
                self.driver.switch_to.window(self.driver.window_handles[1])  # 테스트 팝업창으로 전환
                # 테스트 팝업창의 출력 버튼 클릭
                element = self.driver.find_element_by_class_name('btn_blue')
                element.click()

                # self.driver.execute_script(
                #     """
                #     if(document.readyState === "complete") {
                #         var button = document.querySelector(".btn_blue");
                #         var button_name = button.innerHTML;
                #         button.click();
                #     }
                #     """
                # )
                sleep(3)
                self.driver.switch_to.window(self.driver.window_handles[0])
                sleep(1)
                # 테스트 열람 모드 확인
                alertTitle = '인터넷등기소'
                alertWin = getWinStrBegin(alertTitle)  # 테스트 열람 alert창

                if alertWin:
                    alertWin.to_top()
                    alertWin.always_on_top = True
                    if alertWin.activate() is None:
                        print("인터넷 등기소창 활성화안됨")
                        alertWin.activate()
                    elif alertWin.activate() is not None:
                        print("인터넷 등기소창 활성화됨")
                    else :
                        print("등기소창 에러")
                    ahk.send_input('{Enter}')
                    sleep(10)
                    print("등기소 alert창 끔")
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    self.anySignWaitting()
                    # 열람
                    element = self.driver.find_elements_by_class_name('btn1_n_bg02_action')
                    element[1].click()
                print("=-=-=-=-=-=-=-=-= 열람/발급 버튼 재클릭 =-=-=-=-=-=-=-=-=")
                sleep(10)


        except Exception as e:
            print(e)
        print("=-=-=-=-=-=-=-=-= 4성공 =-=-=-=-=-=-=-=-=")

        # 열람
        try:
            print('ahk for browse start!')
            

            while mode is None:  # 테스트/일반 열람 중 어떤 모드인지 판별이 안된 경우
                # 일반 열람 모드 확인
                browseTitle = '부동산 등기사항증명서 열람'
                browseWin = getWinStrBegin(browseTitle)  # 일반 열람 화면 창

                # 테스트 열람 모드 확인
                alertTitle = '인터넷등기소'
                alertWin = getWinStrBegin(alertTitle)  # 테스트 열람 alert창

                # 에러 화면 확인
                errorTitle = '서비스종료'
                errorWin = getWinStrBegin(errorTitle)  # 에러 화면 창

                if step == 1:
                    if browseWin:  # 일반 열람 모드, 진행 단계가 1단계인 경우
                        mode = 'browse'
                        step = step + 1
                        print(mode)
                        break
                    if alertWin:  # 테스트 열람 모드, 진행 단계가 1단계인 경우
                        mode = 'test'
                        print(mode)
                        break
                    if errorWin:  # 에러 창 출력, 진행 단계가 1단계인 경우
                        mode = 'error'
                        print(mode)
                        break

            # while mode == 'test':  # 테스트 열람 모드인경우
            #     # May 03, 2022 : by indigo : 인터넷 등기소 alert창뜨면 닫는 코드 추가[S]
            #     if step == 1:  # 1번스텝[테스트열람], 4번스텝[일반열람]에서 인터넷 등기소 alert창이 뜨기때문에 확인함
            #         try:
            #             print("인터넷등기소")
            #             alertTitle = '인터넷등기소'
            #             alertWin = getWinSrtBegin(alertTitle)  # 테스트 열람 alert창
            #             while alertWin:  # 테스트 열람 alert창이 떠있는 경우
            #                 alertWin.to_top()
            #                 alertWin.always_on_top = True
            #                 if alertWin.activate() is None:
            #                     alertWin.activate()
            #                 ahk.send_input('{Enter}')  # alert창 활성화 후 Enter키로 alert창을 닫음
                            
            #                 alertTitle = '인터넷등기소'
            #                 alertWin = getWinStrBegin(alertTitle)  # 테스트 열람 alert창
            #                 wait(lambda: getWinStrBegin(alertTitle), timeout_seconds=3)  # alert창을 재 조회 함
            #         except TimeoutExpired as e:  # alert창 재조회시 timeout이되면 정상적으로 창이 닫힌것으로 판단                        
            #             if step == 1 and mode == 'test':
            #                 self.driver.switch_to.window(self.driver.window_handles[0])  # 인터넷 등기소 창 선택
            #                 print("등기소 원본창 선택!")
            #                 sleep(1)
            #                 self.anySignWaitting()
            #                 sleep(1.0)
            #                 # 열람
            #                 self.wait_for((By.CLASS_NAME, 'btn1_n_bg02_action'))
            #                 element = self.driver.find_elements_by_class_name(
            #                     'btn1_n_bg02_action')  # 등기소 열람/발급 조회 페이지의 열람 버튼을 선택
            #                 element[1].click()  # 열람 버튼 클릭
            #                 # self.driver.execute_script(
            #                 #     """
            #                 #     if(document.readyState === "complete") {
            #                 #         var button = document.querySelectorAll(".btn1_n_bg02_action");
            #                 #         var button_name = button[1].innerHTML;

            #                 #         if(button_name=='열람'||button_name=='발급'){
            #                 #             button[1].click();
            #                 #         }
            #                 #     }
            #                 #     """
            #                 # )
            #                 sleep(2)
            #                 mode = 'browse'  # 열람 모드로 변경
            #                 step = step + 1  # 다음 step으로 이동
            #                 print("테스트 -> 열람모드 변경")
            #                 print(step)
            #                 break

            while mode == 'browse':  # 일반 열람 모드인경우
                print(step)
                # May 03, 2022 : by indigo : 인터넷 등기소 alert창뜨면 닫는 코드 추가[S]
                # if step == 2 or step == 5:  # 2번스텝[테스트열람], 5번스텝[일반열람] 동작
                if step == 2:  # 2번스텝[일반 열람] 동작
                    try:
                        print("step-2")
                        # 일반 열람 모드 확인
                        browseTitle = '부동산 등기사항증명서 열람'
                        browseWin = getWinStrBegin(browseTitle)  # 일반 열람 화면 창
                        while browseWin:  # 일반 열람 화면 창이 떠있는 경우
                            browseWin.to_top()
                            browseWin.always_on_top = True
                            browseWinRect = browseWin.rect

                            if browseWin.activate() is None:  # 일반 열람 화면 창이 활성화 되지 않은 경우
                                browseWin.activate()  # 일반 열람 화면 창을 활성화시킴
                            # browsePrintButton = ahk.image_search('search/browse_print.png')  # 일반 열람 화면 창의 출력 버튼 이미지 서치
                    
                            browsePrintButton = ahk.image_search('search/print_browse.png')  # 일반 열람 화면 창의 출력 버튼 이미지 서치    

                            if browsePrintButton:  # 일반 열람 화면 창의 출력 버튼 이미지 서치 성공시
                                print("프린트 버튼 찾음")
                                ahk.mouse_position = (browseWinRect[0] + browsePrintButton[0] + 2,
                                                      browseWinRect[1] + browsePrintButton[1] + 2)
                                ahk.click()  # 출력 버튼 클릭
                                print("in step 2")
                                # 인쇄[프린터 선택]창 확인
                                try:
                                    browsePrintTitle = '인쇄'
                                    browsePrintWin = wait(lambda: getWinStrBegin(browsePrintTitle),
                                                        timeout_seconds=10)  # 인쇄[프린터 선택]창 서치
                                except Exception as e:
                                    print("인쇄[프린터 선택]창 서치 실패")
                                    print(e)
                                else:
                                    if browsePrintWin:  # 인쇄[프린터 선택]창이 존재하는 경우(10초 내에 인쇄[프린터 선택]창을 찾은 경우)
                                        print("인쇄[프린터 선택]창 찾기 성공")
                                        step = step + 1  # 다음 step으로 이동
                                        break

                    except TimeoutExpired as e:  # 인쇄[프린터 선택]창 조회시 timeout된 경우
                        print(e)  # 에러 메세지 출력

                try:
                    print("step-3")
                    browsePrintTitle = '인쇄'
                    browsePrintWin = getWinStrBegin(browsePrintTitle)  # 인쇄[프린터 선택]창
                    sleep(2)
                    while browsePrintWin:  # 인쇄[프린터 선택]창이 존재하는 경우
                        browsePrintWin.to_top()
                        browsePrintWin.always_on_top = True
                        browsePrintWinRect = browsePrintWin.rect
                        if browsePrintWin.activate() is None:  # 인쇄[프린터 선택]창이 활성화 되지 않은 경우
                            browsePrintWin.activate()  # 인쇄[프린터 선택]창을 활성화시킴

                        if step == 3:
                            
                            browsePrintDropdownButton = ahk.image_search(
                                'search/browse.1.dropdown.png')  # 인쇄[프린터 선택]창의 드랍다운 버튼 이미지 서치
                            if browsePrintDropdownButton:  # 인쇄[프린터 선택]창의 드랍다운 버튼 이미지 서치 성공시
                                ahk.mouse_position = (browsePrintWinRect[0] + browsePrintDropdownButton[0] + 2,
                                                      browsePrintWinRect[1] + browsePrintDropdownButton[1] + 2)
                                ahk.click()  # 인쇄[프린터 선택]창의 드랍다운 버튼 클릭
                                ahk.mouse_position = (50,
                                                      50)  # 인쇄[프린터 선택]창의 드랍다운 버튼 클릭 후 50, 50위치로 마우스 커서 이동(마우스 포인터가 드랍다운 메뉴 위에 있는경우 다음에 찾을때 마우스에 가려져서 이미지 서치가 안되는 현상 발생)
                                sleep(1.0)
                                step = step + 1  # 다음 step으로 이동

                        if step == 4:
                            print("step-4")
                            browseSelectPrinterButton = ahk.image_search('search/browse.2.printer.png')  # 프린터 모델명 1 이미지
                            browseSelectPrinterButton1 = ahk.image_search(
                                'search/browse.2.printer1.png')  # 프린터 모델명 2 이미지

                            if browseSelectPrinterButton:  # 프린터 모델명 1 이미지 서치 성공시
                                ahk.mouse_position = (browsePrintWinRect[0] + browseSelectPrinterButton[0] + 2,
                                                      browsePrintWinRect[1] + browseSelectPrinterButton[1] + 2)
                                ahk.click()
                                print("1번 프린트 이미지 클릭")
                                print(step)
                                step = step + 1  # 다음 step으로 이동

                            elif browseSelectPrinterButton1:  # 프린터 모델명 2 이미지 서치 성공시
                                ahk.mouse_position = (browsePrintWinRect[0] + browseSelectPrinterButton1[0] + 2,
                                                      browsePrintWinRect[1] + browseSelectPrinterButton1[1] + 2)
                                ahk.click()
                                print("2번 프린트 이미지 클릭")
                                print(step)
                                step = step + 1  # 다음 step으로 이동

                        if step == 5:
                            print("step-5")
                            # browsePrintOutButton = ahk.image_search('search/browse.2.print.button.png')  # 인쇄[프린터 선택]창의 인쇄 버튼 이미지 서치
                            # sleep(0.5)
                            # if browsePrintOutButton:  # 인쇄[프린터 선택]창의 인쇄 버튼 이미지 서치 성공시
                                #ahk.mouse_position = (browsePrintWinRect[0] + browsePrintOutButton[0] + 2,
                                #                      browsePrintWinRect[1] + browsePrintOutButton[1] + 2)
                                #ahk.click()  # 인쇄[프린터 선택]창의 인쇄 버튼 클릭
                            sleep(1)
                            ahk.send_input('{Enter}')
                            step = step + 1  # 다음 step으로 이동

                        if step == 6:  # 6번스텝[일반 열람]에서 인터넷 등기소 alert창이 뜨기때문에 확인함
                            print("step-6")
                            alertTitle = '인터넷등기소'
                            alertWin = wait(lambda: getWinStrBegin(alertTitle), timeout_seconds=20)  # 인터넷 등기소 alert창 찾기

                            if alertWin:  # 인터넷 등기소 alert창 찾기 성공시
                                print("6단계 등기소창 찾음")
                                alertWin.to_top()
                                alertWin.always_on_top = True
                                if alertWin.activate() is None:  # 인터넷 등기소 alert창이 활성화 되지 않은 경우
                                    alertWin.activate()  # 인터넷 등기소 alert창 활성화시킴
                                ahk.send_input('{Enter}')  # alert창 활성화 후 Enter키로 alert창을 닫음
                                sleep(1)
                                alertTitle = '인터넷등기소'
                                alertWin = getWinStrBegin(alertTitle)  # 테스트 열람 alert창
                                if alertWin is False:  # 1초뒤 다시 인터넷 등기소 alert창을 찾았을때 찾지 못한 경우
                                    step = step + 1  # 다음 step으로 이동
                            else:
                                print("6단계 등기소창 못찾음")

                        if step == 7:
                            try:
                                print("step-7")
                                # 일반 열람 모드 확인
                                browseTitle = '부동산 등기사항증명서 열람'
                                browseWin = getWinStrBegin(browseTitle)  # 일반 열람 화면 창
                                if browseWin:  # 일반 열람 화면 창을 찾은 경우
                                    browseWin.to_top()
                                    browseWin.always_on_top = True
                                    browseWinRect = browseWin.rect
                                    if browseWin.activate() is None:  # 일반 열람 화면 창이 활성화 되지 않은 경우
                                        browseWin.activate()  # 일반 열람 화면 창을 활성화시킴
                                    browseCloseButton = ahk.image_search(
                                        'search/browse.4.close.png')  # 일반 열람 화면 닫기 버튼 이미지 서치
                                    if browseCloseButton:  # 일반 열람 화면 닫기 버튼 이미지 서치 성공시
                                        ahk.mouse_position = (browseWinRect[0] + browseCloseButton[0] + 2,
                                                              browseWinRect[1] + browseCloseButton[1] + 2)
                                        ahk.click()  # 일반 열람 화면 닫기 버튼 클릭
                                        sleep(3)
                                        # 일반 열람 모드 확인
                                        browseTitle = '부동산 등기사항증명서 열람'
                                        browseWin = getWinStrBegin(browseTitle)  # 일반 열람 화면 창
                                        if browseWin is False:  # 3초 뒤 일반 열람 화면 창을 못찾은 경우
                                            mode = None
                                            print('browse')
                                            return 'browse'

                                else:
                                    print("7번스텝 창 못찾음")


                            except TimeoutExpired as e:  # alert창 재조회시 timeout이되면 정상적으로 창이 닫힌것으로 판단
                                print("7단계 예외")
                                print(e)

                except TimeoutExpired as e:  # alert창 재조회시 timeout이되면 정상적으로 창이 닫힌것으로 판단
                    print(e)
                # May 03, 2022 : by indigo : 인터넷 등기소 alert창뜨면 닫는 코드 추가[E]

        except Exception as e:
            pass

        finally:
            print('완료 스텝 : ' + str(step))
            print('6. Closing ChromeDriver instance...')
            ahk.stop()
            sleep(1.0)
            # os._exit(0)

    def close(self):
        sleep(3)
        self.driver.quit()
