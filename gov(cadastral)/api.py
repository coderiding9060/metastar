from flask import request
from flask_api import FlaskAPI
from flask_cors import CORS
from flask import send_file, abort
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver import Firefox
from fake_useragent import UserAgent
from time import sleep
from datetime import datetime
import os
import json
import re
import cadastral

GOV_ID1 = "baecdu"
GOV_PW1 = "choi8125@@"

GOV_ID2 = "kjs264"
GOV_PW2 = "kjs885323@"

GOV_ID3 = "chojang6103"
GOV_PW3 = "kjs885323@"

GOV_ID4 = "gawn92"
GOV_PW4 = "rkdnjs92!!"

ACCOUNT = 4

FILE_NAME = "정부24 - 문서출력.pdf"

result = ["", "", 0, "cadastral"]

app = FlaskAPI(__name__)
CORS(app)

@app.route("/cadastral/request", methods=['POST'])
def cadastral_download():
    start = datetime.now()
    global result
    response = request.data  # data is empty
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    print(response)
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    user_id = response['user_id'] # 유저ID
    unique_number = response['unique_number'] # 부동산 고유번호
    path_time = response['path_time']
    callNumber = int(response['callNumber'])
    print(callNumber)
    uid = response['uid']
    result[0] = uid
    result[2] = 0
    
    option = Options() # 셀레니움 옵션
    # option.add_argument('--window-size=1890,1030') # 창 크기
    option.add_argument("--disable-gpu")
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("--no-sandbox")
    option.add_argument("test-type"); 
    option.add_argument("--js-flags=--expose-gc"); 
    option.add_argument("--enable-precise-memory-info"); 
    option.add_argument("--disable-default-apps"); 
    option.add_argument('--disable-extensions')
    option.add_argument('--incognito')
    option.add_argument('--disable-application-cache')

    option.add_experimental_option("detach", True) # 꺼지지 않고 유지


    curr_dir = os.getcwd() # 현재 디렉토리 위치
    curr_dir = curr_dir.replace("\\", "/")
    curr_dir_file = curr_dir + "/files" # 현재 디렉토리 위치
    path = user_id+"/"+unique_number+"/"+path_time # 유저ID/부동산고유번호/오늘날짜
    result[1] = path
    download_path = os.path.join(curr_dir_file, path) # 현재디텍토리위치/유저ID/부동산고유번호/오늘날짜
    download_path = download_path.replace("\\", "/")
    
    os.makedirs(download_path, exist_ok=True) # 디렉토리 생성
    # 프린팅 세팅
    settings = {
        "recentDestinations": [
            {
                "id": "Save as PDF",
                "origin": "local",
                "account": ""
            }
        ],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
        "isLandscapeEnabled": True, # 가로 설정
        "isHeaderFooterEnabled": False # 머리글, 바닥글 설정
    }

    prefs = {
        'printing.print_preview_sticky_settings.appState': json.dumps(settings),
        'savefile.default_directory': download_path, # 다운로드될 디렉토리 위치 설정
        'profile.managed_default_content_settings.images': 1
    }
    option.add_experimental_option('prefs', prefs)
    option.add_argument('--kiosk-printing') # 인쇄대화상자를 표시하지 않음
    # option.add_argument("'chrome.prefs': {'profile.managed_default_content_settings.images': 2}")

    ## 인터넷 등기소
    print(unique_number)

    ### 정부24
    address = response['address']
    # 경상남도 거창군 거창읍 새동네2길 40 거창코아루에듀시티2단지 제203동 제3층 제303호 [대평리 1518]
    # 경상남도 거창군 거창읍 교촌길 110-12 [가지리 294]
    # 서울특별시 성동구 연무장길 37-14 [성수동2가 316-46]
    # 서울특별시 강남구 가로수길 5 주건축물제1동 [신사동 537-5 외 1필지]
    # 서울특별시 강남구 가로수길 77 제5층 제501호 [신사동 532-11]
    # 서울특별시 강남구 역삼동 632-3
    # 서울특별시 강남구 강남대로 298 푸르덴셜타워 제4층호 [역삼동 838 외 4필지]
    
    address_division_for_gu = address.split(' ')
    if address_division_for_gu[2][-1] == '구':
        for i in range(len(address_division_for_gu)):
            if i == len(address_division_for_gu) - 1:
                address_division_for_gu[i] = ''
            else:
                address_division_for_gu[i] = address_division_for_gu[i+1]
        address = " ".join(list(filter(None, address_division_for_gu)))
    
    ### 주소 앞자리
    if "[" in address:
        print('[]있음')
        address_road = address.split('[')[0].strip()
        # 경상남도 거창군 거창읍 새동네2길 40 거창코아루에듀시티2단지 제203동 제3층 제303호
        # 경상남도 거창군 거창읍 교촌길 110-12
        # 서울특별시 성동구 연무장길 37-14
        # 서울특별시 강남구 가로수길 5 주건축물제1동
        # 서울특별시 강남구 가로수길 77 제5층 제501호
        address_road_division = address_road.split(' ')
        address_road_sido = address_road_division[0]
        # 경상남도
        # 경상남도
        # 서울특별시
        # 서울특별시
        # 서울특별시
        address_road_gungu = address_road_division[1]
        # 거창군
        # 거창군
        # 성동구
        # 강남구
        # 강남구
        address_road_third = address_road_division[2]
        # 거창읍
        # 거창읍
        # 연무장길
        # 가로수길
        # 가로수길
        last_word = address_road_third[-1]
        address_road_eupmyun = ''
        if last_word == '읍' or last_word == '면':
            address_road_eupmyun = address_road_division[2]
            # 거창읍
            # 거창읍
            # 가조면
                
        address_front = address_road_sido + ' ' + address_road_gungu + ' ' + address_road_eupmyun

        ## 주소 뒷자리
        address_dong = address.split('[')[1].replace(']','')
        # 대평리 1518
        # 가지리 294
        # 성수동2가 316-46
        # 신사동 537-5 외 1필지
        # 신사동 532-11
        lidong_number_address = address_dong.split(' ')[0]
        # 대평리
        # 가지리
        # 성수동2가
        # 신사동
        # 신사동
        gibun_address = address_dong.split(' ')[1]
        # 1518
        # 294
        # 316-46
        # 537-5
        # 532-11
        if '-' in gibun_address:
            address_bun = gibun_address.split('-')[0]
            # 316
            # 537
            # 532
            address_ho = gibun_address.split('-')[1]
            # 46
            # 5
            # 11
        else:
            address_bun = gibun_address
            address_ho = ''
        
        cadastral_address = address_front + ' ' + lidong_number_address

    else:
        print('[]없음')
        address_road = address
        print(address_road)
        # 서울특별시 강남구 역삼동 632-3
        # 경상남도 거창군 거창읍 가지리 292
        # 경상남도 거창군 거창읍 읍지리 292-23 제230동 제1층 제32호
        # 서울특별시 강남구 역삼동 292 제230동 제32호
        # 경상남도 거창군 가조면 기리 359-3
        # 경상남도 거창군 가조면 기리 359
        address_road_division = address_road.split(' ')
        address_road_sido = address_road_division[0]
        print(address_road_sido)
        # 서울특별시
        # 경상남도
        address_road_gungu = address_road_division[1]
        print(address_road_gungu)
        # 강남구
        # 거창군
        address_road_third = address_road_division[2]
        print(address_road_third)
        # 역삼동
        # 거창읍
        # 가조면
        last_word = address_road_third[-1]
        address_road_eupmyun = ''
        gibun_address = ''
        lidong_number_address = ''
        print(last_word)
        if last_word == '읍' or last_word == '면':
            address_road_eupmyun = address_road_third
            print(address_road_eupmyun)
            # 거창읍
            # 거창읍
            # 가조면
            # 가조면
            lidong_number_address = address_road_division[3]
            print(lidong_number_address)
            # 기리
            # 기리
            gibun_address = address_road_division[4]
            print(gibun_address)
            # 359-3
            # 359
        else:
            lidong_number_address = address_road_third
            gibun_address = address_road_division[3]
            # 292-23
            # 292

        if '-' in gibun_address:
            address_bun = gibun_address.split('-')[0]
            # 316
            # 537
            # 532
            address_ho = gibun_address.split('-')[1]
            # 46
            # 5
            # 11
        else:
            address_bun = gibun_address
            address_ho = ''

        address_front = address_road_sido + ' ' + address_road_gungu + ' ' + address_road_eupmyun
        cadastral_address = address_front + ' ' + lidong_number_address
    
    print(cadastral_address)
    
    # 정부24
    if callNumber%4 == 0:
          connection = cadastral.CadastralDownloadPDF(GOV_ID1, GOV_PW1, option)
    elif callNumber%4 == 1:
        connection = cadastral.CadastralDownloadPDF(GOV_ID2, GOV_PW2, option)
    elif callNumber%4 == 2:
        connection = cadastral.CadastralDownloadPDF(GOV_ID3, GOV_PW3, option)
    elif callNumber%4 == 3:
        connection = cadastral.CadastralDownloadPDF(GOV_ID4, GOV_PW4, option)

    sleep(callNumber*10)
    connection.login()

    try:
        connection.cadastral(cadastral_address, lidong_number_address, address_bun, address_ho)
        try:
            os.rename(f'{download_path}'+'/'+FILE_NAME, f'{download_path}'+'/'+'cadastral.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경
            connection.close()
            finish = datetime.now()
            runningTime = finish - start
            result[2] = 1
            print("######################### Running time: " + str(runningTime))
            print(result)
            return result # 성공
        except Exception as e:
            connection.close()
            finish = datetime.now()
            runningTime = finish - start
            result[2] = 2
            print("######################### Running time: " + str(runningTime))
            print(e)
            print(result)
            return result # 파일 못 찾음
    except Exception as e:
        connection.close()
        finish = datetime.now()
        runningTime = finish - start
        result[2] = 2
        print("######################### Running time: " + str(runningTime))
        print(e)
        print(result)
        return result     # 실행 실패

@app.route("/status", methods=['POST'])
def cadastral_status():
    global result
    print(result)
    return result

@app.route("/cadastral/reassign", methods=['POST'])
def cadastral_reassign():
    start = datetime.now()
    global result
    response = request.data  # data is empty
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    print(response)
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    user_id = response['user_id'] # 유저ID
    unique_number = response['unique_number'] # 부동산 고유번호
    path = response['path']
    callNumber = int(response['callNumber'])
    print(callNumber)
    uid = response['uid']
    result[0] = uid
    result[1] = path
    result[2] = 0
    
    option = Options() # 셀레니움 옵션
    # option.add_argument('--window-size=1890,1030') # 창 크기
    option.add_argument("--disable-gpu")
    option.add_argument("--no-sandbox")
    option.add_experimental_option("detach", True) # 꺼지지 않고 유지

    option.add_argument("test-type"); 
    option.add_argument("--js-flags=--expose-gc"); 
    option.add_argument("--enable-precise-memory-info"); 
    option.add_argument("--disable-default-apps"); 
    option.add_argument('--disable-extensions')
    option.add_argument('--incognito')
    option.add_argument('--disable-application-cache')

    curr_dir = os.getcwd() # 현재 디렉토리 위치
    curr_dir = curr_dir.replace("\\", "/")
    curr_dir_file = curr_dir + "/files" # 현재 디렉토리 위치
    download_path = os.path.join(curr_dir_file, path) # 현재디텍토리위치/유저ID/부동산고유번호/오늘날짜
    download_path = download_path.replace("\\", "/")
    
    try:
        os.rename(f'{download_path}'+'/'+FILE_NAME, f'{download_path}'+'/'+'cadastral.pdf')
        finish = datetime.now()
        runningTime = finish - start
        result[2] = 1
        print("######################### Running time: " + str(runningTime))
        print(result)
        return result # 성공
    except:
        try:
            os.rename(f'{download_path}'+'/'+'cadastral.pdf', f'{download_path}'+'/'+'cadastral.pdf')
            finish = datetime.now()
            runningTime = finish - start
            result[2] = 1
            print("######################### Running time: " + str(runningTime))
            print(result)
            return result # 성공
        except:
            os.makedirs(download_path, exist_ok=True) # 디렉토리 생성
            # 프린팅 세팅
            settings = {
                "recentDestinations": [
                    {
                        "id": "Save as PDF",
                        "origin": "local",
                        "account": ""
                    }
                ],
                "selectedDestinationId": "Save as PDF",
                "version": 2,
                "isLandscapeEnabled": True, # 가로 설정
                "isHeaderFooterEnabled": False # 머리글, 바닥글 설정
            }

            prefs = {
                'printing.print_preview_sticky_settings.appState': json.dumps(settings),
                'savefile.default_directory': download_path, # 다운로드될 디렉토리 위치 설정
                'profile.managed_default_content_settings.images': 1
            }
            option.add_argument('--kiosk-printing') # 인쇄대화상자를 표시하지 않음
            option.add_experimental_option('prefs', prefs)
            # option.add_argument("'chrome.prefs': {'profile.managed_default_content_settings.images': 2}")

            ## 인터넷 등기소
            print(unique_number)

            ### 정부24
            address = response['address']
            # 경상남도 거창군 거창읍 새동네2길 40 거창코아루에듀시티2단지 제203동 제3층 제303호 [대평리 1518]
            # 경상남도 거창군 거창읍 교촌길 110-12 [가지리 294]
            # 서울특별시 성동구 연무장길 37-14 [성수동2가 316-46]
            # 서울특별시 강남구 가로수길 5 주건축물제1동 [신사동 537-5 외 1필지]
            # 서울특별시 강남구 가로수길 77 제5층 제501호 [신사동 532-11]
            # 서울특별시 강남구 역삼동 632-3
            # 서울특별시 강남구 강남대로 298 푸르덴셜타워 제4층호 [역삼동 838 외 4필지]
            
            address_division_for_gu = address.split(' ')
            if address_division_for_gu[2][-1] == '구':
                for i in range(len(address_division_for_gu)):
                    if i == len(address_division_for_gu) - 1:
                        address_division_for_gu[i] = ''
                    else:
                        address_division_for_gu[i] = address_division_for_gu[i+1]
                address = " ".join(list(filter(None, address_division_for_gu)))
            
            ### 주소 앞자리
            if "[" in address:
                print('[]있음')
                address_road = address.split('[')[0].strip()
                # 경상남도 거창군 거창읍 새동네2길 40 거창코아루에듀시티2단지 제203동 제3층 제303호
                # 경상남도 거창군 거창읍 교촌길 110-12
                # 서울특별시 성동구 연무장길 37-14
                # 서울특별시 강남구 가로수길 5 주건축물제1동
                # 서울특별시 강남구 가로수길 77 제5층 제501호
                address_road_division = address_road.split(' ')
                address_road_sido = address_road_division[0]
                # 경상남도
                # 경상남도
                # 서울특별시
                # 서울특별시
                # 서울특별시
                address_road_gungu = address_road_division[1]
                # 거창군
                # 거창군
                # 성동구
                # 강남구
                # 강남구
                address_road_third = address_road_division[2]
                # 거창읍
                # 거창읍
                # 연무장길
                # 가로수길
                # 가로수길
                last_word = address_road_third[-1]
                address_road_eupmyun = ''
                if last_word == '읍' or last_word == '면':
                    address_road_eupmyun = address_road_division[2]
                    # 거창읍
                    # 거창읍
                    # 가조면
                        
                address_front = address_road_sido + ' ' + address_road_gungu + ' ' + address_road_eupmyun

                ## 주소 뒷자리
                address_dong = address.split('[')[1].replace(']','')
                # 대평리 1518
                # 가지리 294
                # 성수동2가 316-46
                # 신사동 537-5 외 1필지
                # 신사동 532-11
                lidong_number_address = address_dong.split(' ')[0]
                # 대평리
                # 가지리
                # 성수동2가
                # 신사동
                # 신사동
                gibun_address = address_dong.split(' ')[1]
                # 1518
                # 294
                # 316-46
                # 537-5
                # 532-11
                if '-' in gibun_address:
                    address_bun = gibun_address.split('-')[0]
                    # 316
                    # 537
                    # 532
                    address_ho = gibun_address.split('-')[1]
                    # 46
                    # 5
                    # 11
                else:
                    address_bun = gibun_address
                    address_ho = ''
                
                cadastral_address = address_front + ' ' + lidong_number_address

            else:
                print('[]없음')
                address_road = address
                print(address_road)
                # 서울특별시 강남구 역삼동 632-3
                # 경상남도 거창군 거창읍 가지리 292
                # 경상남도 거창군 거창읍 읍지리 292-23 제230동 제1층 제32호
                # 서울특별시 강남구 역삼동 292 제230동 제32호
                # 경상남도 거창군 가조면 기리 359-3
                # 경상남도 거창군 가조면 기리 359
                address_road_division = address_road.split(' ')
                address_road_sido = address_road_division[0]
                print(address_road_sido)
                # 서울특별시
                # 경상남도
                address_road_gungu = address_road_division[1]
                print(address_road_gungu)
                # 강남구
                # 거창군
                address_road_third = address_road_division[2]
                print(address_road_third)
                # 역삼동
                # 거창읍
                # 가조면
                last_word = address_road_third[-1]
                address_road_eupmyun = ''
                gibun_address = ''
                lidong_number_address = ''
                print(last_word)
                if last_word == '읍' or last_word == '면':
                    address_road_eupmyun = address_road_third
                    print(address_road_eupmyun)
                    # 거창읍
                    # 거창읍
                    # 가조면
                    # 가조면
                    lidong_number_address = address_road_division[3]
                    print(lidong_number_address)
                    # 기리
                    # 기리
                    gibun_address = address_road_division[4]
                    print(gibun_address)
                    # 359-3
                    # 359
                else:
                    lidong_number_address = address_road_third
                    gibun_address = address_road_division[3]
                    # 292-23
                    # 292

                if '-' in gibun_address:
                    address_bun = gibun_address.split('-')[0]
                    # 316
                    # 537
                    # 532
                    address_ho = gibun_address.split('-')[1]
                    # 46
                    # 5
                    # 11
                else:
                    address_bun = gibun_address
                    address_ho = ''

                address_front = address_road_sido + ' ' + address_road_gungu + ' ' + address_road_eupmyun
                cadastral_address = address_front + ' ' + lidong_number_address
            
            print(cadastral_address)
            
            # 정부24
            if callNumber%4 == 0:
                connection = cadastral.CadastralDownloadPDF(GOV_ID1, GOV_PW1, option)
            elif callNumber%4 == 1:
                connection = cadastral.CadastralDownloadPDF(GOV_ID2, GOV_PW2, option)
            elif callNumber%4 == 2:
                connection = cadastral.CadastralDownloadPDF(GOV_ID3, GOV_PW3, option)
            elif callNumber%4 == 3:
                connection = cadastral.CadastralDownloadPDF(GOV_ID4, GOV_PW4, option)

            connection.login()

            try:
                connection.cadastral(cadastral_address, lidong_number_address, address_bun, address_ho)
                try:
                    os.rename(f'{download_path}'+'/'+FILE_NAME, f'{download_path}'+'/'+'cadastral.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경
                    connection.close()
                    finish = datetime.now()
                    runningTime = finish - start
                    result[2] = 1
                    print("######################### Running time: " + str(runningTime))
                    print(result)
                    return result # 성공
                except Exception as e:
                    connection.close()
                    finish = datetime.now()
                    runningTime = finish - start
                    result[2] = 2
                    print("######################### Running time: " + str(runningTime))
                    print(e)
                    print(result)
                    return result # 파일 못 찾음
            except Exception as e:
                connection.close()
                finish = datetime.now()
                runningTime = finish - start
                result[2] = 2
                print("######################### Running time: " + str(runningTime))
                print(e)
                print(result)
                return result     # 실행 실패

@app.route("/file", methods=['POST'])
def file():
    response = request.data  # data is empty
    print(response)
    path = response['path']
    pdf = response['pdf']
    if "pdf" not in pdf:
        pdf += '.pdf'

    default = "C:/inetpub/ftproot/files/"
    api = default + path + pdf
    print(api)

    try:
        return send_file(api,
                         mimetype='application/pdf',
                         as_attachment=True)
    except FileNotFoundError:
        abort(404)

host_addr = '0.0.0.0'
port_num = 10002

if __name__ == "__main__":
    app.run(host=host_addr, port=port_num, threaded=True, ssl_context=('cert.crt', 'cert.key'))
