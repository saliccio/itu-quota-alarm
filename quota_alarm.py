import mechanize
from bs4 import BeautifulSoup
import time
from notifypy import Notify

courseCode = input("Ders kodu: ").upper()
crn = input("CRN: ")

cachedCRNIndex = -1
cachedCourseName = ""

def init():
    browser = mechanize.Browser()
    browser.open(f"https://www.sis.itu.edu.tr/TR/ogrenci/ders-programi/ders-programi.php?seviye=LS&derskodu={courseCode[:3]}")
    #browser.select_form(nr=0)
    #browser.form["derskodu"] = [courseCode[:3]]
    #browser.submit()

    return browser

browser = init()

def check():
    global cachedCRNIndex

    soupData = BeautifulSoup(browser.response().read(), "lxml")
    coursesTable = soupData.find("table")
    rows = coursesTable("tr")[2:]

    if cachedCRNIndex == -1:
        i = 0
        for row in rows:
            if isSearchedRow(row):
                cachedCRNIndex = i
                
            hasQuota = rowHasQuota(row)
            if hasQuota:
                break
            i += 1
    else:
        hasQuota = rowHasQuota(rows[cachedCRNIndex])

    if hasQuota:
        notification = Notify()
        notification.title = "Boş Kontenjan"
        notification.message = f"{crn} CRN'li '{cachedCourseName}' dersinde boş kontenjan var!"
        notification.send()

        print(f"{crn} CRN'li '{cachedCourseName}' dersinde boş kontenjan var!")

def isSearchedRow(crnRow):    #returns whether the row is the one we are looking for
    rowCRN = crnRow.next.text
    return crn == rowCRN

def rowHasQuota(crnRow):    #returns whether the row has empty quota
    global cachedCourseName

    values = crnRow.find_all("td")
    if isSearchedRow(crnRow):
        try:
            quota = int(values[9].text)
            enrolled = int(values[10].text)
        except:
            return False

        cachedCourseName = values[1].find_next("a").text + "\t " + values[2].text

        return quota > enrolled

    return False

while True:
    check()
    time.sleep(5)