#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# get_timetable.py: 東海道新幹線の時刻表HTMLを取得して時刻表を作成する
# Copyright (C) N.Togashi 2021-2023
# JR各駅の時刻表：https://railway.jr-central.co.jp/time-schedule/search/index.html
# JR個別列車案内：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti05.html
# JR個別列車案内(こだま)：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti07.html?traintype=2&train=723
# JR個別列車案内(ひかり)：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti07.html?traintype=1&train=511
# JR個別列車案内(のぞみ)：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti07.html?traintype=6&train=31
# JRアクセス検索：https://railway.jr-central.co.jp/timetable/nr_doc/search.html
# JR到着列車案内：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti09.html
# JR列車走行位置：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti08.html
# JR三島駅下り：https://railway.jr-central.co.jp/cgi-bin/timetable/tokainr.cgi?MODE=7&HOUR=0&DIAF=%bb%b0%c5%e7&DIAR=%c5%ec%b3%a4%c6%bb%a1%a6%bb%b3%cd%db%bf%b7%b4%b4%c0%fe&DIAD=1
# JR三島駅上り：https://railway.jr-central.co.jp/cgi-bin/timetable/tokainr.cgi?MODE=7&HOUR=0&DIAF=%bb%b0%c5%e7&DIAR=%c5%ec%b3%a4%c6%bb%a1%a6%bb%b3%cd%db%bf%b7%b4%b4%c0%fe&DIAD=2
# ドクターイエロー：https://oyaji-photo.club/dy/
# requestsで取得できないWebページをスクレイピングする方法：
#               https://gammasoft.jp/blog/how-to-download-web-page-created-javascript/
# Pythonでかんたんスクレイピング （JavaScript・Proxy・Cookie対応版）：
#               https://qiita.com/_akisato/items/2daafdbc3de544cf6c92
# requests-html 0.10.0：https://pypi.org/project/requests-html/
#   How to fix pyppeteer pyppeteer.errors.BrowserError: Browser closed unexpectedly:
#               https://techoverflow.net/2020/09/29/how-to-fix-pyppeteer-pyppeteer-errors-browsererror-browser-closed-unexpectedly/
#   sudo pip3 install requests-html
#   sudo apt install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget
# Ubuntu 18.04でのみ動作（Python3.6のみ動作）

import os
import sys
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import jpholiday
import re
import csv
import json
import shutil
import urllib.parse
import requests
import codecs
from bs4 import BeautifulSoup
from logging import getLogger, handlers, FileHandler, StreamHandler, Formatter, INFO, DEBUG

# 定数
STATION_DIAGRAM_URL = 'https://railway.jr-central.co.jp/cgi-bin/timetable/tokainr.cgi'
TRAIN_DIAGRAM_URL = 'https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti07.html'
TRAIN_COMMON_JSON = 'https://traininfo.jr-central.co.jp/shinkansen/common/data/common_ja.json'
TRAIN_DIAGRAM_JSON = 'https://traininfo.jr-central.co.jp/shinkansen/var/train_info/train_info_%s_%s.json'
DIAGRAM_ROUTE = '東海道・山陽新幹線'
TRAIN_TYPES = {'こだま': '2', 'ひかり': '1', 'のぞみ': '6'}
STATIONS = [
    '東京', '品川', '新横浜', '小田原', '熱海', '三島', '新富士','静岡', '掛川',
    '浜松', '豊橋', '三河安城', '名古屋', '岐阜羽島', '米原', '京都', '新大阪'
]
STATIONS_ID = {i:STATIONS[i] for i in range(len(STATIONS))}
WEBAPI_SLEEP_TIME = 30

# クラス定義
class Timetable:

    def __init__(self, start, end, cache_dir='./cache', cache_timetable=False):
        """
        コンストラクタ
        :param start: str型、開始日、例：'20210901'
        :param end: str型、終了日（有効期限）、例：'20210930'
        :cache_dir: str型、キャッシュディレクトリパス
        :cache_timetable: bool型、True=各列車毎の時刻表をキャッシュする、False=キャッシュしない
        :return: なし
        """
        logger = getLogger(__name__)
        # パラメタチェック
        if start is None or type(start) is not str or len(start) != 8 or str(int(start)) != start:
            raise Exception('start parameter is invalid, ' + str(start))
        if end is None or type(end) is not str or len(end) != 8 or str(int(end)) != end:
            raise Exception('end parameter is invalid, ' + str(end))
        if start > end:
            raise Exception('start parameter is big from end paramter, ' + str(start) + ' ' + str(end))
        if cache_dir is None or type(cache_dir) is not str or len(cache_dir) == 0:
            raise Exception('cache_dir parameter is invalid, ' + str(cache_dir))
        if type(cache_timetable) is not bool:
            raise Exception('cache_timetable parameter is invalid. ' + str(cache_timetable))
        # 実行
        self.start = start
        self.end = end
        self.cache_dir = cache_dir
        self.cache_timetable = cache_timetable
        self.today = datetime.now().strftime('%Y%m%d')
        self.start_date = datetime.strptime(self.start, '%Y%m%d')
        self.end_date = datetime.strptime(self.end, '%Y%m%d')
        self.months = []
        dt = self.start_date.replace(day=1)
        while dt < self.end_date:
            self.months.append(str(dt.year) + ('0'+str(dt.month))[-2:])
            dt = dt + relativedelta(months=1)
        self.__DIAGRAM_ROUTE_ENCODE = urllib.parse.quote(DIAGRAM_ROUTE, encoding='euc_jp').lower()
        self.__request_headers = {
                # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                # 'Access-Control-Allow-Origin': '*'
        }
        self.__proxies = {
                # 'http':  'https://43.128.18.61:8080',
                # 'https': 'https://43.128.18.61:8080'
        }
        self.__requests_retry_max = 5
        self.__requests_retry_seconds = WEBAPI_SLEEP_TIME
        self.__diagram_common = {}
        self.__cleared_date = '00000000'    # YYYYMMDD

    def __del__(self):
        """
        デストラクタ
        :return: なし
        """
        logger = getLogger(__name__)
        pass

    def initialize(self):
        """
        準備を行う。
        :return: int型、0=正常終了
        """
        logger = getLogger(__name__)
        logger.info('initialize() start.')
        rc = 0
        # キャッシュディレクトリの存在確認
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            msg = 'maked cache directory: ' + self.cache_dir
            logger.info(msg)
            print('INFO:' + msg, file=sys.stderr)
        # 実行日が時刻表の開始日以降でキャッシュが未削除なら削除する
        cleared_date = None
        for file_name in os.listdir(self.cache_dir):
            if file_name[:8] == 'cleared_':
                cleared_date = file_name[8:]
                break
        if cleared_date is None \
        or cleared_date < self.start:
            cleared_date = self.today
            cleared_file = os.path.join(self.cache_dir, 'cleared_' + self.today)
            if not os.path.exists(cleared_file):
                for file_name in os.listdir(self.cache_dir):
                    if file_name[0] == '.':
                        continue
                    if (file_name[-5:] == '.json' or file_name[-5:] == '.html') \
                    and (file_name[:3] == 'up_' or file_name[:5] == 'down_' or file_name[:10] == 'timetable_'):
                        file_path = os.path.join(self.cache_dir, file_name)
                        if datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y%m%d') >= self.start:
                            continue
                        if '_回送9' in file_name:
                            continue
                    if (file_name[-8:] == '_up.html' or file_name[-10:] == '_down.html') \
                    and file_name.split('_')[1] >= self.start:
                        continue
                    os.remove(os.path.join(self.cache_dir, file_name))
                with open(cleared_file, 'w') as fh:
                    fh.write('')
            msg = 'cleared in cache directory: ' + self.cache_dir
            logger.info(msg)
            print('INFO:' + msg, file=sys.stderr)
        if cleared_date is not None:
            self.__cleared_date = cleared_date
        logger.info('initialize() ended.')
        # 復帰
        return rc

    def get_stations_timetable(self):
        """
        JR時刻表サービスから各駅の時刻表を取得する。
        :return: dict型、駅毎の時刻表HTML
        """
        logger = getLogger(__name__)
        logger.info('get_stations_timetable() start.')
        stations_timetable = {}
        station_i = 0
        for station in STATIONS:
            station_i += 1
            msg = '各駅の時刻表取得：' + station  + '  ' + str(station_i) + '/' + str(len(STATIONS))
            logger.info(msg)
            print('INFO:' + msg, file=sys.stderr)
            station_encode = urllib.parse.quote(station, encoding='euc_jp').lower()
            # 各駅の下りの出発時刻
            file_name = os.path.join(self.cache_dir, station + '_' + self.today + '_down.html')
            if os.path.exists(file_name) \
            and os.path.getsize(file_name) > 0:
                with open(file_name, 'r') as t_h:
                    stations_timetable[station+'_down'] = t_h.read()
                logger.debug('used cache: ' + file_name)
            else:
                get_url = '%s?MODE=7&HOUR=0&DIAF=%s&DIAR=%s&DIAD=%s' \
                            % (STATION_DIAGRAM_URL,
                               station_encode,
                               self.__DIAGRAM_ROUTE_ENCODE,
                               '1')
                logger.debug('下りURL：' + get_url)
                content = self.http_get_content(get_url)
                if content is not None:
                    stations_timetable[station+'_down'] = content.decode('euc_jp')
                    with open(file_name, 'w') as t_h:
                        t_h.write(stations_timetable[station+'_down'])
                        logger.debug('write cache: ' + file_name)
                time.sleep(WEBAPI_SLEEP_TIME)
            # 各駅の上りの出発時刻
            if station == '東京':
                continue
            file_name = os.path.join(self.cache_dir, station + '_' + self.today + '_up.html')
            if os.path.exists(file_name) \
            and os.path.getsize(file_name) > 0:
                with open(file_name, 'r') as t_h:
                    stations_timetable[station+'_up'] = t_h.read()
                    logger.debug('used cache: ' + file_name)
            else:
                get_url = '%s?MODE=7&HOUR=0&DIAF=%s&DIAR=%s&DIAD=%s' \
                            % (STATION_DIAGRAM_URL,
                               station_encode,
                               self.__DIAGRAM_ROUTE_ENCODE,
                               '2')
                logger.debug('上りURL：' + get_url)
                content = self.http_get_content(get_url)
                if content is not None:
                    stations_timetable[station+'_up'] = content.decode('euc_jp')
                    with open(file_name, 'w') as t_h:
                        t_h.write(stations_timetable[station+'_up'])
                        logger.debug('write cache: ' + file_name)
                if station_i < len(STATIONS):
                    time.sleep(WEBAPI_SLEEP_TIME)

        logger.info('stations_timetable keys: ' \
                + str(sorted(list(stations_timetable.keys()))))
        logger.info('get_stations_timetable() ended.')
        # 復帰
        return stations_timetable

    def get_trains_list(self, stations_timetable):
        """
        駅毎の時刻表HTMLから列車一覧を作成する。
        :param stations_timetable: dict型、駅毎の時刻表HTML
        :return: dict型、列車一覧、例：{'こだま723号': 'down', ... }
        """
        logger = getLogger(__name__)
        logger.info('get_trains_list() start.')
        trains = {}
        file_name = os.path.join(self.cache_dir, 'trains.json')
        if os.path.exists(file_name):
            with open(file_name, 'r') as fh:
                trains = json.loads(fh.read())
            logger.debug('read cache: ' + file_name)

        for key in stations_timetable.keys():
            msg = '駅の時刻表から列車名取得：' + key
            logger.info(msg)
            print('INFO:' + msg, file=sys.stderr)
            st_way = key.split('_')
            stations_timetable[key] = stations_timetable[key].replace('</TD><TR>', '</TD></TR><TR>')
            stations_timetable[key] = stations_timetable[key].replace('</TD></TABLE>', '</TD></TR></TABLE>')
            soup = BeautifulSoup(stations_timetable[key], "lxml")
            try:
                station = soup.find('body').find_all('table')[1].find('font').text.strip()
            except:
                key_array = key.split('_')
                html_file = os.path.join(self.cache_dir, key_array[0] + '_' + self.today + '_' + key_array[1] + '.html')
                os.rename(html_file, html_file + '.error')
                raise Exception('駅の時刻表の内容に誤りがあります。'+ html_file + '.error')
            td_trains = soup.find_all(class_=re.compile('V'))
            for td_train in td_trains:
                train = td_train.find('table').find_all('td')
                train = [t.text for t in train]
                if train[0][:3] in TRAIN_TYPES:
                    trains[train[0]] = st_way[1]
                    logger.debug(key + '：' + ', '.join(train))

        with open(file_name, 'w') as fh:
            fh.write(json.dumps(trains, ensure_ascii=False, sort_keys=True))
            logger.debug('write cache: ' + file_name)

        logger.info('trains keys:' + str(sorted(list(trains.keys()))))
        logger.info('get_trains_list() ended.')
        # 復帰
        return trains

    def get_trains_timetable(self, trains, remarks, get_json=True):
        """
        列車一覧から列車毎の時刻表を取得する。
        :param trains: dict型、列車一覧、例：{'こだま723号': 'down', ... }
        :param remarks: dict型、特記事項、例：{'こだま802号': {'updown': 'up', '事項': '土曜・休日運休', '運転日': [], '運休日': [,,,]}}
        :param get_json: bool型、True=JSON形式で取得する、False=HTML形式で取得する
        :return: dict型、列車毎の時刻表
        """
        logger = getLogger(__name__)
        logger.info('get_trains_timetable() start.')
        if get_json:
            # 定義情報を取得する
            timestamp = str(datetime.now().timestamp())
            timestamp = timestamp[:timestamp.index('.')+4].replace('.', '')
            file_name = os.path.join(self.cache_dir, 'common_ja.json')
            if os.path.exists(file_name) \
            and os.path.getsize(file_name) > 0:
                with open(file_name, 'r') as t_h:
                    self.__diagram_common = json.loads(t_h.read())
            else:
                url_get = TRAIN_COMMON_JSON + '?timestamp=%s' \
                            % (timestamp)
                common = self.http_get_content(url_get)
                common = codecs.decode(common, 'utf-8-sig')
                with open(file_name, 'w') as t_h:
                    t_h.write(common)
                self.__diagram_common = json.loads(common)

        trains_timetable = {}
        train_i = 0
        for train in trains.keys():
            train_i += 1
            msg = '各列車の時刻表取得：' + train  + '  ' + str(train_i) + '/' + str(len(trains))
            logger.info(msg)
            print('INFO:' + msg, file=sys.stderr, end='')
            if train[:3] not in TRAIN_TYPES or train[:2] == '回送':
                logger.warning('対象外車種？：' + train)
                print(' 対象外車種？', file=sys.stderr)
                continue
            trains_timetable[train] = ''
            train_type = TRAIN_TYPES[train[:3]]
            train_no = train.split('.')[0][3:-1]
            if get_json:
                file_name = os.path.join(self.cache_dir, trains[train]+'_'+train+'.json')
            else:
                file_name = os.path.join(self.cache_dir, trains[train]+'_'+train+'.html')
            if os.path.exists(file_name) \
            and os.path.getsize(file_name) > 0:
                with open(file_name, 'r') as t_h:
                    trains_timetable[train] = t_h.read()
            if not os.path.exists(file_name) \
            or os.path.getsize(file_name) == 0 \
            or datetime.fromtimestamp(os.path.getmtime(file_name)).strftime('%Y%m%d') < self.__cleared_date:
                if train in remarks:
                    if '事項' in remarks[train]:
                        if '◆' in remarks[train]['事項'][0]:
                            if '運転日' in remarks[train] and len(remarks[train]['運転日']) > 0:
                                if self.today not in remarks[train]['運転日']:
                                    print(' 運転日以外', file=sys.stderr)
                                    continue
                            if '運休日' in remarks[train] and len(remarks[train]['運休日']) > 0:
                                if self.today in remarks[train]['運休日']:
                                    print(' 運休日', file=sys.stderr)
                                    continue
                if get_json:
                    print(' JSONデータ取得中...', file=sys.stderr, end='')
                    get_url = TRAIN_DIAGRAM_JSON \
                                % (train_type, train_no) \
                            + '?timestamp=%s' \
                                % (timestamp)
                    logger.debug('列車URL：' + get_url)
                    content = self.http_get_content(get_url)
                    trains_timetable[train] = content.decode('utf-8')
                    if trains_timetable[train][0] != '{':
                        logger.warning('取得したデータがJSON形式以外です。' + train + ':' + trains_timetable[train][:15])
                        del trains_timetable[train]
                        print(' 失敗', file=sys.stderr)
                        continue
                else:
                    print(' HTMLデータ取得中...', file=sys.stderr, end='')
                    get_url = '%s?traintype=%s&train=%s' \
                                % (TRAIN_DIAGRAM_URL, train_type, train_no)
                    logger.debug('列車URL：' + get_url)
                    content = self.http_get_content(get_url, script=True)
                    trains_timetable[train] = content.decode('utf-8')

                with open(file_name, 'w') as t_h:
                    t_h.write(trains_timetable[train])
                if train_i < len(trains):
                    time.sleep(WEBAPI_SLEEP_TIME)

            print(' 完了', file=sys.stderr)

        logger.info('trains_timetable keys:' + str(sorted(list(trains_timetable.keys()))))
        logger.info('get_trains_timetable() ended.')
        # 復帰
        return trains_timetable

    def get_remarks_file(self, remarks_file):
        """
        時刻表の特記事項を読み込む。
        :param remarks_file: str型、時刻表の特記事項を記載したCSVファイル、例：時刻表_210901_0930_記事.csv
                                    内容例：こだま802,up,◆,土曜・休日運休
        :return: dict型、特記事項、例：{'こだま802号': {'updown': 'up', '事項': '土曜・休日運休', '運転日': [], '運休日': [,,,]}}
        """
        logger = getLogger(__name__)
        logger.info('get_remarks_file() start.')
        print('INFO:時刻表の特記事項を読み込み開始', file=sys.stderr)
        remarks = {}
        if remarks_file is None:
            return remarks
        remarks_csv = []
        with open(remarks_file, 'r') as rfh:
            rfh_csv = csv.reader(rfh)
            for rec in rfh_csv:
                rec = [r.strip() for r in rec]
                if rec[0] == '期間':
                    continue
                remarks_csv.append(rec)
        for rec in remarks_csv:
            train = rec[0]+'号'
            if train in remarks:
                # msg = '列車が二重に定義されています。マージして下さい。' + rec[0]
                # logger.warning(msg)
                # print('WARNING:' + msg, file=sys.stderr)
                # 列車名の後に「.1」等の追番を付加する
                if type(remarks[train]) == dict:
                    remarks[train + '.1'] = remarks[train]
                    remarks[train] = 2
                else:
                    remarks[train] += 1
                train += '.' + str(remarks[train])
            remarks[train] = {'updown': rec[1], '事項': '', '運転日': [], '運休日': []}
            if '◆' in rec[2]:
                if remarks[train]['事項'] != '':
                    # 現在は許されない：行先が異なる同一列車は解釈不能
                    remarks[train]['事項'] = rec[2] + rec[3] + '\n' + remarks[train]['事項']
                else:
                    remarks[train]['事項'] = rec[2] + rec[3]
                rem = rec[3]
                rem_result = self.interpret_remark(train, rem, self.start, self.end, self.months)
                remarks[train]['運転日'] = rem_result['運転日']
                remarks[train]['運休日'] = rem_result['運休日']
            elif '☆' in rec[2]:
                if remarks[train]['事項'] != '':
                    remarks[train]['事項'] += '\n'
                remarks[train]['事項'] += rec[2] + rec[3]

        print('INFO:時刻表の特記事項を読み込み終了', file=sys.stderr)
        logger.info('remarks keys: ' + str(sorted(list(remarks.keys()))))
        logger.debug('remarks: ' + str(remarks))
        logger.info('get_remarks_file() ended.')
        # 復帰
        return remarks

    def interpret_remark(self, train, rem, start, end, months):
        """
        １つの事項を変換する。
        :param rem: str型、事項
        :return: dict型、{'運転日': [], '運休日': []}
        """
        logger = getLogger(__name__)
        logger.info('interpret_remark() start, rem=' + str(rem))
        result = {'運転日': [], '運休日': []}
        rem_year = start[:4]
        rem_month = start[4:6]
        rem = rem.replace('[', '').replace(']', '')
        rem = rem.split('　')[0]
        rems = rem.split('・但し、')
        if len(rems) > 1:
            rem = rems[1]
        logger.debug(train + ': ' + rem)
        if rem[-2:] == '運転':
            dates = []
            match = re.search(r'^([0-9]+)月(.+)は?運転$', rem)
            if match is not None:
                new_month = ('0'+match.group(1))[-2:]
                if int(new_month, base=10) < int(rem_month, base=10):
                    rem_year = str(int(rem_year)+1)
                rem_month = new_month
                dates.extend(self.rem_to_dates(rem_year, rem_month, match.group(2)))
            if len(dates) > 0:
                result['運転日'] = sorted(list(set(dates)))
        rem = rems[0]
        logger.debug(train + ': ' + rem)
        rem_year = start[:4]
        rem_month = start[4:6]
        if rem[-2:] == '運休':
            dates = []
            rem_array = rem.split('と')
            for rem1 in rem_array:
                match = re.search(r'^([0-9]+)月(.+)は?運休$', rem1)
                if match is not None:
                    new_month = ('0'+match.group(1))[-2:]
                    if int(new_month, base=10) < int(rem_month, base=10):
                        rem_year = str(int(rem_year)+1)
                    rem_month = new_month
                    dates.extend(self.rem_to_dates(rem_year, rem_month, match.group(2)))
                else:
                    if rem1 == '土曜' or rem1 == '土曜運休' or rem1 == '土曜・休日運休':    # 土曜日
                        for yyyymm in months:
                            dt = datetime.strptime(yyyymm+'01', '%Y%m%d')
                            (weekday1, days) = calendar.monthrange(dt.year, dt.month)
                            saturday = [yyyymm+('0'+str(d))[-2:] for d in range(1, days+1) if ((weekday1+d-1)%7) == 5]
                            saturday = [d for d in saturday if d >= self.start and d <= self.end]
                            dates.extend(saturday)
                    if rem1 == '休日' or rem1 == '休日運休' or rem1 == '土曜・休日運休':    # 日曜日
                        for yyyymm in months:
                            dt = datetime.strptime(yyyymm+'01', '%Y%m%d')
                            (weekday1, days) = calendar.monthrange(dt.year, dt.month)
                            sunday = [yyyymm+('0'+str(d))[-2:] for d in range(1, days+1) if ((weekday1+d-1)%7) == 6]
                            sunday = [d for d in sunday if d >= self.start and d <= self.end]
                            dates.extend(sunday)
                    if rem1 == '休日' or rem1 == '休日運休' or rem1 == '土曜・休日運休':    # 祝日
                        for yyyymm in months:
                            dt = datetime.strptime(yyyymm+'01', '%Y%m%d')
                            (weekday1, days) = calendar.monthrange(dt.year, dt.month)
                            for d in range(1, days+1):
                                dt = yyyymm+('0'+str(d))[-2:]
                                if dt < self.start or dt > self.end:
                                    continue
                                dt = datetime.strptime(dt, '%Y%m%d')
                                if jpholiday.is_holiday(dt):
                                    dates.append(yyyymm+('0'+str(d))[-2:])
            if len(dates) > 0:
                result['運休日'] = [d for d in sorted(list(set(dates))) if d <= end]
        # 「・但し、」の処理
        if len(rems) > 1:
            if rems[0][-2:] == '運休':
                for dt in result['運転日']:
                    if dt in result['運休日']:
                        result['運休日'].remove(dt)
                result['運転日'] = []
            elif rems[0][-2:] == '運転':
                for dt in result['運休日']:
                    if dt in result['運転日']:
                        result['運転日'].remove(dt)
                result['運休日'] = []
        # 復帰
        logger.info('interpret_remark() ended, result=' + str(result))
        return result

    def rem_to_dates(self, year, month, rem):
        """
        特記事項の日付指定を配列の全日付に変換する。
        :param year: str型、4桁の開始年
        :param month: str型、2桁の開始月
        :param rem: str型、特記事項の日付指定。但し、最初の月指定は無い。
        :return: array型、全日付をstr型8文字の年月日の配列で返却する。
        """
        logger = getLogger(__name__)
        logger.debug('rem_to_dates() start, year='+year+', month='+month+', rem='+rem)
        dates = []
        rem_year = year
        rem_month = month
        rem_array = re.split('[・、]', rem)
        for dt in rem_array:
            dt = dt.rstrip('日は')
            dt_array = dt.split('～')
            m_index = dt_array[0].find('月')
            if m_index >= 0:
                new_month = ('0'+dt_array[0][:m_index])[-2:]
                if int(new_month, base=10) < int(rem_month, base=10):
                    rem_year = str(int(rem_year)+1)
                rem_month = new_month
                dt_array[0] = dt_array[0][m_index+1:]
            if len(dt_array) == 1:
                dates.append(rem_year+rem_month+('0'+str(dt_array[0]))[-2:])
            else:
                dt_array[0] = dt_array[0].rstrip('日')
                m2_index = dt_array[1].find('月')
                if m2_index < 0:
                    dates.extend([rem_year+rem_month+('0'+str(d))[-2:] \
                        for d in range(int(dt_array[0]), int(dt_array[1])+1)])
                else:
                    dt1 = int(dt_array[0], base=10)
                    dt2_year = int(rem_year)
                    dt2_month = int(('0'+dt_array[1][:m2_index])[-2:], base=10)
                    dt2 = int(dt_array[1][m2_index+1:], base=10)
                    if dt2_month < int(rem_month, base=10):
                        dt2_year += 1
                    y = int(rem_year, base=10)
                    m = int(rem_month, base=10)
                    while(y!=dt2_year or m!=dt2_month):
                        md = (datetime(y, m, 1) \
                           + relativedelta(months=+1,day=1,days=-1)).day
                        dates.extend([str(y)+('0'+str(m))[-2:]+('0'+str(d))[-2:] \
                            for d in range(dt1, md+1)])
                        dt1 = 1
                        m += 1
                        if m > 12:
                            m = 1
                            y += 1
                    else:
                        md = dt2
                        dates.extend([str(y)+('0'+str(m))[-2:]+('0'+str(d))[-2:] \
                            for d in range(dt1, md+1)])
                        rem_year = str(y)
                        rem_month = ('0'+str(m))[-2:]
        # 復帰
        logger.debug('rem_to_dates() ended, dates='+str(dates))
        return dates

    def append_trains_from_remarks(self, trains, remarks):
        """
        時刻表に特記事項がある列車を列車一覧に追加する
        :param trains: dict型、列車一覧、例：{'こだま723号': 'down', ... }
        :param remarks: dict型、特記事項、例：{'こだま802号': {'updown': 'up', '事項': '土曜・休日運休', '運転日': [], '運休日': [,,,]}}
        """
        logger = getLogger(__name__)
        logger.info('append_trains_from_remarks() start.')
        print('INFO:時刻表の特記事項から列車名を追加', file=sys.stderr)
        trains_append = []
        for train in remarks.keys():
            if type(remarks[train]) != dict:
                if train in trains:
                    del trains[train]
                continue
            if train not in trains:
                trains[train] = remarks[train]['updown']
                trains_append.append(train + '(' + remarks[train]['updown'] + ')')

        logger.info('特記事項からの追加列車：' + str(trains_append))
        logger.info('append_trains_from_remarks() ended.')
        # 復帰
        return trains

    def make_timetable_from_json(self, trains, trains_timetable, remarks):
        """
        列車毎の時刻表JSONから各列車の時刻表を作成する。
        :param trains: dict型、列車一覧、例：{'こだま723号': 'down', ... }
        :param trains_timetable: dict型、列車毎の時刻表
        :param remarks: dict型、特記事項、例：{'こだま802号': {'updown': 'up', '事項': '土曜・休日運休', '運転日': [], '運休日': [,,,]}}
        :return: dict型、各列車の時刻表
        """
        logger = getLogger(__name__)
        logger.info('make_timetable_from_json() start.')
        timetables_down = {
            'property': ['down', int(self.start), int(self.end), int(self.today)], # up/down, 開始日, 終了日, 更新日
                                                        # '列車名': timetable
        }
        timetables_up = {
            'property': ['up', int(self.start), int(self.end), int(self.today)],   # up/down, 開始日, 終了日, 更新日
                                                        # '列車名': timetable
        }
        stations_name = self.__diagram_common['constant']['station']
        stations_id = {k:STATIONS.index(v) for k,v in stations_name.items() if v in STATIONS}
        train_i = 0
        for train in trains.keys():
            train_i += 1
            msg = '各列車の時刻表解析：' + train  + '  ' + str(train_i) + '/' + str(len(trains))
            logger.info(msg)
            print('INFO:' + msg, file=sys.stderr)
            train_file = os.path.join(self.cache_dir, 'timetable_'+trains[train]+'_'+train+'.json')
            get_file = os.path.join(self.cache_dir, trains[train]+'_'+train+'.json')
            if train not in trains_timetable or not os.path.exists(get_file):
                if os.path.exists(train_file):
                    with open(train_file, 'r') as fh:
                        timetable = json.loads(fh.read())
                    if train in remarks:
                        timetable['remarks'] = remarks[train]
                    if trains[train] == 'down':
                        timetables_down[train] = timetable  # 下り
                    else:
                        timetables_up[train] = timetable    # 上り
                continue
            train_json = json.loads(trains_timetable[train])

            # or train_json['suspensionInfoIsEnabled'] == True \ 
            if train_json == {} \
            or 'suspensionInfoIsEnabled' not in train_json \
            or 'trainInfo' not in train_json \
            or 'trains' not in train_json['trainInfo'] \
            or type(train_json['trainInfo']['trains']) is not list \
            or len(train_json['trainInfo']['trains']) != 1 \
            or 'startingStation' not in train_json['trainInfo']['trains'][0] \
            or 'terminalStation' not in train_json['trainInfo']['trains'][0] \
            or 'stations' not in train_json['trainInfo']['trains'][0] \
            or type(train_json['trainInfo']['trains'][0]['stations']) is not list \
            or len(train_json['trainInfo']['trains'][0]['stations']) <= 1:
                os.rename(get_file, get_file + '.error')
                rem = ''
                if train in remarks:
                    rem = remarks[train]['事項']
                logger.error('JSONの形式が異常？：' + train + ', 事項=' + rem + '、' + get_file + '.error')
                continue
            stations = train_json['trainInfo']['trains'][0]['stations']
            if stations[0]['station'] == '15' and train_json['trainInfo']['bound'] == '2':
                # 新大阪発(最終駅)の下りは除く
                continue
            train_start = train_json['trainInfo']['trains'][0]['startingStation']
            train_term = train_json['trainInfo']['trains'][0]['terminalStation']
            timetable = {
                'property': [               # up/down, 入線時刻, 退線時刻, 始発駅, 終着駅
                        trains[train],
                        self.minutes2HM(train_start['time'] - 5),
                        self.minutes2HM(train_term['time']),
                        stations_name[train_start['station']],
                        stations_name[train_term['station']]
                ],
                'remarks': {'事項': '', '運転日': [], '運休日': []},
                'timeLine': []              # [[駅ID, 到着時刻, 出発時刻], ...]
            }
            if remarks != None and train in remarks:
                timetable['remarks'] = remarks[train]
                if 'updown' in timetable['remarks']:
                    del timetable['remarks']['updown']
            for st_i in range(len(stations)):
                if stations_name[stations[st_i]['station']] not in STATIONS:
                    continue
                if stations[st_i]['arrivalTime'] is None:
                    continue
                arrival_time = stations[st_i]['arrivalTime']
                if arrival_time == 0:
                    arrival_time = stations[st_i]['departureTime'] - 5
                arrival_time = self.minutes2HM(arrival_time)
                departure_time = stations[st_i]['departureTime']
                if departure_time == 0:
                    departure_time = stations[st_i]['arrivalTime'] + 5
                departure_time = self.minutes2HM(departure_time)
                # 時刻表に追加する
                table = [stations_id[stations[st_i]['station']],
                         arrival_time,
                         departure_time,
                         0]
                timetable['timeLine'].append(table)
            timetable['property'][1] = timetable['timeLine'][0][1]  # 入線時刻
            timetable['property'][2] = timetable['timeLine'][-1][2] # 退線時刻
            if self.cache_timetable:
                with open(train_file, 'w') as fh:
                    wlen = fh.write(json.dumps(timetable, ensure_ascii=False, sort_keys=True))
            if trains[train] == 'down':
                timetables_down[train] = timetable  # 下り
            else:
                timetables_up[train] = timetable    # 上り
        # 下りと上りを１つにする
        timetables = {'down': timetables_down, 'up': timetables_up}

        logger.info('make_timetable_from_json() ended.')
        # 復帰
        return timetables

    def make_timetable_from_html(self, trains, trains_timetable, remarks):
        """
        列車毎の時刻表HTMLから各列車の時刻表を作成する。
        :param trains: dict型、列車一覧、例：{'こだま723号': 'down', ... }
        :param trains_timetable: dict型、列車毎の時刻表
        :param remarks: dict型、特記事項、例：{'こだま802号': {'updown': 'up', '事項': '土曜・休日運休', '運転日': [], '運休日': [,,,]}}
        :return: dict型、各列車の時刻表
        """
        logger = getLogger(__name__)
        logger.info('make_timetable_from_html() start.')
        timetables_down = {
            'property': ['down', int(self.start), int(self.end), int(self.today)], # up/down, 開始日, 終了日, 更新日
                                                        # '列車名': timetable
        }
        timetables_up = {
            'property': ['up', int(self.start), int(self.end), int(self.today)],   # up/down, 開始日, 終了日, 更新日
                                                        # '列車名': timetable
        }
        train_i = 0
        for train in trains.keys():
            train_i += 1
            msg = '各列車の時刻表解析：' + train  + '  ' + str(train_i) + '/' + str(len(trains))
            logger.info(msg)
            print('INFO:' + msg, file=sys.stderr)
            train_file = os.path.join(self.cache_dir, 'timetable_'+trains[train]+'_'+train+'.json')
            get_file = os.path.join(self.cache_dir, trains[train]+'_'+train+'.html')
            if train not in trains_timetable or not os.path.exists(get_file):
                if os.path.exists(train_file):
                    with open(train_file, 'r') as fh:
                        timetable = json.loads(fh.read())
                    if trains[train] == 'down':
                        timetables_down[train] = timetable  # 下り
                    else:
                        timetables_up[train] = timetable    # 上り
                continue
            soup = BeautifulSoup(trains_timetable[train], "lxml")
            contents_body = soup.find(class_=re.compile('contents-body'))
            if contents_body is None:
                os.rename(get_file, get_file + '.error')
                rem = ''
                if train in remarks:
                    rem = remarks[train]['事項']
                logger.error('時刻表HTMLにcontents-body無し？：' + train + ', 事項=' + rem + '、' + get_file + '.error')
                continue
            info_area = contents_body.find(class_=re.compile('info-area'))
            if info_area is None:
                os.rename(get_file, get_file + '.error')
                rem = ''
                if train in remarks:
                    rem = remarks[train]['事項']
                logger.error('時刻表HTMLにinfo_area無し？：' + train + ', 事項=' + rem + '、' + get_file + '.error')
                continue
            info_area = info_area.find_all('div')
            train_name = info_area[0].text.replace('<br>', '')
            if train_name == '':
                os.rename(get_file, get_file + '.error')
                rem = ''
                if train in remarks:
                    rem = remarks[train]['事項']
                logger.error('列車の運行日以外？：' + train + ', 事項=' + rem + '、' + get_file + '.error')
                continue
            train_start = info_area[1].contents
            if train_start[2] == STATIONS[-1] and trains[train] == 'down':
                # 新大阪発(最終駅)の下りは除く
                continue
            train_term = info_area[3].contents
            timetable = {
                'property': [               # up/down, 入線時刻, 退線時刻, 始発駅, 終着駅
                        trains[train],
                        train_start[0],
                        train_term[0],
                        train_start[2],
                        train_term[2]
                ],
                'remarks': {'事項': '', '運転日': [], '運休日': []},
                'timeLine': []              # [[駅ID, 到着時刻, 出発時刻], ...]
            }
            if remarks != None and train in remarks:
                timetable['remarks'] = remarks[train]
                if 'updown' in timetable['remarks']:
                    del timetable['remarks']['updown']
            main_table = contents_body.find(class_=re.compile('main-table')).find_all('tr')
            table = [0, '00:00', '00:00', 0]
            for tr_i in range(len(main_table)):
                attrs = main_table[tr_i].attrs['class']
                td_table = main_table[tr_i].find_all('td')
                if 'passing' in attrs:
                    continue
                if 'start' in attrs:
                    # 始発駅
                    if td_table[2].text not in STATIONS:
                        continue
                    table = [STATIONS.index(td_table[2].text),
                             self.minusTime(td_table[3].text, '00:05'),
                             self.plusTime(td_table[3].text, '00:00'),
                             0]
                elif 'end' in attrs:
                    # 終着駅
                    if td_table[2].text not in STATIONS:
                        continue
                    table = [STATIONS.index(td_table[2].text),
                             self.plusTime(td_table[3].text, '00:00'),
                             self.plusTime(td_table[3].text, '00:05'),
                             0]
                elif 'stop' in attrs or 'stopped' in attrs:
                    # 到着時刻
                    if td_table[2].text not in STATIONS:
                        continue
                    table = [STATIONS.index(td_table[2].text),
                             self.plusTime(td_table[3].text, '00:00'),
                             self.plusTime(td_table[3].text, '00:05'),
                             0]
                elif 'bottom'in attrs:
                    # 発車時刻
                    if table[1] == '00:00':
                        continue
                    if len(td_table) >= 3 and td_table[2].text != '':
                        table[2] = self.plusTime(td_table[2].text, '00:00')
                elif 'top'in attrs:
                    # topのみは通過？
                    pass
                else:
                    logger.error('時刻の属性が想定外：' + str(attrs))
                if 'bottom' in attrs or 'end' in attrs:
                    # 時刻表に追加する
                    if table != [0, '00:00', '00:00', 0]:
                        timetable['timeLine'].append(table)
                        table = [0, '00:00', '00:00', 0]
            timetable['property'][1] = timetable['timeLine'][0][1]  # 入線時刻
            timetable['property'][2] = timetable['timeLine'][-1][2] # 退線時刻
            if self.cache_timetable:
                with open(train_file, 'w') as fh:
                    wlen = fh.write(json.dumps(timetable, ensure_ascii=False, sort_keys=True))
            if trains[train] == 'down':
                timetables_down[train] = timetable  # 下り
            else:
                timetables_up[train] = timetable    # 上り
        # 下りと上りを１つにする
        timetables = {'down': timetables_down, 'up': timetables_up}

        logger.info('make_timetable_from_html() ended.')
        # 復帰
        return timetables

    def write_timetable(self, timetables, output_dir='./output', file=None, files_max=31):
        """
        dict型、各列車の時刻表をファイルに出力する。
        :param timetables: dict型、各列車の時刻表
        :param output_dir: str型、出力ディレクトリ、省略時：'.'
        :param file: str型、出力ファイル名、省略時：'timetables_YYYYMMDD.json'
        :param max: int型、最大出力ファイル数、0=上限無し、1以上=最大数を超えた場合はファイル名の古い方から削除する
        :return: str型、出力ファイルパス
        """
        logger = getLogger(__name__)
        logger.info('write_timetable() start.')
        rc = 0
        file_name = file
        if file_name is None:
            file_name = 'timetables_' + self.today + '.json'
        file_name = os.path.join(output_dir, file_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info('maked output_dir: ' + output_dir)
        tt_json_str = json.dumps(timetables, ensure_ascii=False, sort_keys=True)
        # 列車毎に改行する
        tt_json_str = re.sub(r'("(こだま|ひかり|のぞみ|回送)[0-9]+号\.?[0-9]*"\:)', r'\n\1', tt_json_str)
        tt_json_str = re.sub(r'("(down|up)"\: )', r'\n\1', tt_json_str)
        wlen = 0
        with open(file_name, 'w') as fh:
            wlen = fh.write(tt_json_str)
        if wlen != len(tt_json_str):
            raise Exception('ファイルの書き込みに失敗しました。' + file_name)
        if files_max > 0:
            file_list = os.listdir(output_dir)
            if len(file_list) > files_max:
                file_list = sorted(file_list, reverse=True)[files_max:]
                for file in file_list:
                    remove_file = os.path.join(output_dir, file)
                    os.remove(remove_file)
                    logger.info('deleted oldest file: ' + remove_file)

        logger.info('write_timetable() ended, rc=' + str(rc) + ', output=' + file_name)
        print('INFO:時刻表を書き込みました。' + file_name, file=sys.stderr)
        return file_name

    def http_get_content(self, url, script=False):
        """
        HTTP GETで指定URLの資源を取得する。
        :param url: str型、取得する資源のURL
        :param script: bool型、True=JavaScriptを使用する、False=JavaScriptを使用しない
        :param headers: dict型、リクエストヘッダーに追加するヘッダーを指定する
        :param proxies: dict型、Proxyを使用する場合に指定する
        :return: str型、取得したコンテンツ、失敗した場合はNoneを返却する
        """
        logger = getLogger(__name__)
        logger.debug('http_get_content() start.')
        content = None
        if script:
            if 'HTMLSession' not in globals():
                from requests_html import HTMLSession
            session = HTMLSession()
            for try_i in range(self.__requests_retry_max):
                try_ok = False
                try:
                    res = session.get(url, headers=self.__request_headers, proxies=self.__proxies)
                    res.html.render()
                except requests.exceptions.ProxyError as e:
                    logger.exception(e)
                    res = None
                    if (try_i+1) < self.__requests_retry_max:
                        time.sleep(self.__requests_retry_seconds)
                if try_ok:
                    break
            if res is None or res.status_code != requests.codes.ok:
                logger.error('requests error(1): ' + str(res))
            else:
                logger.debug('response.encoding: ' + str(res.encoding))
                content = res.html.html
            if res is not None:
                res.close()
            session.close()
        else:
            for try_i in range(self.__requests_retry_max):
                try_ok = False
                try:
                    res = requests.get(url, headers=self.__request_headers, proxies=self.__proxies)
                    try_ok = True
                except requests.exceptions.ProxyError as e:
                    logger.exception(e)
                    res = None
                    if (try_i+1) < self.__requests_retry_max:
                        time.sleep(self.__requests_retry_seconds)
                if try_ok:
                    break
            if res is None or res.status_code != requests.codes.ok:
                logger.error('requests error(2): ' + str(res))
            else:
                logger.debug('response.encoding: ' + str(res.encoding))
                content = res.content
            if res is not None:
                res.close()

        # 復帰
        logger.debug('http_get_content() ended.')
        return content

    def minutes2HM(self, m):
        """
        00:00からの経過分数を時分文字列('12:34')に変換する。
        :param m: int型、00:00からの経過分数
        :return: str型、時分文字列('12:34')
        """
        if type(m) is not int or m < 0 or m >= 1440:
            return None
        return ('0' + str(int(m / 60)))[-2:] \
             + ':' \
             + ('0' + str(m % 60))[-2:]

    def plusTime(self, base, diff):
        """
        文字列の時刻と時刻を加算する。
        :param base: str型、加算元時刻、例：'12:34'
        :param diff: str型、加算時刻、例：'00:01'
        :return: str型、加算結果時刻、例：'12:35'
        """
        diff_hm = diff.split(':')
        rc = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rc = rc[:11] + base + rc[16:]
        rc = datetime.strptime(rc, '%Y-%m-%d %H:%M:%S')
        if diff_hm[0] != '00' or diff_hm[0] != '0':
            rc += timedelta(hours=int(diff_hm[0]))
        if diff_hm[1] != '00' or diff_hm[1] != '0':
            rc += timedelta(minutes=int(diff_hm[1]))
        if len(diff_hm) > 2:
            if diff_hm[2] != '00' or diff_hm[2] != '0':
                rc += timedelta(seconds=int(diff_hm[2]))
        return ('0'+str(rc.hour))[-2:] + ':' + ('0'+str(rc.minute))[-2:]

    def minusTime(self, base, diff):
        """
        文字列の時刻から時刻を減算する。
        :param base: str型、加算元時刻、例：'12:34'
        :param diff: str型、加算時刻、例：'00:01'
        :return: str型、加算結果時刻、例：'12:33'
        """
        diff_hm = diff.split(':')
        rc = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rc = rc[:11] + base + rc[16:]
        rc = datetime.strptime(rc, '%Y-%m-%d %H:%M:%S')
        if diff_hm[0] != '00' or diff_hm[0] != '0':
            rc -= timedelta(hours=int(diff_hm[0]))
        if diff_hm[1] != '00' or diff_hm[1] != '0':
            rc -= timedelta(minutes=int(diff_hm[1]))
        if len(diff_hm) > 2:
            if diff_hm[2] != '00' or diff_hm[2] != '0':
                rc -= timedelta(seconds=int(diff_hm[2]))
        return ('0'+str(rc.hour))[-2:] + ':' + ('0'+str(rc.minute))[-2:]

# 関数定義
def get_remarks_info(remarks_file, remarks_dir=os.path.join('.', 'remarks')):
    """
    時刻表の記事ファイルと開始日と終了日を取得する。
    :param remarks_file: str型、時刻表の記事ファイル名、None=省略時は実行日を含む記事ファイルを探す
    :return: dict型、{'path': 'ファイルパス', 'start_date': '開始日', 'end_date': '終了日'}、日=YYYYMMDD
    """
    logger = getLogger(__name__)
    logger.info('get_remarks_info() start.')
    if remarks_file is None \
    or type(remarks_file) is not str \
    or remarks_file == '':
        remarks_file = None
    if remarks_dir is None \
    or type(remarks_dir) is not str \
    or remarks_dir == '':
        remarks_dir = os.path.join('.', 'remarks')
    remarks_path = None
    start_date = None
    end_date = None
    today = datetime.now()
    now_date = int(today.strftime('%Y%m%d'))
    if remarks_file is None:
        # 実行日を含む記事ファイルを探す
        for file_name in sorted(os.listdir(remarks_dir), reverse=True):
            if file_name[-4:] != '.csv':
                continue
            logger.debug('file_name:' + file_name)
            period = None
            file_path = os.path.join(remarks_dir, file_name)
            with open(file_path, 'r') as fh:
                csv_file = csv.reader(fh)
                period = next(csv_file)
                logger.debug('period:' + str(period))
            if period is not None and period[0] == '期間':
                if int(period[1]) <= now_date \
                and now_date <= int(period[2]):
                    remarks_path = file_path
                    start_date = period[1]
                    end_date = period[2]
                    break
        if remarks_path is None:
            msg = '時刻表の特記事項ファイルが見付かりません。'
            logger.warning(msg)
            print('WARN:' + msg, file=sys.stderr)
    else:
        # 指定された記事ファイルを読み込む
        file_path = remarks_file
        if remarks_file[0] != '.' and remarks_file[0] != '/':
            file_path = os.path.join(remarks_dir, remarks_file)
        period = None
        with open(file_path, 'r') as fh:
            csv_file = csv.reader(fh)
            period = next(csv_file)
            logger.debug('period:' + str(period))
        if period is not None and period[0] == '期間':
            # if int(period[1]) <= now_date \
            # and now_date <= int(period[2]):
            remarks_path = file_path
            start_date = period[1]
            end_date = period[2]
        if remarks_path is None:
            msg = '時刻表の特記事項ファイルが存在しません。' + file_path
            logger.warning(msg)
            print('WARN:' + msg, file=sys.stderr)
    # 復帰値を設定
    if start_date is None:
        start_date = today.replace(day=1).strftime('%Y%m%d')
        end_date = (today.replace(day=1) + relativedelta(months=1, days=-1)).strftime('%Y%m%d')
        msg = '省略時の開始日と終了日を採用しました。' + start_date + ',' + end_date
        logger.warning(msg)
        print('WARN:' + msg, file=sys.stderr)
    res = {
        'path': remarks_path,
        'start_date': start_date,
        'end_date': end_date
    }
    # 復帰
    logger.info('get_remarks_info() ended.')
    logger.debug('res:' + str(res))
    return res

def setup_logger(name, level, log_file='get_timetable.log', log_dir='log'):
    """
    ログ初期化
    :param name: str型、関数、__main__
    :param level: int型、INFO、DEBUG、...
    :param log_file: str型/stderr、ログファイル名またはstderr
    :param log_dir: str型、ログディレクトリ名、log_fileがログファイル名の場合に有効なパラメタ
    :return: logger
    """
    logger = getLogger(name)
    logger.parent.setLevel(level)
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_handler_format = Formatter(log_format)
    if type(log_file) is str:
        # ファイル出力ハンドラ
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        # log_file_handler = FileHandler(os.path.join(log_dir, log_file))
        log_file_handler= handlers.RotatingFileHandler(os.path.join(log_dir, log_file), maxBytes=1024000, backupCount=5)
        log_file_handler.setLevel(level)
        log_file_handler.setFormatter(log_handler_format)
        logger.addHandler(log_file_handler)
    else:
        # 標準エラー出力ハンドラ
        log_stream_handler = StreamHandler()
        log_stream_handler.setLevel(level)
        log_stream_handler.setFormatter(log_handler_format)
        logger.addHandler(log_stream_handler)
    return logger

# コマンド呼び出し
if __name__ == '__main__':
    # 初期化
    rc = 0
    logger = setup_logger(__name__, INFO)  # DEBUG

    try:
        # コマンドのパラメタを取得する
        logger.debug('パラメタ取得開始')
        import argparse
        start_date = None
        end_date = None
        p = argparse.ArgumentParser()
        p.add_argument('-r', '--remarks_file', type=str, help='時刻表の記事ファイル名を指定する。')
        p.add_argument('-j', '--get_json', action='store_true', help='JSONデ－タを取得する場合に指定する。省略時はHTMLデータを取得する。')
        p.add_argument('-c', '--cache_timetable', action='store_true', help='各列車毎の時刻表をキャッシュする場合に指定する。省略時はキャッシュしない。')
        p.add_argument('-v', '--verify_remarks', action='store_true', help='時刻表の記事の内容を確かめる。')
        args = p.parse_args(sys.argv[1:])
        if args.remarks_file is not None \
        and not os.path.exists(args.remarks_file):
            msg = '時刻表の特記事項ファイルが存在しません。' + args.remarks_file
            logger.error(msg)
            print('ERR:' + msg, file=sys.stderr)
            rc = 1
            args.remarks_file = None
        remarks_info = get_remarks_info(args.remarks_file)
        try:
            start_date = datetime.strptime(remarks_info['start_date'], '%Y%m%d')
        except:
            msg = '開始日の指定に誤りがあります。' + remarks_info['start_date']
            logger.error(msg)
            print('ERR:' + msg, file=sys.stderr)
            rc = 1
        try:
            end_date = datetime.strptime(remarks_info['end_date'], '%Y%m%d')
        except:
            msg = '終了日の指定に誤りがあります。' + remarks_info['end_date']
            logger.error()
            print('ERR:' + msg, file=sys.stderr)
            rc = 1
        if start_date > end_date:
            msg = '開始日と終了日の指定が矛盾しています。' + remarks_info['start_date'] + ',' + remarks_info['end_date']
            logger.error(msg)
            print('ERR:' + msg, file=sys.stderr)
            rc = 1
        if rc != 0:
            sys.exit(rc)
        msg = 'get_timetable.py start.'
        logger.info(msg)
        print(msg, file=sys.stderr)
        msg = '時刻表の開始日=' + str(remarks_info['start_date']) + '、終了日=' + str(remarks_info['end_date']) + '、記事ファイル=' + str(remarks_info['path'])
        logger.info(msg)
        print(msg, file=sys.stderr)

        # 実行
        ttobj = Timetable(remarks_info['start_date'], remarks_info['end_date'],
                        cache_timetable=args.cache_timetable)
        if args.verify_remarks:
            # 時刻表の記事の内容確認
            rem = ttobj.get_remarks_file(remarks_info['path'])
            for k, v in rem.items():
                print(k, v)
        else:
            # 時刻表作成
            # 準備
            ttobj.initialize()
            # ①各駅の時刻表を取得する
            stt = ttobj.get_stations_timetable()
            # ②列車一覧を作成する
            trl = ttobj.get_trains_list(stt)
            # ③時刻表の特記事項を読み込む
            rem = None
            if args.remarks_file != '':
                rem = ttobj.get_remarks_file(remarks_info['path'])
                # 列車一覧に特記事項の列車を追加する
                trl = ttobj.append_trains_from_remarks(trl, rem)
            # ④列車毎の時刻表を取得する
            trt = ttobj.get_trains_timetable(trl, rem, get_json=args.get_json)
            # ⑤各列車の時刻表を作成する
            if args.get_json:
                tt = ttobj.make_timetable_from_json(trl, trt, rem)
            else:
                tt = ttobj.make_timetable_from_html(trl, trt, rem)
            # ⑥時刻表をファイルに出力する
            output_path = ttobj.write_timetable(tt)
            ttobj = None
            # WebAPIのcacheディレクトリに複写する
            shutil.copy2(output_path,
                         os.path.join('.', 'cache', 'timetables.json'))

    except Exception as e:
        logger.exception(f'{e}')
        rc = 99

    # 終了
    msg = 'get_timetable.py ended, rc=' + str(rc)
    logger.info(msg)
    print(msg, file=sys.stderr)

    # 復帰
    sys.exit(rc)
