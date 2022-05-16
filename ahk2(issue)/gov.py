# from asyncio import wait_for
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
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

class GovDownloadPDF():

    def __init__(self, userId, passWd, option):
        self.option = option
        self.option.headless = False # 창이 없음
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
        self.driver.get('https://www.gov.kr/nlogin/?regType=ctab')
        login = self.driver.find_element_by_id('아이디')
        login.click()
        self.driver.find_element_by_id('userId').send_keys(self.userId)
        self.driver.find_element_by_id('pwd').send_keys(self.pwd)
        self.driver.find_element_by_id('pwd').send_keys(Keys.RETURN)

    # 건축물대장
    def building(self, category_type, address, direct_ho, direct_dong):
        print(category_type)
        print(address)
        print(direct_ho)
        print(direct_dong)

        # 페이지 이동
        self.driver.get('https://www.gov.kr/mw/AA020InfoCappView.do?CappBizCD=15000000098&HighCtgCD=A02004002&Mcode=10205')
        # 발급
        issued = self.driver.find_element_by_css_selector('#applyBtn a')
        issued.click()
        
        # 건축물소재지 - 검색
        address_name = self.wait_for((By.ID, '주소검색'))
        address_name.click()

        # 주소검색
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.find_element_by_id('txtRoad').send_keys(address)
        self.driver.find_element_by_id('txtRoad').send_keys(Keys.RETURN)

        # 검색한 주소 - 첫번째 자식
        result = self.wait_for((By.CSS_SELECTOR, '.address-result-list a:first-child'))
        result.click()
        # 행정처리기관 선택
        land = self.wait_for((By.CSS_SELECTOR, '.land a:nth-child(2)'))
        land.click()

        self.driver.switch_to.window(self.driver.window_handles[0])

        # 대장구분
        if category_type == '집합건물':
            # 집합(아파트,연립주택 등)
            category_btn = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장구분_.라디오코드2')
            category_btn.click()
            # 전유부
            type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드13')
            type.click()
        else:
            # 일반(단독주택)
            category_btn = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장구분_.라디오코드1')
            category_btn.click()
            # 일반
            type = self.driver.find_element_by_id('건축물관리대장발급신청서_IN-건축물관리대장발급신청서_입력항목_공통항목_대장종류_.라디오코드02')
            type.click()

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
        address_dong = self.driver.find_element_by_id('동명검색')
        address_dong.click()
        print(By.PARTIAL_LINK_TEXT)

        # 주소검색 - 선택
        WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(2))
        self.driver.switch_to.window(self.driver.window_handles[1])
        if category_type == '집합건물':
            ibtn = self.wait_for((By.PARTIAL_LINK_TEXT, direct_dong))
            if ibtn == '':
                ibtn = self.driver.find_element_by_css_selector('.ibtn button')
        else:
            ibtn = self.driver.find_element_by_css_selector('.ibtn button')
            
        ibtn.click()
        self.driver.switch_to.window(self.driver.window_handles[0])

        sleep(1)

        ho_name = ''
        if category_type == '집합건물':
            # 호명칭 - 검색
            ho_name = self.driver.find_element_by_id('호명검색')
            ho_name.click()

            # 주소검색 - 선택
            WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(2))
            self.driver.switch_to.window(self.driver.window_handles[1])
            ibtn = self.wait_for((By.PARTIAL_LINK_TEXT, direct_ho))
            ibtn.click()

            self.driver.switch_to.window(self.driver.window_handles[0])

        # 민원신청하기
        btn_end = self.driver.find_element_by_id('btn_end')
        btn_end.click()

        sleep(3)

        # 문서출력
        ibtn_a = self.wait_for((By.CSS_SELECTOR, 'tbody tr .cs-state .ibtn a'))
        ibtn_a.click()

        # 인쇄
        self.printing()

    # 토지대장
    def cadastral(self, cadastral_address, lidong_number_address, address_bun, address_ho):
        print(cadastral_address)
        print(lidong_number_address)
        print(address_bun)
        print(address_ho)

        # 페이지 이동
        self.driver.get('https://www.gov.kr/mw/AA020InfoCappView.do?CappBizCD=13100000026&HighCtgCD=A02001001&Mcode=10207')

        #발급
        issued = self.driver.find_element_by_css_selector('#applyBtn a')
        issued.click()

        # 검색
        btnAddress = self.wait_for((By.ID, 'btnAddress'))
        btnAddress.click()

        self.driver.switch_to.window(self.driver.window_handles[1])

        ### 대상토지 소재지
        # 지번주소 검색
        self.driver.find_element_by_id('txtAddr').send_keys(cadastral_address)
        search_btn = self.driver.find_element_by_css_selector('.ibtn button')
        search_btn.click()

        # 행정처리기관 선택
        try:
            land = self.wait_for((By.PARTIAL_LINK_TEXT, lidong_number_address))
        except:
            land = self.wait_for((By.CSS_SELECTOR, '.land a:nth-child(2)'))
        land.click()

        self.driver.switch_to.window(self.driver.window_handles[0])

        # 번지&호 입력
        self.driver.find_element_by_id('토지임야대장신청서_IN-토지임야대장신청서_신청토지소재지_주소정보_상세주소_번지').send_keys(address_bun)
        self.driver.find_element_by_id('토지임야대장신청서_IN-토지임야대장신청서_신청토지소재지_주소정보_상세주소_호').send_keys(address_ho)
        
        # 민원신청하기
        btn_end = self.driver.find_element_by_id('btn_end')
        btn_end.click()

        # 문서출력
        ibtn_a = self.wait_for((By.CSS_SELECTOR, 'tbody tr .cs-state .ibtn a'))
        ibtn_a.click()

        # 인쇄
        self.printing()

    # 지적도
    def cadastral_map(self, cadastral_address, lidong_number_address, address_bun, address_ho):
        print(cadastral_address)
        print(lidong_number_address)
        print(address_bun)
        print(address_ho)

        # 페이지 이동
        self.driver.get('https://www.gov.kr/mw/AA020InfoCappView.do?CappBizCD=13100000027&HighCtgCD=-&FAX_TYPE=B&Mcode=10208')

        #발급
        issued = self.driver.find_element_by_css_selector('#applyBtn a')
        issued.click()

        # 대상토지소재지 주소 - 검색
        btnAddress = self.wait_for((By.ID, '주소검색'))
        btnAddress.click()

        self.driver.switch_to.window(self.driver.window_handles[1])

        # 지번주소 검색
        self.driver.find_element_by_id('txtAddr').send_keys(cadastral_address)
        search_btn = self.driver.find_element_by_css_selector('.ibtn button')
        search_btn.click()

        # 행정처리기관 선택
        land = self.wait_for((By.PARTIAL_LINK_TEXT, lidong_number_address))
        # land = self.wait_for((By.CSS_SELECTOR, '.land a:nth-child(2)'))
        land.click()
        
        # 검색결과가 나오는 경우
        try:
            if self.driver.find_element_by_id('wrap'):
                wrap = self.wait_for((By.CSS_SELECTOR, 'tbody tr td a:first-child'))
                wrap.click()
        except:
            pass

        self.driver.switch_to.window(self.driver.window_handles[0])

        # 번지&호 입력
        self.driver.find_element_by_id('지적도임야도등본교부신청서_IN-지적도임야도등본교부신청서_신청토지소재지_주소정보_상세주소_번지').send_keys(address_bun)
        self.driver.find_element_by_id('지적도임야도등본교부신청서_IN-지적도임야도등본교부신청서_신청토지소재지_주소정보_상세주소_호').send_keys(address_ho)
        
        # 민원신청하기
        btn_end = self.driver.find_element_by_id('btn_end')
        btn_end.click()

        # 문서출력
        ibtn_a = self.wait_for((By.CSS_SELECTOR, 'tbody tr .cs-state .ibtn a'))
        ibtn_a.click()

        # 인쇄
        self.printing()

    def close(self):
        sleep(3)
        self.driver.quit()
