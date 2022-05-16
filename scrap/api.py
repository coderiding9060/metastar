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
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    print(response)
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    user_id = response['user_id'] # 유저ID
    unique_number = response['unique_number'] # 부동산 고유번호
    iros_type = response['certified_type']
    
    
    option = Options() # 셀레니움 옵션
    # option.add_argument('--window-size=1890,1030') # 창 크기
    option.add_experimental_option("detach", True) # 꺼지지 않고 유지
    curr_dir = os.getcwd() # 현재 디렉토리 위치
    curr_dir = curr_dir.replace("\\", "/")
    print(curr_dir)
    curr_dir_file = curr_dir + "/files" # 현재 디렉토리 위치
    print(curr_dir_file)
    date = re.sub(r"[^0-9]", "", str(datetime.now())) # 오늘날짜
    path = user_id+"/"+unique_number+"/"+date # 유저ID/부동산고유번호/오늘날짜
    print(path)
    download_path = os.path.join(curr_dir_file, path) # 현재디텍토리위치/유저ID/부동산고유번호/오늘날짜
    download_path = download_path.replace("\\", "/")
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
    address2 = response['address2']
    if address2 == '':
        address2 = address
    print("=========" + address2 + "==========")
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
                direct_dong = re.sub(r'[^0-9]', '', address_road_last_3)
                direct_dong += "동"
            elif "동" in address_road_last_3:
                direct_dong = re.sub(r'[^0-9]', '', address_road_last_3)
                direct_dong += "동"
                # 203동
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
        
        building_road = address_front + ' ' + address_road_eupmyun + ' ' + address_road_gil + ' ' + address_road_gilbungi
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
                direct_dong += "동"
            elif "동" in address_road_last_3:
                direct_dong = re.sub(r'[^0-9]', '', address_road_last_3)
                direct_dong += "동"
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
        print("-=-=-=-=-=-=-="+address2_division[0])
        address_front = address_road_sido + ' ' + address_road_gungu + ' ' + address_road_eupmyun
        building_road = ' '.join(list(filter(None, address2_division)))
        building_address = address_front + ' ' + lidong_number_address + ' ' + gibun_address
        cadastral_address = address_front + ' ' + lidong_number_address
        
        iros_type = response['certified_type']
    
    building_address = building_address.replace("   ", " ")
    building_address = building_address.replace("  ", " ")
    building_road = building_road.replace("   ", " ")
    building_road = building_road.replace("  ", " ")
    
    print(building_address)
    print(cadastral_address)
    
    # 정부24
    connection = gov.GovDownloadPDF(GOV_ID, GOV_PW, option)
    connection.login()
    FILE_NAME = "정부24 - 문서출력.pdf"
    connection.building(gubun, building_address, direct_ho, direct_dong, building_road)
    os.rename(f'{download_path}'+'/'+FILE_NAME, f'{download_path}'+'/'+'building.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경
    connection.cadastral(cadastral_address, lidong_number_address, address_bun, address_ho)
    os.rename(f'{download_path}'+'/'+FILE_NAME, f'{download_path}'+'/'+'cadastral.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경
    connection.cadastral_map(cadastral_address, lidong_number_address, address_bun, address_ho)
    os.rename(f'{download_path}'+'/'+FILE_NAME, f'{download_path}'+'/'+'cadastral_map.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경
    connection.close()

    # 등본
    connection = iros.IrosDownloadPDF(IROS_ID, IROS_PW, option)
    connection.login()
    FILE_NAME = "등본.pdf"
    isUpload = connection.realEstate(unique_number, PREPAYMENT, iros_type)
    sleep(5)
    # connection.realEstate(unique_number, PREPAYMENT, iros_type)
    if isUpload == 'browse': # 열람 완료 시
        print("열람완료")
        os.rename(f'{curr_dir}'+'/files/'+FILE_NAME, f'{download_path}'+'/'+'browse.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경
        connection.close()
    elif isUpload == 'issue': # 발급 완료 시
        print("발급완료")
        os.rename(f'{curr_dir}'+'/files/'+FILE_NAME, f'{download_path}'+'/'+'issue.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경
        connection.close()
    else:
        print("파일 생성 실패")
        
    # 토지이음
    connection = eum.eumDownloadPDF(EUM_ID, EUM_PW, option)
    connection.planning(building_address)
    FILE_NAME = "토지이용계획 - 토지이음.pdf"
    sleep(5)
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
