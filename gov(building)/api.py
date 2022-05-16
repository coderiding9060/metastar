from flask import request
from flask_api import FlaskAPI
from flask_cors import CORS
from flask import send_file, abort
from selenium.webdriver.chrome.options import Options
from time import sleep
from datetime import datetime
import os
import json
import re
import building

GOV_ID1 = "didokim1"
GOV_PW1 = "Taesoo68@"

GOV_ID2 = "showdaeki"
GOV_PW2 = "Apxktmxk0!23"

GOV_ID3 = "sj24sj"
GOV_PW3 = "sj6154sj!!"

GOV_ID4 = "kmhking1231"
GOV_PW4 = ".cjdtjd0618"

GOV_ID5 = "jeuni27"
GOV_PW5 = "wh273536wh!"

ACCOUNT = 5

FILE_NAME = "정부24 - 문서출력.pdf"
# CHROME_PROFILE = "--user-data-dir=C:/chrome-profiles/chrome-dev-profile"

result = ["", "", 0, "building"]

app = FlaskAPI(__name__)
CORS(app)

@app.route("/building/request", methods=['POST'])
def building_download():
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
    # option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36");  # May 05, 2022 : by indigo : headless-chrome->chrome으로 변경(한글깨짐 문제때문에 추가함[임시])
    option.add_argument("disable-gpu")  # May 05, 2022 : by indigo : 크롬드라이버 GPU 사용 X 옵션 설정
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("no-sandbox")
    option.add_argument("test-type"); 
    option.add_argument("--js-flags=--expose-gc"); 
    option.add_argument("--enable-precise-memory-info"); 
    option.add_argument("--disable-default-apps"); 
    option.add_argument('--disable-extensions')
    option.add_argument('--incognito')
    option.add_argument('--disable-application-cache')
    # if callNumber%5 == 0:
    #     option.add_argument(CHROME_PROFILE + "1")
    # elif callNumber%5 == 1:
    #     option.add_argument(CHROME_PROFILE + "2")
    # elif callNumber%5 == 2:
    #     option.add_argument(CHROME_PROFILE + "3")
    # elif callNumber%5 == 3:
    #     option.add_argument(CHROME_PROFILE + "4")
    # elif callNumber%5 == 4:
    #     option.add_argument(CHROME_PROFILE + "5")
    
    # option.add_argument('--window-size=1890,1030') # 창 크기
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
    address2 = response['address2']
    if address2 == '':
        address2 = address
    print("=========1" + address + "1==========")
    print("=========2" + address2 + "2==========")
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
    
    address_division_for_gu2 = address2.split(' ')
    if address_division_for_gu2[2][-1] == '구':
        for i in range(len(address_division_for_gu2)):
            if i == len(address_division_for_gu2) - 1:
                address_division_for_gu2[i] = ''
            else:
                address_division_for_gu2[i] = address_division_for_gu2[i+1]
        address2 = " ".join(list(filter(None, address_division_for_gu2)))
    
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
        address_road_gil = ''
        address_road_gilbungi = ''
        if last_word == '길' or last_word == '로':
            address_road_gil = address_road_division[2]
            # 연무장길
            # 가로수길
            # 가로수길
            address_road_gilbungi = address_road_division[3]
            # 37-14
            # 5
            # 77
        elif last_word == '읍' or last_word == '면':
            address_road_eupmyun = address_road_division[2]
            # 거창읍
            # 거창읍
            # 가조면
            address_road_gil = address_road_division[3]
            # 새동네2길
            # 교촌길
            address_road_gilbungi = address_road_division[4]
            # 40
            # 110-12
            
        gubun = response['gubun']
        direct_ho = ''
        direct_floor = ''
        direct_dong = ''
        if gubun == '집합건물':
            # 경상남도 거창군 거창읍 새동네2길 40 거창코아루에듀시티2단지 제203동 제3층 제303호
            # 서울특별시 강남구 가로수길 77 제5층 제501호
            address_road_last_1 = address_road_division[-1]
            # 제303호
            # 제501호
            if "호" in address_road_last_1:
                if "층" in address_road_last_1:
                    direct_ho = address_road_last_1.replace("제", "").replace("호", "")
                else:
                    direct_ho = re.sub(r'[^0-9]', '', address_road_last_1)
                # 303
                # 501
            address_road_last_2 = address_road_division[-2]
            # 제3층
            # 제5층
            if "층" in address_road_last_2:
                direct_floor = re.sub(r'[^0-9]', '', address_road_last_2)
                # 3
                # 5
            address_road_last_3 = address_road_division[-3]
            # 제203동
            # 77
            if "동" in address_road_last_2:
                direct_dong = re.sub(r'[^0-9]', '', address_road_last_2)
                if direct_dong == "":
                    direct_dong = address_road_last_2.replace("제", "")
            elif "동" in address_road_last_3:
                direct_dong = re.sub(r'[^0-9]', '', address_road_last_3)
                if direct_dong == "":
                    direct_dong = address_road_last_3.replace("제", "")
            else:
                direct_dong = "동명칭없음"
                
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
        
        building_road = address_front + ' ' + address_road_gil + ' ' + address_road_gilbungi
        building_address = address_front + ' ' + lidong_number_address + ' ' + gibun_address

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

        gubun = response['gubun']
        direct_ho = ''
        direct_floor = ''
        direct_dong = ''

        if gubun == '집합건물':
            # 경상남도 거창군 거창읍 새동네2길 40 거창코아루에듀시티2단지 제203동 제3층 제303호
            # 서울특별시 강남구 가로수길 77 제5층 제501호
            address_road_last_1 = address_road_division[-1]
            # 제303호
            # 제501호
            if "호" in address_road_last_1:
                if "층" in address_road_last_1:
                    direct_ho = address_road_last_1.replace("제", "").replace("호", "")
                else:
                    direct_ho = re.sub(r'[^0-9]', '', address_road_last_1)
                # 303
                # 501
            address_road_last_2 = address_road_division[-2]
            # 제3층
            # 제5층
            if "층" in address_road_last_2:
                direct_floor = re.sub(r'[^0-9]', '', address_road_last_2)
                # 3
                # 5
            address_road_last_3 = address_road_division[-3]
            # 제203동
            # 77
            if "동" in address_road_last_2:
                direct_dong = re.sub(r'[^0-9]', '', address_road_last_3)
                # direct_dong += "동"
            elif "동" in address_road_last_3:
                direct_dong = re.sub(r'[^0-9]', '', address_road_last_3)
                # direct_dong += "동"
                # 203동
            else:
                direct_dong = "동명칭없음"
        
        address2_division = address2.split(' ')
        j = 0
        for i in range(len(address2_division)):
            if address2_division[i].isnumeric():
                for j in range(i+1, len(address2_division)):
                    address2_division[j] = ""
                break
        if address2_division[0] in address_road_sido:
            address2_division[0] = address_road_sido
        
        address_front = address_road_sido + ' ' + address_road_gungu + ' ' + address_road_eupmyun
        building_road = ' '.join(list(filter(None, address2_division)))
        building_address = address_front + ' ' + lidong_number_address + ' ' + gibun_address
    
    building_address = building_address.replace("   ", " ")
    building_address = building_address.replace("  ", " ")
    building_road = building_road.replace("   ", " ")
    building_road = building_road.replace("  ", " ")
    
    print(building_address)
    
    # 정부24
    if callNumber%5 == 0:
        connection = building.BuildingDownloadPDF(GOV_ID1, GOV_PW1, option)
    elif callNumber%5 == 1:
        connection = building.BuildingDownloadPDF(GOV_ID2, GOV_PW2, option)
    elif callNumber%5 == 2:
        connection = building.BuildingDownloadPDF(GOV_ID3, GOV_PW3, option)
    elif callNumber%5 == 3:
        connection = building.BuildingDownloadPDF(GOV_ID4, GOV_PW4, option)
    elif callNumber%5 == 4:
        connection = building.BuildingDownloadPDF(GOV_ID5, GOV_PW5, option)
    
    sleep(callNumber*10)
    connection.login()
    
    try:
        connection.building(gubun, building_address, direct_ho, direct_dong, building_road)
        try:
            os.rename(f'{download_path}'+'/'+FILE_NAME, f'{download_path}'+'/'+'building.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경
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
def building_status():
    global result
    print(result)
    return result

@app.route("/building/reassign", methods=['POST'])
def building_reassign():
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

    # option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36");  # May 05, 2022 : by indigo : headless-chrome->chrome으로 변경(한글깨짐 문제때문에 추가함[임시])
    option.add_argument("disable-gpu")  # May 05, 2022 : by indigo : 크롬드라이버 GPU 사용 X 옵션 설정
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("no-sandbox")
    option.add_argument("test-type"); 
    option.add_argument("--js-flags=--expose-gc"); 
    option.add_argument("--enable-precise-memory-info"); 
    option.add_argument("--disable-default-apps"); 
    option.add_argument('--disable-extensions')
    option.add_argument('--incognito')
    option.add_argument('--disable-application-cache')

    # option.add_argument('--window-size=1890,1030') # 창 크기
    option.add_experimental_option("detach", True) # 꺼지지 않고 유지
    
    curr_dir = os.getcwd() # 현재 디렉토리 위치
    curr_dir = curr_dir.replace("\\", "/")
    curr_dir_file = curr_dir + "/files" # 현재 디렉토리 위치
    download_path = os.path.join(curr_dir_file, path) # 현재디텍토리위치/유저ID/부동산고유번호/오늘날짜
    download_path = download_path.replace("\\", "/")
    
    try:
        os.rename(f'{download_path}'+'/'+FILE_NAME, f'{download_path}'+'/'+'building.pdf')
        finish = datetime.now()
        runningTime = finish - start
        result[2] = 1
        print("######################### Running time: " + str(runningTime))
        print(result)
        return result # 성공
    except:
        try:
            os.rename(f'{download_path}'+'/'+'building.pdf', f'{download_path}'+'/'+'building.pdf')
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
            option.add_experimental_option('prefs', prefs)
            option.add_argument('--kiosk-printing') # 인쇄대화상자를 표시하지 않음 
            # option.add_argument("'chrome.prefs': {'profile.managed_default_content_settings.images': 2}")

            ## 인터넷 등기소
            print(unique_number)

            ### 정부24
            address = response['address']
            address2 = response['address2']
            if address2 == '':
                address2 = address
            print("=========1" + address + "1==========")
            print("=========2" + address2 + "2==========")
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
            
            address_division_for_gu2 = address2.split(' ')
            if address_division_for_gu2[2][-1] == '구':
                for i in range(len(address_division_for_gu2)):
                    if i == len(address_division_for_gu2) - 1:
                        address_division_for_gu2[i] = ''
                    else:
                        address_division_for_gu2[i] = address_division_for_gu2[i+1]
                address2 = " ".join(list(filter(None, address_division_for_gu2)))
            
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
                address_road_gil = ''
                address_road_gilbungi = ''
                if last_word == '길' or last_word == '로':
                    address_road_gil = address_road_division[2]
                    # 연무장길
                    # 가로수길
                    # 가로수길
                    address_road_gilbungi = address_road_division[3]
                    # 37-14
                    # 5
                    # 77
                elif last_word == '읍' or last_word == '면':
                    address_road_eupmyun = address_road_division[2]
                    # 거창읍
                    # 거창읍
                    # 가조면
                    address_road_gil = address_road_division[3]
                    # 새동네2길
                    # 교촌길
                    address_road_gilbungi = address_road_division[4]
                    # 40
                    # 110-12
                    
                gubun = response['gubun']
                direct_ho = ''
                direct_floor = ''
                direct_dong = ''
                if gubun == '집합건물':
                    # 경상남도 거창군 거창읍 새동네2길 40 거창코아루에듀시티2단지 제203동 제3층 제303호
                    # 서울특별시 강남구 가로수길 77 제5층 제501호
                    address_road_last_1 = address_road_division[-1]
                    # 제303호
                    # 제501호
                    if "호" in address_road_last_1:
                        if "층" in address_road_last_1:
                            direct_ho = address_road_last_1.replace("제", "").replace("호", "")
                        else:
                            direct_ho = re.sub(r'[^0-9]', '', address_road_last_1)
                        # 303
                        # 501
                    address_road_last_2 = address_road_division[-2]
                    # 제3층
                    # 제5층
                    if "층" in address_road_last_2:
                        direct_floor = re.sub(r'[^0-9]', '', address_road_last_2)
                        # 3
                        # 5
                    address_road_last_3 = address_road_division[-3]
                    # 제203동
                    # 77
                    if "동" in address_road_last_2:
                        direct_dong = re.sub(r'[^0-9]', '', address_road_last_2)
                        if direct_dong == "":
                            direct_dong = address_road_last_2.replace("제", "")
                    elif "동" in address_road_last_3:
                        direct_dong = re.sub(r'[^0-9]', '', address_road_last_3)
                        if direct_dong == "":
                            direct_dong = address_road_last_3.replace("제", "")
                    else:
                        direct_dong = "동명칭없음"
                        
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
                
                building_road = address_front + ' ' + address_road_gil + ' ' + address_road_gilbungi
                building_address = address_front + ' ' + lidong_number_address + ' ' + gibun_address

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

                gubun = response['gubun']
                direct_ho = ''
                direct_floor = ''
                direct_dong = ''

                if gubun == '집합건물':
                    # 경상남도 거창군 거창읍 새동네2길 40 거창코아루에듀시티2단지 제203동 제3층 제303호
                    # 서울특별시 강남구 가로수길 77 제5층 제501호
                    address_road_last_1 = address_road_division[-1]
                    # 제303호
                    # 제501호
                    if "호" in address_road_last_1:
                        if "층" in address_road_last_1:
                            direct_ho = address_road_last_1.replace("제", "").replace("호", "")
                        else:
                            direct_ho = re.sub(r'[^0-9]', '', address_road_last_1)
                        # 303
                        # 501
                    address_road_last_2 = address_road_division[-2]
                    # 제3층
                    # 제5층
                    if "층" in address_road_last_2:
                        direct_floor = re.sub(r'[^0-9]', '', address_road_last_2)
                        # 3
                        # 5
                    address_road_last_3 = address_road_division[-3]
                    # 제203동
                    # 77
                    if "동" in address_road_last_2:
                        direct_dong = re.sub(r'[^0-9]', '', address_road_last_3)
                        # direct_dong += "동"
                    elif "동" in address_road_last_3:
                        direct_dong = re.sub(r'[^0-9]', '', address_road_last_3)
                        # direct_dong += "동"
                        # 203동
                    else:
                        direct_dong = "동명칭없음"
                
                address2_division = address2.split(' ')
                j = 0
                for i in range(len(address2_division)):
                    if address2_division[i].isnumeric():
                        for j in range(i+1, len(address2_division)):
                            address2_division[j] = ""
                        break
                if address2_division[0] in address_road_sido:
                    address2_division[0] = address_road_sido
                
                address_front = address_road_sido + ' ' + address_road_gungu + ' ' + address_road_eupmyun
                building_road = ' '.join(list(filter(None, address2_division)))
                building_address = address_front + ' ' + lidong_number_address + ' ' + gibun_address
            
            building_address = building_address.replace("   ", " ")
            building_address = building_address.replace("  ", " ")
            building_road = building_road.replace("   ", " ")
            building_road = building_road.replace("  ", " ")
            
            print(building_address)
            
            # 정부24
            if callNumber%5 == 0:
                connection = building.BuildingDownloadPDF(GOV_ID1, GOV_PW1, option)
            elif callNumber%5 == 1:
                connection = building.BuildingDownloadPDF(GOV_ID2, GOV_PW2, option)
            elif callNumber%5 == 2:
                connection = building.BuildingDownloadPDF(GOV_ID3, GOV_PW3, option)
            elif callNumber%5 == 3:
                connection = building.BuildingDownloadPDF(GOV_ID4, GOV_PW4, option)
            elif callNumber%5 == 4:
                connection = building.BuildingDownloadPDF(GOV_ID5, GOV_PW5, option)
            
            connection.login()
            try:
                connection.building(gubun, building_address, direct_ho, direct_dong, building_road)
                try:
                    os.rename(f'{download_path}'+'/'+FILE_NAME, f'{download_path}'+'/'+'building.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경
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
