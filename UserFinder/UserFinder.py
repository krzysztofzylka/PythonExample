import urllib
from requests_html import HTMLSession
import sys
import threading
import time

#hidden error for user
class DevNull:
    def write(self, msg):
        pass
sys.stderr = DevNull()

#search with threading
class scanthread(threading.Thread):
    def __init__(self, threadID, name, counter, tc):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.tc = tc
    def run(self):
        if scan.database[self.tc][0] == 'pagetitle':
            while (scan.scanUrlTitleWait == True):
                time.sleep(0.1)
            scan.scanSite(self.tc, scan.login)
        else:
            scan.scanSite(self.tc, scan.login)
        scan.scanend+=1
        scan.thread-=1

#search class
class scan:
    colorList = {
        'red': '\u001b[31m',
        'green': '\u001b[32m',
        'yellow': '\u001b[33m'
    }
    color = 'green'
    status = 'Not Found'
    database = {}
    success = 0
    login = ''
    scanend = 0
    scanUrlTitleWait = False
    maxthread = 8
    thread = 0
    printwait = False
    def __init__(self):
        self.readDatabase()
    def scanAllSite(self, login):
        self.success = 0
        for site in self.database:
            self.scanSite(site, login)
        print("Find: %s/%s" % (self.success, len(self.database)))
    #scan with multi thread
    def scanAllSiteMT(self, login):
        self.login = login
        self.success = 0
        for site in self.database:
            while (self.thread == self.maxthread):
                time.sleep(0.1)
            self.thread+=1
            thread = scanthread(1, "Scanner", 1, site)
            thread.start()
        while (self.scanend < len(self.database)):
            time.sleep(0.1)
    #scan with one thread
    def scanUrlCode(self, url):
        try:
            response = urllib.request.urlopen(url)
            return response.getcode()
        except urllib.error.URLError as e:
            try:
                return e.code
            except:
                return False
    def getGenerateURLTitle(self, url):
        self.scanUrlTitleWait = True
        session = HTMLSession()
        request = session.get(url)
        request.html.arender(8, None, 0.2, False, 0.2)
        searchTitle = request.html.find('title', first=True)
        self.scanUrlTitleWait = False
        try:
            return searchTitle.text
        except:
            return ''
    def scanSite(self, sitename, login):
        try:
            dbarray = self.database[sitename]
        except:
            print(self.colorList['yellow']+'Not found site %s\u001b[0m' % sitename)
            return False
        if dbarray[0] == 'urlcode':
            url = dbarray[2].replace('$login$', login)
            scan = self.scanUrlCode(url)
            self.printInfo(login, dbarray[1], 'green' if scan == 200 else 'red', url)
            if scan == 200:
                self.success+=1
        elif dbarray[0] == 'pagetitle':
            url = dbarray[2].replace('$login$', login)
            getTitle = self.getGenerateURLTitle(url)
            if dbarray[4] == 'reverse':
                self.printInfo(login, dbarray[1], 'red' if getTitle.find(dbarray[3].replace('$login$', login)) != -1 else 'green', url)
                if getTitle.find(dbarray[3].replace('$login$', login)) != -1:
                    self.success+=1
            else:
                self.printInfo(login, dbarray[1], 'green' if getTitle.find(dbarray[3].replace('$login$', login)) != -1 else 'red', url)
                if getTitle.find(dbarray[3].replace('$login$', login)) == -1:
                    self.success+=1
        else:
            print(self.colorList['yellow']+'Not found site type %s\u001b[0m' % dbarray[0])
            return False
    def readDatabase(self):
        print("Read database file... Please wait...")
        with open('database.txt') as f:
            for line in f:
                dbarray = line.strip().split('||')
                self.database[dbarray[1]] = dbarray
        print('Success loading database (%s)' % len(self.database))
    def printInfo(self, login, site, color, url):
        while (self.printwait == True):
            time.sleep(0.01)
        self.printwait = True
        print(self.colorList[color]+'Search %s in %s: %s %s\u001b[0m' % (login, site, 'Not found' if color == 'red' else 'OK', '('+url+')' if color != 'red' else ''))
        self.printwait = False
scan = scan()

#search cmd
print("Enter login or name:")
login = input()
print("Search: %s" % login)
scan.scanAllSiteMT(login)
print("Scanning is complete")
input()