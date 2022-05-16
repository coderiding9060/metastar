### IROS Macro Proof-of-Concept v1
# By: work@xeung.tech

### requirements
# (pip) waiting, autohotkey(ahk), selenium and selenium driver (+ webdriver_manager on PoC env)
# (machine) autohotkey should be installed as global variable or on same dir, with admin access
# (machine) modu-print service should be installed and configured as well

### References
# view-source:http://www.iros.go.kr/iris/prt/RPRTCheckRegisterJ.jsp?openerName=
# view-source:http://www.iros.go.kr/frontservlet?cmd=RPRTViewRegisterC&isCallTestPrint=UnIsu
# http://www.iros.go.kr/frontservlet?cmd=RPRTViewRegisterC&isCallTestPrint=UnIsu
# http://www.iros.go.kr/iris/prt/RPRTCheckRegisterJ.jsp?openerName=UnIsu
# https://modu-print.tistory.com/category/%EB%8B%A4%EC%9A%B4%EB%A1%9C%EB%93%9C/%EB%AA%A8%EB%91%90%EC%9D%98%20%ED%94%84%EB%A6%B0%ED%84%B0
# https://github.com/spyoungtech/ahk
# https://pywinauto.readthedocs.io/en/latest/

from ahk.window import Window
from ahk.daemon import AHKDaemon
from ahk import AHK
from waiting import wait, TimeoutExpired
import os
import webbrowser

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service

import time
sleep = time.sleep

### Start AutoHotKey Daemon
ahk = AHKDaemon(executable_path='bin/AutoHotkeyU64.exe')
ahk.start()

### AHK Support Function
def getWinStrBegin(str, charset='cp949'):
  try:
    return list(filter(lambda win: win.title.startswith(str.encode(charset)), ahk.windows()))[0]
  except:
    return False




### Set Chrome Options
opts = webdriver.ChromeOptions()
opts.set_capability('pageLoadStrategy', 'eager')
opts.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
opts.headless = True
### For PoC Code only
# opts.add_argument('--ignore-certificate-errors')
# opts.add_argument('--ignore-ssl-errors')

### For PoC Code only - should be a fixed version based deploy on production env
# from webdriver_manager.chrome import ChromeDriverManager
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
driver = webdriver.Chrome(service=Service('bin/chromedriver.exe'), options=opts)


def clear_cache(driver, timeout=60):
    """Clear the cookies and cache for the ChromeDriver instance."""
    # navigate to the settings page
    driver.get('chrome://settings/clearBrowserData')

    # wait for the button to appear
    wait = WebDriverWait(driver, timeout)
    wait.until(get_clear_browsing_button)

    # click the button to clear the cache
    get_clear_browsing_button(driver).click()

    # wait for the button to be gone before returning
    wait.until_not(get_clear_browsing_button)





injectCode = """
console.log('IROS Macro PoC injectCode injected!')
try {
  window.f_MaLaunch_ = function (vstrApp, vstrCallURL, vstrCookie, vstrAppParam) {
    var makeurl = "";

    if (vstrAppParam == "")
      makeurl = vstrCookie + "@" + vstrCallURL + "@" + "MA== " + "@" + f_Ma_base64_encode(f_Ma_getAdams());
    else
      makeurl = vstrCookie + "@" + vstrCallURL + "@" + f_Ma_base64_encode(vstrAppParam) + "@" + f_Ma_base64_encode(f_Ma_getAdams());

    var vstrExeCallUrl;
    vstrExeCallUrl = vstrApp + "://?registapp" + makeurl;

    var textElem = document.createElement("div");
    textElem.innerHTML += `<textarea id="f_MaLaunch_URL">${vstrExeCallUrl}</textarea>`;
    document.getElementById("Pbody").append(textElem);
  }
  window.f_MaLaunch = window.f_MaLaunch_

  window.setInterval(() => {
    window.f_MaLaunch = window.f_MaLaunch_ ;
    try { window.top.document.getElementById("iframeMaLaunchPrtDlg").remove() } catch (e) {}
  }, 1)
} catch (e) { console.log('IROS Macro PoC Err:', e) }
"""

### Code Injection before page load based on CDP as Page Evaluation
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': injectCode})

print("\n\n====== IROS Macro PoC ======")
print('1. Loading IROS Main Page and waiting for #Lwrap div to appear...\n   (for Cookies&Auth, can be skipped on prod env. Timeout: 60s)\n   (on prod env, this part should be implemented with auth&input etc.)')

driver.get("http://www.iros.go.kr/PMainJ.jsp")

try:
  element = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "Lwrap")))

  print('2. Print Test Page Loading...')
  driver.get("http://www.iros.go.kr/frontservlet?cmd=RPRTViewRegisterC&isCallTestPrint=UnIsu")

  print('2-1. Waiting for Print Page to load...\n     (Timeout: 60s)')
  element = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "f_MaLaunch_URL")))
  launchCode = element.get_attribute('value')

  print('2-2. launchCode extracted!\n     ' + launchCode)
  print('3. Starting Print Application...\n   (by URL Scheme + webbrowser module)')
  
  ### Open Printer Application by URL Scheme
  webbrowser.open_new(launchCode)
  ### Subprocess based call example
  # url = launchCode.replace('rprtregisterxctrl://?', 'rprtregisterxctrl:///?')
  # subprocess.call(f'C:\Program Files (x86)\markany\maepscourt\\rprtregisterxctrl.exe "{url}"')

  ### Step 4 - AHK Based Mouse/Keyboard Macro
  print('4. Search & Wait for Printer Selection Dialog...\n   (by Window Title, Timeout: 600s)')
  matchWin = wait(lambda: getWinStrBegin('[대법원 등기 인터넷 서비스] - [인쇄]'), timeout_seconds=600)
  matchWin.move(x=10, y=10, width=480, height=383)
  matchWin.to_top()
  matchWin.always_on_top = True
  matchWin.activate()
  matchWinRect = matchWin.rect

  print('4-1. Searching for Dropdown & Click...\n     (by search/1.dropdown.png, Timeout: 120s)')
  dropdownButton = wait(lambda: ahk.image_search('search/1.dropdown.png'), timeout_seconds=120)
  ahk.mouse_position = (matchWinRect[0] + dropdownButton[0], matchWinRect[1] + dropdownButton[1])
  ahk.click()

  for x in range(10):
    ahk.send_input('{Up}')

  print('4-2. Searching for Compatable Printer & Click...\n     (by search/2.printer.png, Interval: 1s)')
  while True:
    ahk.send_input('{Down}')
    sleep(1)
    matchPrinter = ahk.image_search('search/2.printer.png')
    # Apr 18, 2022 : by indigo : 드랍다운 메뉴 삼성 프린터 이미지 추가
    matchPrinter1 = ahk.image_search('search/2.printer1.png')
    # Apr 18, 2022 : by indigo : 드랍다운 메뉴 삼성 프린터 이미지 추가
    #matchPrinter2 = ahk.image_search('search/2.printer3.png')
    
    if matchPrinter:
      print('   * Matching Printer found!')
      ahk.mouse_position = (matchWinRect[0] + matchPrinter[0] + 5, matchWinRect[1] + matchPrinter[1] + 5)
      ahk.click()
      clear_cache(driver)
      break
    elif matchPrinter1: # Apr 18, 2022 : by indigo : 드랍다운 메뉴 삼성 프린터 이미지 추가
      print('   * Matching Printer found!')
      ahk.mouse_position = (matchWinRect[0] + matchPrinter[0] + 5, matchWinRect[1] + matchPrinter[1] + 5)
      ahk.click()
      clear_cache(driver)
      break
    #elif matchPrinter2: # Apr 18, 2022 : by indigo : 드랍다운 메뉴 삼성 프린터 이미지 추가
      #print('   * Matching Printer found!')
      #ahk.mouse_position = (matchWinRect[0] + matchPrinter[0] + 5, matchWinRect[1] + matchPrinter[1] + 5)
      #ahk.click()
      #break

  
      
  
  print('4-3. Clicking Print Button...\n     (by search/3.print.png)')
  printButton = ahk.image_search('search/3.print.png')
  ahk.mouse_position = (matchWinRect[0] + printButton[0] + 5, matchWinRect[1] + printButton[1] + 5)
  ahk.click()

  print('4-4. Waiting for print job to finish...\n     (by search/4.close.png, Timeout: 120s)')
  sleep(1)
  closeButton = wait(lambda: ahk.image_search('search/4.close.png'), timeout_seconds=120)

  print('5. Killing finished Print Application...\n   (by os.system & taskkill)')
  os.system("taskkill /im rprtregisterxctrl.xgd")
  os.system("taskkill /im RPRTRegisterXCtrl.exe")
finally:
  print('6. Closing ChromeDriver instance...')
  driver.quit()





