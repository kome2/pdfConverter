import urllib.request, urllib.error
import sys
from bs4 import BeautifulSoup
import requests
import os
import multiprocessing
import threading

## edit here!!!
gameUrl = "http://www.omegatiming.com/2019/tyr-pro-swim-series-5-clovis-live-results"

def download(url, title):
    # string url: download target url
    # string title: saved file name
    print(title, ": downloading!")
    urllib.request.urlretrieve(url, "{0}".format(title))
    print(title, ": success!")

def pdfextract(fp):
    if len(fp) < 5:
        return
    styleData = fp.find(class_="round").string # Women's Freestyle 800m Final

    urls = fp.find_all(class_="two")
    stUrl = urls[0].a.get("href") # startlist Url
    reUrl = urls[1].a.get("href") # result url
    prefix = "http://www.omegatiming.com"
    stArray = styleData.split(" ")
    if stArray[0] == "Men's":
        stArray[0] = "Men"
    elif stArray[0] == "Women's":
        stArray[0] = "Women"
    fname = stArray[0] + stArray[2] + stArray[1] + stArray[3] + ".pdf"

    download(prefix + stUrl, fname)

if __name__ == "__main__":
    day = sys.argv[1]
    session = sys.argv[2]
    r = requests.get(gameUrl)
    
    soup = BeautifulSoup(r.text, "lxml")
     
    contents = soup.find(class_='results-detail-page')
    dayCount = int(day)

    for div in contents.find_all_next(class_="block-table"):
        # 指定した日付の抽出
        dayCount -= 1
        if dayCount != 0:
            continue

        # 種目ブロックの抽出
        # class = rowごとに種目セットになっている
        for row in div.find_all(class_="row"):
            p = threading.Thread(target=pdfextract, args=([row]))
            p.start()
