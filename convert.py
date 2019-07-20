import sys
import os
import re

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTContainer, LTTextBox
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

## edit here!!
gameName = "WorldChamp2019"

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

# 出力用のテキストファイル
filename = os.path.basename(sys.argv[1])
outputfilename = "output/text/" + os.path.splitext(filename)[0] + "_out.txt"

outputfile = open(outputfilename, 'w')
output_txt = ""
prefix = ""
allData = ""
ir = "i"


def print_and_write(txt):
    print(txt)
    #outputfile.write(txt)
#    output_txt.write('\n')
    outputfile.close()

with open(sys.argv[1], 'rb') as f:
    # PDFPage.get_pages()にファイルオブジェクトを指定して、PDFPageオブジェクトを順に取得する。
    # 時間がかかるファイルは、キーワード引数pagenosで処理するページ番号（0始まり）のリストを指定するとよい。
    rank = False
    lanes = []
    thisHeat = ""
    number = 1
    semi = False
    seminumber = 1
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
            if prefix != "":
                if "Heat" in text and "of" in text:
                    if "Slow" in text or "Fast" in text:
                        number = int(text.split(" ")[2])
                    else:
                        number = int(text.split(" ")[1])
                if len(lanes) == 0 and 'Lane' in text:
                    lanes = text.split()
                    numLane = lanes.index('Lane')
                    lanes = lanes[numLane + 1:]
                    # 'Lane' の次から最後までを格納
                elif 'Name' in text or ('NAT' in text and 'code' not in text):
                    if 'BEST' in text:
                        continue
                    names = text.split("\n")
                    # 'Name'の次から最後まで格納
                    names = names[1:]
                    if semi == True:
                        thisHeat = prefix + "_" + str(seminumber) + "_AgeGroup0_["
                        seminumber += 1
                    elif semi == False:
                        thisHeat = prefix + "_" + str(number) + "_AgeGroup0_["
                    if len(lanes) == 0:
                        continue
                    for i in range(len(lanes)):
                        name = names[i]
                        name = name.replace(" - ", "_")
                        name = name.replace(" ", "_")
                        name = name.replace("-", "_")
                        thisHeat += lanes[i] + "#" + name + "-"
                    thisHeat = "CamXX_" + gameName + "_" + thisHeat[:-1] + "].mp4\n"
                    #print(thisHeat)
                    allData += thisHeat
                    rank = False
                    lanes = []
            elif "Men's" in text and "men" not in output_txt:
                if text.count(os.linesep) != 1:
                    text = text.split("\n")[0]
                    
                styles = text.split(" ")
                if "x" in styles[1]:
                    ir = "r"
                output_txt += "Men_" + styles[1] + "_" + style(styles[2].split("\n")[0], ir)
                ir = "i"
            elif "Women's" in text and "women" not in output_txt:
                if text.count(os.linesep) != 1:
                    text = text.split("\n")[0]
                styles = text.split(" ")
                if "x" in styles[1]:
                    ir = "r"
                output_txt += "Women_" + styles[1] + "_" + style(styles[2].split("\n")[0], ir)
                ir = "i"
            elif "Mixed" in text and "mixed" not in output_txt:
                if text.count(os.linesep) != 1:
                    text = text.split("\n")[0]
                styles = text.split(" ")
                if "x" in styles[1]:
                    ir = "r"
                output_txt += "Mixed_" + styles[1] + "_" + style(styles[2].split("\n")[0], ir)
                ir = "i"
            elif "_" in output_txt and\
                    ("Heat" not in output_txt or\
                    "Final" not in output_txt or\
                    "Swim-Off" not in output_txt or\
                    "Semi" not in output_txt):
                output_txt += "_" + text.split("\n")[0]
                prefix = output_txt
                if "Semi" in prefix:
                    semi = True
            #elif "_" in output_txt and "final" not in output_txt:
            #    output_txt += "_Final"
            #    prefix =  output_txt
            if "Reserves" in text:
                break
            if "Rank" in text:
                rank = True

            # print_and_write('-' * 10)  # 読みやすいよう区切り線を表示する。
            # print_and_write(box.get_text().strip())  # テキストボックス内のテキストを表示する。

print_and_write(allData)
