# pdfConverter  
  
# 動作確認環境  
python3.5以上  
Ubuntu18.04  

# 必要なパッケージ
pdfminer
bs4
urllib

# 各プログラムの用途  
## pdfgetter.py  
OMEGA RESULTのウェブサイトから、競技日とセッション()ごとにスタートリストPDFをまるごと取ってくる  
### 各引数  
- arg1: day{n}を入力。大会4日目なら3  
- arg2: sessionを入力。午前競技ならm、午後競技ならe  
### 事前の設定  
プログラム10行目のurlHeaderの大会IDを適切なものに書き換える。OMEGAのリザルトページで取得したい大会のURLを開くと全部似たような感じになっていて、なんとなく大会IDがわかる。  
### PDFの保存場所
カレントディレクトリに対して、./output/pdf/day{n}{session}  
保存先ディレクトリは先に作っておいてください  
- ex) $ mkdir -p ./output/pdf/day{1..6}{e,m}  

## convert.py
PDFからスタートリストに関するテキスト情報を取得してレース映像のリネーム用のファイル名を自動生成する
### 各引数
- arg1: textに変換するpdfのファイルパス
### 事前の設定
ファイル内冒頭に大会名を指定する箇所がある。  
変数: gameName
### 出力
標準出力 + テキストファイル  
テキストファイルは./output/text/以下に出力される。 
出力フォルダは事前に作っておく。ex) $ mkdir ./output/text 
