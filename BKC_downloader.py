import time, re, os, sys
import tkinter as tk
from tkinter import messagebox
import glob
import threading
from collections import defaultdict
try:
  import requests
except ImportError:
  print ("Trying to Install required module: requests\n")
  os.system('py -3 -m pip install requests')
  import requests

try:
  from selenium import webdriver
except ImportError:
  print ("Trying to Install required module: selenium\n")
  os.system('py -3 -m pip install selenium')
  from selenium import webdriver

try:
  from msedge.selenium_tools import Edge, EdgeOptions
except ImportError:
  print ("Trying to Install required module: selenium\n")
  os.system('py -3 -m pip install msedge_selenium_tools')
  from msedge.selenium_tools import Edge, EdgeOptions

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

CurrentPath = os.path.dirname(os.path.abspath(__file__))
DefaultDownloadPath = CurrentPath + '\\BKC_temp'

def saveLoginInfo(account, password):
  with open(CurrentPath + '\\.config', 'w') as f_out:
      f_out.write(account + '\n')
      f_out.write(password + '\n')

def login(WebsiteUrl, browser):
  account = account_entry.get()
  password = password_entry.get()
  try:
    with open(CurrentPath + '\\.config', 'r') as config:
        configData = config.readlines()
    if account != configData[0].strip() or password != configData[1].strip():
      os.remove(CurrentPath + '\\.config')
      saveLoginInfo(account, password)
  except:
    saveLoginInfo(account, password)
  # set wait time 3 sec
  wait = WebDriverWait(browser, 3)
  browser.get(WebsiteUrl)
  #  debug code
  # browser.get('https://www.intel.com/content/www/us/en/secure/design/confidential/software-kits/kit-details.html?kitId=736187&s=Newest')
  # wait for page ready
  time.sleep(3)
  # enter username
  input = wait.until(EC.presence_of_element_located(
      (By.XPATH, '//*[@id="txtUsername"]')))
  input.send_keys(account)
  # enter password
  input = wait.until(EC.presence_of_element_located(
      (By.XPATH, '//*[@id="txtPassword"]')))
  input.send_keys(password)
  # click sumit button
  submit = wait.until(EC.element_to_be_clickable(
      (By.XPATH, '//*[@id="formSubmit"]')))
  submit.click()

def getWebDataAndDownload(browser, DownloadPath):
  # keep getting download pkg name, file name and download link until it success
  while True:
    try:
      browser.find_element_by_xpath("//button[@data-wap_ref='expand-all']").click()
      DownloadPackageElement = browser.find_elements_by_xpath("//div[@class='content-table-list-item content-table-list-item--desktop']")
      if len(DownloadPackageElement) > 0:
        DownloadPackageName = browser.find_element_by_xpath("//div[@class='software-kit-details-content__container__body__data__title']").text.replace(u"*",'').replace("/",'').replace("&amp;",'&').replace(u"\u2122",'')
        if DownloadPackageName != 'Software Kit Details':
          break
    except:
      pass
  label = tk.Label(MessageFrame, text= "There should be " + str(len(DownloadPackageElement)) + " pkg need to be download")
  label.pack()
  # 
  # DownloadPkg => key: Pkg Name, value: [filename, link]
  # 
  DownloadPkg = defaultdict(list)
  for PkgName in DownloadPackageElement:
    ElementText = PkgName.find_elements_by_tag_name("a")
    for index in range(1, len(ElementText)):
      # get BKC name and remove unvalid symbol for folder name
      DownloadPkg[ElementText[0].text.replace(u"*",'').replace("&nbsp;",'').replace("/",'').replace("&amp;",'&').replace(u"\u2122",'')].append([ElementText[index].text, PkgName.find_element_by_link_text(ElementText[index].text).get_attribute("href")])
  Start_download(browser, DownloadPkg, DownloadPath)
  return DownloadPackageName
  # # rename the folder according to the package title
  # os.rename(DownloadPath, CurrentPath + '\\' + DonloadPackageName)

def Start_download(browser, DownloadPkg, DownloadPath):
  # set wait time 3 sec
  wait = WebDriverWait(browser, 3)
  # download file pkg by pkg
  for key, val in DownloadPkg.items():
    for file in val:
      if 'LICENSE AGREEMENT'.lower() in file[0].lower():
        continue
      browser.get(file[1])
  # try to click accept button no matter it has or not
      try:
        submit = wait.until(EC.element_to_be_clickable(
          (By.XPATH, '//*[@id="eula-accept"]')))
        submit.click()
      except:
        pass
    # wait for this pkg download finished
    while True:
      Target = glob.glob(DownloadPath + '\\*.crdownload')
      if len(Target) == 0:
        break
      time.sleep(3)
    time.sleep(1)
    # make pkg folder
    try:
      os.mkdir(DownloadPath + "\\" + key)
    except:
      pass
    # move the related file to pkg folder
    for file in val:
      if 'LICENSE AGREEMENT'.lower() in file[0].lower():
        continue
      if (os.path.isfile(DownloadPath + "\\" + file[0])):
        # try until rename succeess
        while True:
          try:
            os.rename(DownloadPath + "\\" + file[0], DownloadPath + "\\" + key + "\\" + file[0])
            break
          except Exception as e:
            print (e)
            print ("try again")
      else:
        label = tk.Label(MessageFrame, text= file[0] + " in " + key + " is not downloaded")
        label.pack()

def Main():
  if BrowserIndex.get() == 1:
    DriverPath = CurrentPath + '\chromedriver.exe'
    options = webdriver.ChromeOptions()
    RunBrowser = webdriver.Chrome
  elif BrowserIndex.get() == 2:
    DriverPath = CurrentPath + '\msedgedriver.exe'
    options = EdgeOptions()
    options.use_chromium = True
    RunBrowser = Edge
  else:
    messagebox.showwarning("Warning", "Please Select Browser")
    return

  WebsiteUrl = Website_Url_entry.get()
  if WebsiteUrl.find('https://www.intel.com') != -1:
    DownloadPath = DefaultDownloadPath
    while True:
      try:
        os.mkdir(DownloadPath)
        break
      except:
        DownloadPath = DownloadPath + '_'
    # set download path
    prefs = {}
    prefs["profile.default_content_settings.popups"]=0
    prefs["download.default_directory"]= DownloadPath
    prefs["download.prompt_for_download"]= False
    prefs["safebrowsing.enabled"]= True

    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option('excludeSwitches', ["enable-automation", 'enable-logging'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--safebrowsing-disable-download-protection')
    options.add_argument('safebrowsing-disable-extension-blacklist')
    
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36'
    options.add_argument('user-agent={0}'.format(user_agent))

    browser = RunBrowser(options = options, executable_path= DriverPath)
    browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    browser.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                             'Chrome/85.0.4183.102 Safari/537.36'})

    login(WebsiteUrl, browser)
    DownloadPackageName = getWebDataAndDownload(browser, DownloadPath)
    browser.close()
    time.sleep(1)
    while True:
      try:
        os.rename(DownloadPath, CurrentPath + '\\' + DownloadPackageName)
        break
      except Exception as e:
        print (e)
        print ("try again")
  else:
    messagebox.showwarning("Warning", "Please enter the correct websit URL")
  
def LoginInfo():
    try:
      with open(CurrentPath + '\\.config', 'r') as config:
        configData = config.readlines()
        account = configData[0].strip()
        password = configData[1].strip()
        account_entry.insert(0, account)
        password_entry.insert(0, password)
    except:
      pass

def MainThreading():
  x = threading.Thread(target=Main)
  x.start()
  y = threading.Thread(target=StartProcessThreading, args=(x,))
  y.start()

def StartProcessThreading(InputThreading):
    # temporay to disable all button
    Website_Url_button['state'] = 'disabled'

    while InputThreading.is_alive():
      time.sleep(2)
    Website_Url_button['state'] = 'normal'

if __name__ == "__main__":
  window= tk.Tk() 
  window.title('BKC Downloader')
  window.geometry("1000x300")
  window.configure(background='white')

  LoginInfo_fram = tk.Frame(window)
  LoginInfo_fram.pack(pady=10)
  account_label = tk.Label(LoginInfo_fram, text='account :')
  account_label.pack(side=tk.LEFT)
  account_label.configure(background='white')
  account_entry = tk.Entry(LoginInfo_fram, width=30)
  account_entry.pack(side=tk.LEFT)
  password_label = tk.Label(LoginInfo_fram, text='password :')
  password_label.pack(side=tk.LEFT)
  password_label.configure(background='white')
  password_entry = tk.Entry(LoginInfo_fram, width=30, show='*')
  password_entry.pack(side=tk.LEFT)

  Website_Url_fram = tk.Frame(window)
  Website_Url_fram.pack(pady=10)
  Website_Url_label = tk.Label(Website_Url_fram, text='Website URL :')
  Website_Url_label.pack(side=tk.LEFT)
  Website_Url_label.configure(background='white')
  Website_Url_entry = tk.Entry(Website_Url_fram, width=100)
  Website_Url_entry.pack(side=tk.LEFT)

  BrowserIndex = tk.IntVar()
  BroweserSelect1 = tk.Radiobutton(window, text='Chrome', background='white', variable=BrowserIndex, value=1)
  BroweserSelect1.place(x=400, y=80)
  BroweserSelect2 = tk.Radiobutton(window, text='Edge', background='white', variable=BrowserIndex, value=2)
  BroweserSelect2.place(x=600, y=80)

  Website_Url_button = tk.Button (window, text='Go',command=MainThreading)
  Website_Url_button.place(x=500, y=100)

  MessageFrame = tk.LabelFrame(window, text='Error Message')
  MessageFrame.pack(fill = "both", padx=10, pady=50, expand = "yes")

  LoginInfo()
  window.mainloop()