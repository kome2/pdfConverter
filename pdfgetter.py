import urllib.request, urllib.error
import sys
from bs4 import BeautifulSoup
import requests
import os
import multiprocessing
import threading

## edit here!!!
urlHeader = "http://www.omegatiming.com/Competition?id=000112010cffffffffffffffffffffff&day="


def download(url, title):
    print(title, ": downloading!")
    urllib.request.urlretrieve(url, "{0}".format(title))
    print(title, ": success!")

def pdfextract(i, fp):
    style = ""
    prefix = "http://www.omegatiming.com"
    for j in i.find_all(class_="fileTitle"):
        if "Men" in j.string:
            style = "Men_" + j.string.split(" ")[1] + "_" + j.string.split(" ")[2]
        elif "Women" in j.string:
            style = "Women_" + j.string.split(" ")[1] + "_" + j.string.split(" ")[2]
        elif "Mixed" in j.string:
            style = "Mixed_" + j.string.split(" ")[1] + "_" + j.string.split(" ")[2]
        else:
            style += "_" + j.string
    style = fp + style.replace(" ", "_") + ".pdf"
    pdfurl = prefix + i.find(class_="fileName").a.get("href")
    download(pdfurl, style)

if __name__ == "__main__":
    day = sys.argv[1]
    session = sys.argv[2]
    dailyUrl = urlHeader + day
    r = requests.get(dailyUrl)

    soup = BeautifulSoup(r.text, "lxml")
    morning = False
     
    contents = soup.find(id='CompetitionContent')
    index = 1
    evening = False
    styles = []

    for i in contents.find_all_next("div"):
        # if morning
        if session == "m":
            if i.find(class_="SessionSW") != None and morning == False:
                # morning
                morning = True
            elif i.find(class_="SessionSW") == None and morning == True:
                # between morning and evening
                if "fileSW" in str(i):
                    filePrefix = "./output/pdf/day" + day + session + "/" + day + session + "_" + str(index).zfill(2) + "_"
                    styles += [[i, filePrefix]]
                    index += 1
            elif i.find(class_="SessionSW") != None and morning == True:
                # evening
                break
            else:
                # other
                continue
        elif session == "e":
            if i.find(class_="SessionSW") != None and morning == False:
                # morning
                morning = True
            elif i.find(class_="SessionSW") == None and morning == True and evening == False:
                # between morning and evening
                continue
            elif i.find(class_="SessionSW") != None and morning == True:
                # evening
                evening = True
            elif i.find(class_="SessionSW") == None and evening == True and evening == True:
                # evening session
                if "fileSW" in str(i):
                    filePrefix = "./output/pdf/day" + day + session + "/" + day + session + "_" + str(index).zfill(2) + "_"
                    styles += [[i, filePrefix]]
                    index += 1
            else:
                # other
                continue
    
    for st in styles:
        p = threading.Thread(target=pdfextract, args=(st))
        p.start()
