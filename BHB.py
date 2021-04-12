import base64
import requests
import json
from datetime import date
import copy
import boto3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

class BHB: 
    """ Manage the operations on Buchhaltungsbutler """

    __api_base_url = 'https://webapp.buchhaltungsbutler.de/api/v1'
    
    __urls = {
        "get_postings" : "/postings/get",
        "receipts_upload" : "/receipts/upload",
        "add_transactions" : "/transactions/add",
        "edit_debitoor" : "https://webapp.buchhaltungsbutler.de/customer-settings/ajax-edit-customer-creditor-debitor/",
        "susa" : "https://app.buchhaltungsbutler.de/reports/dialog-report-sums",
        "ui_login" : "https://webapp.buchhaltungsbutler.de/index/?from=login"
    }
    

    def __init__(self,secret):
        self.__session = requests.Session()

        self.__username = secret.get("username")
        self.__password = secret.get("password")

        self.__api_client = secret.get("api_client")
        self.__api_secret = secret.get("api_secret")
        self.__api_key = secret.get("api_key")
        self.__StandardBody = {"api_key" : self.__api_key}
        self.__StandardHeader = {"Content-Type" : "application/json"}

        #self.__initSelenium()
        #self.login()

        for key in self.__urls:
            value = self.__urls[key]
            if not("http" in value):
                value = self.__api_base_url + value
                self.__urls[key] = value
    
    def __initSelenium(self):

        args = ['--headless', '--no-sandbox', '--disable-gpu', '--window-size=1280x1696', '--user-data-dir=/tmp/user-data']
        args = args + ['--hide-scrollbars', '--enable-logging', '--log-level=0', '--v=99''--single-process', '--disable-dev-shm-usage']
        args = args + ['--data-path=/tmp/data-path', '--ignore-certificate-errors', '--homedir=/tmp', '--disk-cache-dir=/tmp/cache-dir']
        args = args + ['user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36']
        
        chrome_options = Options()
        for arg in args: chrome_options.add_argument(arg)

        if os.name == "nt":
            path = "C:\\development\\lambda_bhb_sync\\chromedriver.exe"
            self.__seleniumDriver = webdriver.Chrome(path,chrome_options=chrome_options)
        elif os.name == "posix":
            subprocess.run('mkdir /tmp/bin', shell=True)
            os.system("cp ./chromedriver /tmp/bin/chromedriver")
            os.system("cp ./headless-chromium /tmp/bin/headless-chromium")
            os.chmod("/tmp/bin/chromedriver", 0o777)
            os.chmod("/tmp/bin/headless-chromium", 0o777)

            options = webdriver.ChromeOptions()
            options.binary_location = '/tmp/bin/headless-chromium'
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--single-process")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1600x800")
            
            self.__seleniumDriver = webdriver.Chrome(executable_path='/tmp/bin/chromedriver', chrome_options=options)


    def login(self):
        self.__seleniumDriver.get("https://webapp.buchhaltungsbutler.de/login/")
        username = self.__seleniumDriver.find_element_by_name("email")
        password = self.__seleniumDriver.find_element_by_name("password")
        print("\nusername = " + str(username))
        print("password = " + str(password))
        ids = self.__seleniumDriver.find_elements_by_xpath('//*[@id]')

        for i in ids: 
            print("\tid = '"+str(i.id) + "'")
            print("\trect = '"+str(i.rect) + "'")
            print("\ttag_name = '"+str(i.tag_name) + "'")
            print("\taria_role = '" + str(aria_role) + "'")
            print("\ttext = '"+str(i.text) + "'\n")
            
        
        loginButton = self.__seleniumDriver.find_element_by_class_name("pageSection")
        print("loginButton = "+ str(loginButton))
        
        username.send_keys(self.__username)
        password.send_keys(self.__password)
        loginButton.click()

    def get_bookings(self, date_from, date_to):
        url = self.__urls["get_postings"]

        result = []
        iterate = True
        offset = 0
        while iterate: 
            body = {"date_from" : date_from, "date_to" : date_to, "offset" : offset}
            response = self.post(url, body=body, header={})

            if response.status_code == 200:
                response = response.json()
                data = response["data"]
                rowCount = response["rows"]
                if not(rowCount == 1000): iterate = False
                else: offset = offset + 1000
                print("offset = " + str(offset))
                for row in data:  result.append(row)
        return result


    def post(self, url, body, header):        
        StdBody = copy.deepcopy(self.__StandardBody)
        StdHeader = copy.deepcopy(self.__StandardHeader)

        StdBody.update(body)
        StdHeader.update(header)
        return requests.post(url, data=json.dumps(StdBody), headers=StdHeader, auth = (self.__api_client, self.__api_secret))

    def get(self, url, body, header):        
        StdBody = copy.deepcopy(self.__StandardBody)
        StdHeader = copy.deepcopy(self.__StandardHeader)

        StdBody.update(body)
        StdHeader.update(header)
        return requests.get(url, data=json.dumps(StdBody), headers=StdHeader, auth = (self.__api_client, self.__api_secret))


    def add_transaction(self, account, to_from, amount, booking_date, booking_text=""):
        url = self.__urls["add_transactions"]
        payload = {"account" : account, "to_from" : to_from, "amount" : amount, "booking_date": booking_date, "booking_text" : booking_text, "purpose" : booking_text}
        return self.post(url,payload , {})
        

