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
import iros
import gov
import eum

IROS_ID = "didokim1"
IROS_PW = "Taesoo68@"
GOV_ID = "didokim1"
GOV_PW = "Taesoo68@"
EUM_ID = "mustfintech0"
EUM_PW = "mufin00!!"

PREPAYMENT = ('C7311886','1472','aesoo68@') # 선불결제수단

app = FlaskAPI(__name__)
CORS(app)

@app.route("/", methods=['POST'])
def iros_address():
    response = request.data  # data is empty
    print(response)
    print(response['address'])
    option = Options() # 셀레니움 옵션
    # option.add_argument('--window-size=1890,1030') # 창 크기
    option.headless = False # 창이 없음
    option.add_experimental_option("detach", True) # 꺼지지 않고 유지
    connection = iros.IrosDownloadPDF(IROS_ID, IROS_PW, option)
    address_list = connection.browse(response['address'])
    connection.close()
    # 리턴값은 array = () 만 가능
    return address_list

@app.route("/unitTest", methods=['GET'])
def unitTest():
    # import macro
    connection = iros.IrosDownloadPDF(IROS_ID, IROS_PW)
    connection.login()
    connection.close()
    return 'success'

@app.route("/unitTest_eum", methods=['GET'])
def unitTest_eum_login():
    response = request.data  # data is empty
    print(response)
    print(response['address'])

    connection = eum.eumDownloadPDF(EUM_ID, EUM_PW)
    connection.planning(response['address'])
    connection.close()
    return 'success'

@app.route("/unitTest_gov", methods=['GET'])
def unitTest_gov_login():
    # import macro
    connection = gov.GovDownloadPDF(GOV_ID, GOV_PW)
    connection.login()
    connection.close()
    return 'success'

@app.route("/unitTest_iros", methods=['GET'])
def unitTest_iros_login():
    # import macro
    connection = iros.IrosDownloadPDF(IROS_ID, IROS_PW)
    connection.login()
    connection.close()
    return 'success'

@app.route("/download", methods=['POST'])
def gov_download():
    response = request.data  # data is empty
    print(response)
    user_id = response['user_id'] # 유저ID
    unique_number = response['unique_number'] # 부동산 고유번호
    iros_type = response['certified_type']
    
    option = Options() # 셀레니움 옵션
    # option.add_argument('--window-size=1890,1030') # 창 크기
    option.add_experimental_option("detach", True) # 꺼지지 않고 유지
    curr_dir = os.getcwd() # 현재 디렉토리 위치
    curr_dir.replace("₩", "/")
    print(curr_dir)
    curr_dir_file = curr_dir + "/files" # 현재 디렉토리 위치
    print(curr_dir_file)
    date = re.sub(r"[^0-9]", "", str(datetime.now())) # 오늘날짜
    path = user_id+"/"+unique_number+"/"+date # 유저ID/부동산고유번호/오늘날짜
    print(path)
    download_path = os.path.join(curr_dir_file, path) # 현재디텍토리위치/유저ID/부동산고유번호/오늘날짜
    download_path.replace("₩", "/")
    print(download_path)
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
    uid = response['uid']
    address = response['address']
    # 경상남도 거창군 거창읍 새동네2길 40 거창코아루에듀시티2단지 제203동 제3층 제303호 [대평리 1518]
    # 경상남도 거창군 거창읍 교촌길 110-12 [가지리 294]
    # 서울특별시 성동구 연무장길 37-14 [성수동2가 316-46]
    # 서울특별시 강남구 가로수길 5 주건축물제1동 [신사동 537-5 외 1필지]
    # 서울특별시 강남구 가로수길 77 제5층 제501호 [신사동 532-11]
    # 서울특별시 강남구 역삼동 632-3

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
        if last_word == '길':
            address_road_gil = address_road_division[3]
            # 연무장길
            # 가로수길
            # 가로수길
            address_road_gilbungi = address_road_division[4]
            # 37-14
            # 5
            # 77
        elif last_word == '읍' or last_word == '면':
            address_road_eupmyun = address_road_division[3]
            # 거창읍
            # 거창읍
            # 가조면
            address_road_gil = address_road_division[4]
            # 새동네2길
            # 교촌길
            address_road_gilbungi = address_road_division[5]
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
            if "동" in address_road_last_3:
                direct_dong = re.sub(r'[^0-9]', '', address_road_last_3)
                direct_dong += "동"
                # 203동
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

        building_address = address_front + ' ' + lidong_number_address + ' ' + gibun_address
        cadastral_address = address_front + ' ' + lidong_number_address
        
        iros_type = response['certified_type']

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
            if "동" in address_road_last_3:
                direct_dong = re.sub(r'[^0-9]', '', address_road_last_3)
                direct_dong += "동"
                # 203동
        address_front = address_road_sido + ' ' + address_road_gungu + ' ' + address_road_eupmyun

        building_address = address_front + ' ' + lidong_number_address + ' ' + gibun_address
        cadastral_address = address_front + ' ' + lidong_number_address
        
        iros_type = response['certified_type']

    print(building_address)
    print(cadastral_address)
    
    curr_dir.replace("₩", "/")
    download_path.replace("₩", "/")
    print("+++++++++++1" + curr_dir + "+++++++++++")
    print("+++++++++++1" + download_path + "+++++++++++")
    
    # 등본
    connection = iros.IrosDownloadPDF(IROS_ID, IROS_PW, option)
    connection.login()
    
    FILE_NAME = "등본.pdf"
    
    connection.realEstate(unique_number, PREPAYMENT, iros_type)
    os.rename(f'{curr_dir_file}'+'/'+FILE_NAME, f'{download_path}'+'/'+'issue.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경
    connection.close()

    curr_dir.replace("₩", "/")
    download_path.replace("₩", "/")
    print("+++++++++++2" + curr_dir + "+++++++++++")
    print("+++++++++++2" + download_path + "+++++++++++")

    # 정부24
    connection = gov.GovDownloadPDF(GOV_ID, GOV_PW, option)
    connection.login()

    FILE_NAME = "정부24 - 문서출력.pdf"
    
    connection.building(gubun, building_address, direct_ho, direct_dong)
    os.rename(f'{download_path}'+'/'+FILE_NAME, f'{download_path}'+'/'+'building.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경

    connection.cadastral(cadastral_address, lidong_number_address, address_bun, address_ho)
    os.rename(f'{download_path}'+'/'+FILE_NAME, f'{download_path}'+'/'+'cadastral.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경

    connection.cadastral_map(cadastral_address, lidong_number_address, address_bun, address_ho)
    os.rename(f'{download_path}'+'/'+FILE_NAME, f'{download_path}'+'/'+'cadastral_map.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경
    connection.close()

    curr_dir.replace("₩", "/")
    download_path.replace("₩", "/")
    print("+++++++++++3" + curr_dir + "+++++++++++")
    print("+++++++++++3" + download_path + "+++++++++++")

    # 토지이음
    connection = eum.eumDownloadPDF(EUM_ID, EUM_PW, option)
    connection.planning(building_address)
    FILE_NAME = "토지이용계획 - 토지이음.pdf"
    os.rename(f'{download_path}'+'/'+FILE_NAME, f'{download_path}'+'/'+'land_use_plan.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경
    
    connection.close()
    print([uid, path])
    return [uid, path]

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
