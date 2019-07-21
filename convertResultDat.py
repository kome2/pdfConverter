import sys
import os
import re

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTContainer, LTTextBox
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

sexId = {"Men":1, "Women":2, "Mixed":3}
styleId = {"FreeStyle":1, "BackStroke":2, "BreastStroke":3, "Butterfly":4, "IndividualMedley":5, "FreeRelay":6, "MedleyRelay":7}
distId = {"25m":1, "50m":2, "100m":3, "200m":4, "400m":5, "800m":6, "1500m":7, "300m":8, "75m":9}
yoketsuId = {"Heats":1, "Timedfinal":2, "BFinal":3, "Final":4, "Swim-Off":5, "Semifinal":6}
kikenId = {"complete":0, "DNS":1, "DSQ":2, "DNSInRace":3, "OPEN":4, "DSQ(OPEN)":5, "DNS(OPEN)":6}
dsqSwimmerId = {"complete":0, "1":1, "2":2, "3":3, "4":4}
schoolId = {"toddler":0, "ES":1, "JHS":2, "HS":3, "UNIV":4, "ADULT":5, "KOSEN":6}
months = {"JAN":1, "FEB":2, "MAR":3, "APR":4, "MAY":5, "JUN":6, "JUL":7, "AUG":8, "SEP":9, "OCT":10, "NOV":11, "DEC":12}

def find_textboxes_recursively(layout_obj):
    """
    再帰的にテキストボックス（LTTextBox）を探して、テキストボックスのリストを取得する。
    """
    # LTTextBoxを継承するオブジェクトの場合は1要素のリストを返す。
    if isinstance(layout_obj, LTTextBox):
        return [layout_obj]

    # LTContainerを継承するオブジェクトは子要素を含むので、再帰的に探す。
    if isinstance(layout_obj, LTContainer):
        boxes = []
        for child in layout_obj:
            boxes.extend(find_textboxes_recursively(child))

        return boxes

    return []  # その他の場合は空リストを返す。

def style(str, ir):
    if ir == "i":
        if str == "Freestyle":
            return "FreeStyle"
        elif str == "Backstroke":
            return "BackStroke"
        elif str == "Breaststroke":
            return "BreastStroke"
        elif str == "Individual":
            return "IndividualMedley"
        else:
            return str
    elif ir == "r":
        if str == "Freestyle":
            return "FreeRelay"
        elif str == "Medley":
            return "MedleyRelay"

# Layout Analysisのパラメーターを設定。縦書きの検出を有効にする。
laparams = LAParams(detect_vertical=True)

# 共有のリソースを管理するリソースマネージャーを作成。
resource_manager = PDFResourceManager()

# ページを集めるPageAggregatorオブジェクトを作成。
device = PDFPageAggregator(resource_manager, laparams=laparams)

# Interpreterオブジェクトを作成。
interpreter = PDFPageInterpreter(resource_manager, device)

output_txt = ""
prefix = ""
ir = "i"

with open(sys.argv[1], 'rb') as f:
    # PDFPage.get_pages()にファイルオブジェクトを指定して、PDFPageオブジェクトを順に取得する。
    # 時間がかかるファイルは、キーワード引数pagenosで処理するページ番号（0始まり）のリストを指定するとよい。
    if '4x' in sys.argv[1]:
        print("Cannot use this script for Relay Events")
        print('Input File: ' + sys.argv[1] + "\n")
        exit()

    rank = False
    lanes = []
    number = 1
    semi = False
    teambool = False
    birthbool = False
    births = []
    evDateFlag = False
    evDate = ""

    sexNum = 1
    yoketsuNum = 1
    distNum = 2
    styleNum = 1
    kikenNum = 0
    relayDSQNum = 0
    schoolNum = 5
    heatNum = 1 

    for page in PDFPage.get_pages(f):
        # print_and_write('\n====== ページ区切り ======\n')
        interpreter.process_page(page)  # ページを処理する。
        layout = device.get_result()  # LTPageオブジェクトを取得。

        # ページ内のテキストボックスのリストを取得する。
        boxes = find_textboxes_recursively(layout)

        # テキストボックスの左上の座標の順でテキストボックスをソートする。
        # y1（Y座標の値）は上に行くほど大きくなるので、正負を反転させている。
        boxes.sort(key=lambda b: (-b.y1, b.x0))
        
        for box in boxes:
            text = box.get_text()
            if evDateFlag == False:
                if "Event" in text or "EVENT" in text:
                    evDate = text.split("\n")[1].split(" ")
                    evDate = evDate[2] + "/" + str(months[evDate[1]]).zfill(2) + "/" + evDate[0].zfill(2)
                    evDateFlag = True
                else:
                    continue
            if prefix != "":
                if "Heat" in text and "of" in text:
                    if "Slow" in text or "Fast" in text:
                        # タイム決勝
                        number = int(text.split(" ")[2])
                        heatNum = number
                    else:
                        # 普通の予選
                        number = int(text.split(" ")[1])
                        heatNum = number
                if birthbool == True:
                    births = text.split("\n")
                    if semi == True and heatNum == 1:
                        heatNum += 1
                    for i in range(len(lanes)):
                        birth = births[i].split(" ")
                        if birth[0].isdecimal():
                            birth = birth[2] + "/" + str(months[birth[1]]).zfill(2) + "/" + birth[0].zfill(2)
                        else:
                            birth = ""
                        if names[i] == 'Name':
                            continue
                        print(sexNum, ",", styleNum, ",", distNum, ",", yoketsuNum, ",", heatNum, ",", lanes[i], ",", kikenNum, ",", relayDSQNum, ",,", teams[i], ",", "(swimmer id)", ",", sexNum, ",", names[i], ",", birth, ",,,,,,,,,,,,,", schoolNum, ",", "0", ",", evDate, ",,", "(team id)",",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
                    if yoketsuNum == 6:
                        semi = True
                    birthbool = False
                    lanes = []
                if 'NAT' in text and 'NATO' not in text:
                    teams = text.split("\n")
                    teambool = False
                    birthbool = True
                if len(lanes) == 0 and 'Lane' in text:
                    lanes = text.split()
                elif 'Name' in text:
                    names = text.split("\n")
                    for i in range(len(lanes)):
                        name = names[i]
                        name = name.replace(" - ", "_")
                        name = name.replace(" ", "_")
                        name = name.replace("-", "_")
                        names[i] = name
                    rank = False
                    teambool = True
            elif "Men's" in text and "men" not in output_txt:
                sexNum = sexId["Men"]
                if text.count(os.linesep) != 1:
                    text = text.split("\n")[0]
                    
                styles = text.split(" ")
                if "x" in styles[1]:
                    ir = "r"
                output_txt += "Men_" + styles[1] + "_" + style(styles[2].split("\n")[0], ir)
                distNum = distId[styles[1]]
                styleNum = styleId[style(styles[2].split("\n")[0], ir)]
                ir = "i"
            elif "Women's" in text and "women" not in output_txt:
                sexNum = sexId["Women"]
                if text.count(os.linesep) != 1:
                    text = text.split("\n")[0]
                styles = text.split(" ")
                if "x" in styles[1]:
                    ir = "r"
                output_txt += "Women_" + styles[1] + "_" + style(styles[2].split("\n")[0], ir)
                distNum = distId[styles[1]]
                styleNum = styleId[style(styles[2].split("\n")[0], ir)]
                ir = "i"
            elif "Mixed" in text and "mixed" not in output_txt:
                sexNum = sexId["Mixed"]
                if text.count(os.linesep) != 1:
                    text = text.split("\n")[0]
                styles = text.split(" ")
                if "x" in styles[1]:
                    ir = "r"
                output_txt += "Mixed_" + styles[1] + "_" + style(styles[2].split("\n")[0], ir)
                distNum = distId[styles[1]]
                styleNum = styleId[style(styles[2].split("\n")[0], ir)]
                ir = "i"
            elif "_" in output_txt and\
                    ("Heat" not in output_txt or\
                    "Final" not in output_txt or\
                    "Swim-Off" not in output_txt or\
                    "Semi" not in output_txt):
                output_txt += "_" + text.split("\n")[0]
                prefix = output_txt
                if text.split("\n")[0] == 'Preliminary':
                    yoketsuNum = yoketsuId['Heats']
                else:
                    yoketsuNum = yoketsuId[text.split("\n")[0]]
            if "Reserves" in text:
                break
            if "Rank" in text:
                rank = True
