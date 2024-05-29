import csv
import sys
import atexit
import time
import asyncio
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


class Initial_mtx:

    def __init__(self):
        self.startMtx = []
        self.file = "XPM_hltv_ranks.csv"

    def openFile(self):
        with open (self.file, encoding='utf-8') as csvFile:
      
            csvMtx = csv.reader(csvFile, delimiter=";")
            self.startMtx.append(list(csvMtx))
            rowMtx = len(self.startMtx[0])
            colMtx = len(self.startMtx[0][0])
            resMtx = [[0 for x in range(colMtx)] for y in range(rowMtx-1)]
            resMtx.insert(0,self.startMtx[0][0])
            return self.startMtx, rowMtx, colMtx, resMtx



class Values:
   
    initial  = Initial_mtx()
    mtxObj = Initial_mtx.openFile(initial)
    rowMtx = int(mtxObj[1])
    colMtx = int(mtxObj[2])
    startMtx = mtxObj[0][0]
    resMtx = mtxObj[3]
    tableId = "15QuoPJ-laB2Cr8hJvWJkEIBNR6KhTVhxKISzzPkcsvg"


class Connection:

    def __init__():
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--headless=new')
        options.add_argument('log-level=3')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--disable-blink-features=AutomationControlled')
        return options
    browser = webdriver.Chrome(options = __init__())
    page_link = "https://hltv-ranking.perch1.me"
    browser.get(page_link)
    browser.implicitly_wait(5)
    print("Initializing...")    


class Filler(Connection, Values):

    def __init__(self):
        self.resMtx = Values.resMtx
        self.browser = Connection.browser
        self.rowMtx = Values.rowMtx
        self.colMtx = Values.colMtx
        self.startMtx = Values.startMtx

    def getElements(self, row, col, xPath, browser):	
        if xPath != "":		
            parseVal  =  browser.find_element(By.XPATH, xPath).text
        else:
            parseVal = ""
        self.resMtx[row][col] = parseVal


    def fillMtx(self):
        self.errCount = 0
        for i in range(1, self.rowMtx):
            for i2 in range(0, self.colMtx):
                xPath = self.startMtx[i][i2]
                try:                 
                    self.getElements(self, i, i2, xPath, self.browser)
                    self.errCount +=1
                except NoSuchElementException:
                    self.errCount - 1
                    print("invalid xPath: ", xPath)
                    self.browser.implicitly_wait(3)


        return self.resMtx, self.errCount


class GsBuild(Values):

    def get_service_sacc():
        creds_json = "GoogleServiseKEY.json"
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
        return build('sheets', 'v4', http=creds_service)

class Handler:
    #curTime = time.strftime("%H:%M:%S")
    def __init__(self, count, curTime):
        self.count = count
        self.curTime = curTime
    def catch(self):
        stArr = []
        tableId = Values.tableId
        if self.count < (Values.rowMtx-1)*Values.colMtx:
            status1 = 'Data update failed'
            status2 = f"LAST UPDATE: {self.curTime}"
            bodyState = {
        'valueInputOption' : 'RAW',
        'data' : [
        {'range' : 'test!K1', 'values' : [["Invalid_xPath"]]}
         ]
        }
            sendToTableState = GsBuild.get_service_sacc().spreadsheets().values().batchUpdate(spreadsheetId=tableId, body=bodyState).execute()
        else:
            status1 = 'Data update succesfull'
            status2 = f"LAST UPDATE: {self.curTime}"
        stArr.append([status1])
        stArr.append([status2])
        return stArr    

def __main__():
    state = []
    tableId = Values.tableId
    state.append(["STARTED"])
    fillRes = Filler.fillMtx(Filler)
    statuses = Handler(fillRes[1], time.strftime("%H:%M:%S"))
    st = statuses.catch()
    state.append(st[0])
    state.append(st[1])
    bodyState = {
        'valueInputOption' : 'RAW',
        'data' : [
         {'range' : 'test!J1', 'values' : state}
         ]
    }
    sendToTableState = GsBuild.get_service_sacc().spreadsheets().values().batchUpdate(spreadsheetId=tableId, body=bodyState).execute()
    body = {
        'valueInputOption' : 'RAW',
        'data' : [
         {'range' : 'test!A1', 'values' : fillRes[0]}
            ]
    }

    sendToTableData = GsBuild.get_service_sacc().spreadsheets().values().batchUpdate(spreadsheetId=tableId, body=body).execute()
    return statuses

def Isexit():
    tableId = Values.tableId
    state = []
    state.append(["STOPED"])
    bodyState = {
        'valueInputOption' : 'RAW',
        'data' : [
         {'range' : 'test!J1', 'values' : state}
         ]
    }
    sendToTableState = GsBuild.get_service_sacc().spreadsheets().values().batchUpdate(spreadsheetId=Values.tableId, body=bodyState).execute()
    Connection.browser.quit()



async def run(interval):
    while True:
        await asyncio.sleep(interval)
        __main__()

loop = asyncio.get_event_loop()
atexit.register(Isexit)
try:
   loop.run_until_complete(run(20))
except (KeyboardInterrupt, SystemExit):
    loop.stop()
    Isexit()
    print("Cancelling")
except WebDriverException as e:
    loop.stop()
    if 'connection refused' in str(e).lower():
        print("operation aborted")
        Isexit()
finally:
    loop.stop()
    print("app was stopped")
    Isexit()
    sys.exit()


  