#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pdf2remarks.py: 時刻表PDFから記事CSVを出力する
# Copyright (C) N.Togashi 2021-2022
# 使用用法：
#   1. JR東海から時刻表PDFをダウンロードする
#      適当なディレクトリに転送する
#   2. 時刻表PDFから記事CSVを出力する
#      コマンド：python3 pdf2remarks.py 時刻表PDFファイルパス
#          出力：復号化PDF：時刻表PDFファイル_decrypted.pdf
#                記事CSV  ：時刻表PDFファイル_remarks.csv
#   3. 記事CSVファイルに復号化PDFファイルの記事を矩形で貼り付ける
#   4. 所定のtimetable/remarks/ディレクトリに格納する
#   5. 記事CSVの動作確認を行う
#        コマンド：python3 src/get_timetable.py -v -r ./remarks/記事CSVファイル
# 動作環境：
#   Ubuntu 18.04の場合：
#     sudo apt install qpdf openjdk-11-jre
#     sudo pip3 install PyPDF2==1.26.0 pdfminer.six==20211012 tabula-py==2.3.0
#   Ubuntu 22.04の場合：
#     sudo apt install qpdf openjdk-11-jre
#     sudo pip3 install PyPDF2 pdfminer.six tabula-py pycryptodome

import os
import sys
import csv
import re
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
from Crypto.Cipher import AES
import io
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import tabula

# PDFが暗号化されている場合は復号する
# PyPDF2を使用
def my_pdf2decrypt(input_pdf):
    print(get_current_time() + ' my_pdf2decrypt() start.', file=sys.stderr)
    output_pdf = input_pdf
    pgnum = None
    with open(input_pdf, 'rb') as f_pdf:
        pdf = PdfReader(f_pdf)
        if pdf.is_encrypted:
            output_pdf = input_pdf[:-4] + '_decrypted.pdf'
            password = ''
            try:
                pdf.decrypt(password)
                output = PdfWriter()
                pgnum = len(pdf.pages)
                for i in range(pgnum):
                    output.add_page(pdf.pages[i])
                output.write(output_pdf) 
                # output.close()
                print(get_current_time() + ' decrypted pdf, ' + input_pdf, file=sys.stderr)
            except NotImplementedError:
                print(get_current_time() + ' start decrypting pdf by qpdf... from ' + input_pdf, file=sys.stderr)
                command = f"qpdf --password='{password}' --decrypt {input_pdf} {output_pdf};"
                os.system(command)
                if not os.path.exists(output_pdf):
                    raise Exception('ERR: error in decrypt by qpdf.')
                print(get_current_time() + ' ended decrypting pdf by qpdf, to ' + output_pdf, file=sys.stderr)
        else:
            pgnum = len(pdf.pages)

    if pgnum is None and output_pdf != input_pdf:
        with open(output_pdf, 'rb') as f_pdf:
            pdf = PdfReader(f_pdf)
            pgnum = len(pdf.pages)
    print('page number = ' + str(pgnum), file=sys.stderr)

    print(get_current_time() + ' my_pdf2decrypt() ended.', file=sys.stderr)
    return output_pdf, pgnum

# pdfをページ毎に分割してpdfを生成する。またそのファイル名をリストで返す
# PyPDF2を使用
def my_pdf_split(input_pdf):
    print(get_current_time() + ' my_pdf_split() start.', file=sys.stderr)
    file_name_list = []
    f2 = None
    with open(input_pdf, 'rb') as f1:
        input = PdfReader(f1)
        if input.is_encrypted:
            password = ''
            try:
                input.decrypt(password)
            except NotImplementedError:
                decrypted_pdf = input_pdf[:-4] + '_decrypted.pdf'
                command = f"qpdf --password='{password}' --decrypt {input_pdf} {decrypted_pdf};"
                os.system(command)
                f2 = open(decrypted_pdf, 'rb')
                input = PdfReader(f2)
        pgnum = len(input.pages)
        for i in range(pgnum):
            file_name = input_pdf[:-4] + '_p' + str(i+1) + ".pdf"
            output = PdfWriter()
            output.add_page(input.pages[i])
            outputfile = open(file_name, 'wb')
            output.write(outputfile) 
            outputfile.close()
            file_name_list.append(file_name)
    if f2 is not None:
        f2.close()
        os.remove(decrypted_pdf)

    print(get_current_time() + ' my_pdf_split() ended.', file=sys.stderr)
    return file_name_list

# PDFから表形式部分をリスト型で抽出する
# tabulaを使用
def my_pdf2data(my_pdf, pages):
    print(get_current_time() + ' my_pdf2data() start.', file=sys.stderr)
    csv_file = my_pdf[:-4] + '.csv'
    csv_data = []
    if os.path.exists(csv_file):
        with open(csv_file, 'r') as f_csv:
            h_csv = csv.reader(f_csv)
            for rec in h_csv:
                if re.search('【【[0123456789]+】】', rec[0]):
                    csv_data.append([])
                else:
                    csv_data[-1].append(rec)
        print(get_current_time() + ' my_pdf2data() ended, data already exists', file=sys.stderr)
        return csv_data

    print('  ' + str(len(pages)) + ':', file=sys.stderr, end='')
    pgcnt = 0
    for page in pages:
        pgcnt += 1
        print(str(pgcnt) + '...', file=sys.stderr, end='')
        csv_data.append([])
        # lattice=Trueでテーブルの軸線でセルを判定
        dfs = tabula.read_pdf(my_pdf, lattice=True, pandas_options={'header': None}, pages=page)

        # PDFの表をちゃんと取得できているか確認
        df = dfs[0]
        for row in range(len(df)):
            # row_data = list(df.iloc[row, ::])
            row_data = []
            for col in range(len(df.columns)):
                col_data = str(df.iloc[row, col])
                if col_data == 'nan':
                    col_data = ''
                elif col_data in ['の\rぞ\rみ', 'ひ\rか\rり', 'こ\rだ\rま']:
                    col_data = col_data.replace('\r', '')
                elif col_data[:7] in ['Nozomi\r', 'Hikari\r', 'Kodama\r']:
                    col_data = col_data[7:]
                row_data.append(col_data)
            csv_data[-1].append(row_data)
            # print(str(row) + '：', file=sys.stderr, end='')
            # print(str(row_data), file=sys.stderr)

        # df.to_csv("PDFの表.csv", index=None)      # CSV
        # df.to_excel("PDFの表.xlsx", index=None)   # Excel
    print('end', file=sys.stderr)

    # print(str(csv_data), file=sys.stderr)
    with open(csv_file, 'w') as f_csv:
        h_csv = csv.writer(f_csv)
        for page_i in range(len(csv_data)):
            h_csv.writerow(['【【'+str(pages[page_i])+'】】'])
            for row in csv_data[page_i]:
                h_csv.writerow(row)

    print(get_current_time() + ' my_pdf2data() ended.', file=sys.stderr)
    return csv_data

# PDFからページ単位にテキストを抽出する
# pdfminerを使用
def my_pdf2txt(my_pdf, pages):
    print(get_current_time() + ' my_pdf2txt() start.', file=sys.stderr)
    txt_file = my_pdf[:-4] + '.txt'
    txt_data = []
    if os.path.exists(txt_file):
        with open(txt_file, 'r') as f_txt:
            for rec in f_txt:
                if re.search('【【[0123456789]+】】', rec):
                    txt_data.append([])
                else:
                    txt_data.append(rec)
        print(get_current_time() + ' my_pdf2txt() ended, text file already exists', file=sys.stderr)
        return txt_data

    with open(my_pdf, 'rb') as f_pdf:
        print('  ' + str(len(pages)) + ':', file=sys.stderr, end='')
        pgcnt = 0
        for page in PDFPage.get_pages(f_pdf):
            pgcnt += 1
            print(str(pgcnt) + '...', file=sys.stderr, end='')
            manager = PDFResourceManager()
            out_string = io.StringIO()
            laparams = LAParams()
            laparams.detect_vertical = True
            with TextConverter(manager, out_string, codec='utf-8', laparams=laparams) as converter:
                interpreter = PDFPageInterpreter(manager, converter)
                interpreter.process_page(page)
            text = out_string.getvalue()
            text = text.replace('\r', '')
            txt_data.append(text)
            out_string.close()
        print('end', file=sys.stderr)

    with open(txt_file, 'w') as h_txt:
        for txt_i in range(len(txt_data)):
            txt = txt_data[txt_i]
            print('【【' + str(pages[txt_i]) + '】】', file=h_txt)
            print(txt, file=h_txt)

    print(get_current_time() + ' my_pdf2txt() ended.', file=sys.stderr)
    return txt_data

# ページ単位のリスト型表データから記事用CSVを出力する
def my_data2remarks(csv_data, span, output_csv):
    print(get_current_time() + ' my_data2remarks() start.', file=sys.stderr)
    train_data = []
    for page in csv_data:
        if page[0][0][0:4] == '下 り ' or page[0][0][0:4] == '上 り ':
            del page[0]
        for i in range(1, len(page[0])):
            # print('page[0][i]='+page[0][i]+'page[1][i]='+page[1][i], file=sys.stderr)
            if page[1][i] == '':
                continue
            train = [page[1][i]+page[2][i], page[0][i]]
            for j in range(3, len(page)):
                if page[j][i] != '':
                    train.extend(page[j][i].split())
            train_data.append(train)
            # print(str(train_data[-1]), file=sys.stderr)
    # print(str(train_data), file=sys.stderr)

    with open(output_csv, 'w') as f_csv:
        h_csv = csv.writer(f_csv)
        h_csv.writerow(['期間'] + span)
        for train in train_data:
            if train[1] != '':
                updown = 'down'
                # print('train[0]='+train[0], file=sys.stderr)
                if int(train[0][3:]) % 2 == 0:
                    updown = 'up'
                h_csv.writerow([train[0], updown, train[1], ''])

    print(get_current_time() + ' my_data2remarks() ended.', file=sys.stderr)
    return

# 時刻表の有効期間を抽出する
def my_get_timetable_span(txt_data):
    print(get_current_time() + ' my_get_timetable_span() start.', file=sys.stderr)
    # １２月１日（水）～１月１０日（月）の運転列車　　Timetable ( December 1st ～ January 10th )
    number = {'０':'0', '１':'1', '２':'2', '３':'3', '４':'4', '５':'5', '６':'6', '７':'7', '８':'8', '９':'9'}
    span_txt = [txt for txt in txt_data if '運転列車' in txt][0]
    match = re.search('([０１２３４５６７８９]+)月([０１２３４５６７８９]+)日（[月火水木金土日]）～([０１２３４５６７８９]+)月([０１２３４５６７８９]+)日（[月火水木金土日]）の運転列車', span_txt)
    if match is None:
        print(span_txt, file=sys.stderr)
        raise Exception('ERR: timetable span not found.')
    start_month = ('0' + ''.join([number[v] for v in list(match.group(1))]))[-2:]
    start_day = ('0' + ''.join([number[v] for v in list(match.group(2))]))[-2:]
    end_month = ('0' + ''.join([number[v] for v in list(match.group(3))]))[-2:]
    end_day = ('0' + ''.join([number[v] for v in list(match.group(4))]))[-2:]
    year = datetime.now().year
    month = datetime.now().month
    start_year = str(year)
    end_year = start_year
    if start_month < ('0'+str(month))[-2:]:
        start_year = str(year+1)
        end_year = str(year+1)
    elif end_month < start_month:
        if end_month >= ('0'+str(month))[-2:]:
            start_year = str(year-1)
        else:
            end_year = str(year+1)
    rc = [start_year+start_month+start_day,
            end_year+end_month+end_day]

    print(get_current_time() + ' my_get_timetable_span() ended, rc=' + str(rc), file=sys.stderr)
    return rc

# 現在時刻を文字列で取得
def get_current_time():
    return datetime.now().strftime('%H:%M:%S')

# 実行
if __name__ == '__main__':
    print(get_current_time() + ' pdf2remarks.py start.', file=sys.stderr)
    input_pdf = sys.argv[1]
    output_csv = input_pdf[:-4] + '_remarks.csv'

    # PDFが暗号化されている場合は復号する
    decrypted_pdf, pgnum = my_pdf2decrypt(input_pdf)
    # PDFからページ単位にテキストを抽出する
    txt_data = my_pdf2txt(decrypted_pdf, list(range(1, pgnum+1)))
    # 時刻表の有効期間を抽出する
    span = my_get_timetable_span(txt_data)
    # PDFからページ単位に表データをリスト型で抽出する
    csv_data = my_pdf2data(decrypted_pdf, list(range(1, pgnum+1)))
    # ページ単位のリスト型表データから記事用CSVを出力する
    my_data2remarks(csv_data, span, output_csv)

    # pdfをページ毎に分割してpdfを生成する。またそのファイル名をリストで返す
    # file_name_list = my_pdf_split(decrypted_pdf)

    # 作業ファイルを削除する
    # if decrypted_pdf != input_pdf:
    #     os.remove(decrypted_pdf)

    # 復帰
    print(get_current_time() + ' pdf2remarks.py ended.', file=sys.stderr)
    sys.exit(0)
