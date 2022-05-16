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
import browse

IROS_ID = "didokim1"
IROS_PW = "Taesoo68@"

result = ["", "", 0, "browse"]

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
    connection = browse.BrowseDownloadPDF(IROS_ID, IROS_PW, option)
    address_list = connection.browse(response['address'])
    connection.close()
    # 리턴값은 array = () 만 가능
    return address_list

@app.route("/browse/request", methods=['POST'])
def browse_download():
    start = datetime.now()
    global result
    response = request.data  # data is empty
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    print(response)
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    user_id = response['user_id'] # 유저ID
    unique_number = response['unique_number'] # 부동산 고유번호
    iros_type = response['certified_type']
    path_time = response['path_time']
    uid = response['uid']
    result[0] = uid
    result[2] = 0
    
    option = Options() # 셀레니움 옵션
    # option.add_argument('--window-size=1890,1030') # 창 크기
    option.add_argument('--disable-gpu')
    option.add_argument('--no-sandbox')
    option.add_argument("--enable-precise-memory-info"); 
    option.add_argument('--incognito')
    option.add_experimental_option("detach", True) # 꺼지지 않고 유지


    curr_dir = os.getcwd() # 현재 디렉토리 위치
    curr_dir = curr_dir.replace("\\", "/")
    curr_dir_file = curr_dir + "/files" # 현재 디렉토리 위치
    # date = re.sub(r"[^0-9]", "", str(datetime.now())) # 오늘날짜
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

    # 등본
    connection = browse.BrowseDownloadPDF(IROS_ID, IROS_PW, option)
    connection.login()
    FILE_NAME = "등본.pdf"
    
    try:
        connection.realEstate(unique_number, PREPAYMENT, iros_type)
        try:
            os.rename(f'{curr_dir}'+'/files/'+FILE_NAME, f'{download_path}'+'/'+'browse.pdf') # 첫번째 인자값 파일명을 두번째 인자값 파일명으로 변경
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
def browse_status():
    global result
    print(result)
    return result

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
