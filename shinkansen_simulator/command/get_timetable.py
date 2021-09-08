#!/usr/bin/env python3
# get_timetable.py: 東海道新幹線の時刻表HTMLを取得して時刻表を作成する
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
# requestsで取得できないWebページをスクレイピングする方法：
#               https://gammasoft.jp/blog/how-to-download-web-page-created-javascript/
# Pythonでかんたんスクレイピング （JavaScript・Proxy・Cookie対応版）：
#               https://qiita.com/_akisato/items/2daafdbc3de544cf6c92
# requests-html 0.10.0：https://pypi.org/project/requests-html/
# How to fix pyppeteer pyppeteer.errors.BrowserError: Browser closed unexpectedly:
#               https://techoverflow.net/2020/09/29/how-to-fix-pyppeteer-pyppeteer-errors-browsererror-browser-closed-unexpectedly/
# sudo pip3 install requests-html
# sudo apt install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget
# Ubuntu 18.04でのみ動作（Python3.6のみ動作）
# Free Proxy：http://free-proxy.cz/ja/proxylist/country/JP/https/ping/all
#             sudo pip3 install urllib3==1.25.11

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
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from logging import getLogger, FileHandler, StreamHandler, Formatter, INFO, DEBUG

# 定数
STATION_DIAGRAM_URL = 'https://railway.jr-central.co.jp/cgi-bin/timetable/tokainr.cgi'
TRAIN_DIAGRAM_URL = 'https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti07.html'
DIAGRAM_ROUTE = '東海道・山陽新幹線'
TRAIN_TYPES = {'こだま': '2', 'ひかり': '1', 'のぞみ': '6'}
STATIONS = [
    '東京', '品川', '新横浜', '小田原', '熱海', '三島', '新富士','静岡', '掛川',
    '浜松', '豊橋', '三河安城', '名古屋', '岐阜羽島', '米原', '京都', '新大阪'
]
STATIONS_ID = {i:STATIONS[i] for i in range(len(STATIONS))}
WEBAPI_SLEEP_TIME = 30

# クラス定義
class timetable:

    def __init__(self, start, end, cache_dir='./cache'):
        """
        コンストラクタ
        :param start: str型、開始日、例：'20210901'
        :param end: str型、終了日（有効期限）、例：'20210930'
        :cache_dir: str型、キャッシュディレクトリパス
        :return: なし
        """
        logger = getLogger(__name__)
        self.start = start
        self.end = end
        self.cache_dir = cache_dir
        self.today = datetime.now().strftime('%Y%m%d')
        self.start_date = datetime.strptime(self.start, '%Y%m%d')
        self.end_date = datetime.strptime(self.end, '%Y%m%d')
        self.months = []
        dt = self.start_date
        while dt < self.end_date:
            self.months.append(str(dt.year) + ('0'+str(dt.month))[-2:])
            dt = dt + relativedelta(months=1)
        self.__DIAGRAM_ROUTE_ENCODE = urllib.parse.quote(DIAGRAM_ROUTE, encoding='euc_jp').lower()
        self.__request_headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                'Access-Control-Allow-Origin': '*'
        }
        self.__proxies = {
                'http':  'https://43.128.18.61:8080',
                'https': 'https://43.128.18.61:8080'
        }
        self.__requests_retry_max = 5
        self.__requests_retry_seconds = WEBAPI_SLEEP_TIME

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
        """
        logger = getLogger(__name__)
        logger.info('initialize() start.')
        rc = 0
        # キャッシュディレクトリの存在確認
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            logger.info('maked cache directory: ' + self.cache_dir)
        # 今日が1日ならキャッシュを削除する
        if self.today[-2:] == '01':
            for file_name in os.listdir(self.cache_dir):
                os.remove(os.path.join(self.cache_dir, file_name))
            logger.info('cleared in cache directory: ' + self.cache_dir)
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
            logger.info('各駅の時刻表取得：' + station)
            station_i += 1
            station_encode = urllib.parse.quote(station, encoding='euc_jp').lower()
            # 各駅の下りの出発時刻
            file_name = os.path.join(self.cache_dir, station + '_' + self.today + '_down.html')
            if os.path.exists(file_name):
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
                for try_i in range(self.__requests_retry_max):
                    try_ok = False
                    try:
                        res = requests.get(get_url, headers=self.__request_headers, proxies=self.__proxies)
                        try_ok = True
                    except HTTPSConnectionPool as e:
                        time.sleep(self.__requests_retry_seconds)
                    if try_ok:
                        break
                if res.status_code != requests.codes.ok:
                    logger.error('requests error: ' + str(res))
                else:
                    logger.debug('response.encoding: ' + str(res.encoding))
                    stations_timetable[station+'_down'] = res.content.decode('euc_jp')
                    with open(file_name, 'w') as t_h:
                        t_h.write(stations_timetable[station+'_down'])
                        logger.debug('write cache: ' + file_name)
                time.sleep(WEBAPI_SLEEP_TIME)
            # 各駅の上りの出発時刻
            if station == '東京':
                continue
            file_name = os.path.join(self.cache_dir, station + '_' + self.today + '_up.html')
            if os.path.exists(file_name):
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
                for try_i in range(self.__requests_retry_max):
                    try_ok = False
                    try:
                        res = requests.get(get_url, headers=self.__request_headers, proxies=self.__proxies)
                        try_ok = True
                    except HTTPSConnectionPool as e:
                        time.sleep(self.__requests_retry_seconds)
                    if try_ok:
                        break
                if res.status_code != requests.codes.ok:
                    logger.error('requests error: ' + str(res))
                else:
                    logger.debug('response.encoding: ' + str(res.encoding))
                    stations_timetable[station+'_up'] = res.content.decode('euc_jp')
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
            logger.info(key)
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
                trains[train[0]] = st_way[1]
                logger.debug(key + '：' + ', '.join(train))

        with open(file_name, 'w') as fh:
            fh.write(json.dumps(trains, ensure_ascii=False, sort_keys=True))
            logger.debug('write cache: ' + file_name)

        logger.info('trains keys:' + str(sorted(list(trains.keys()))))
        logger.info('get_trains_list() ended.')
        # 復帰
        return trains

    def get_trains_timetable(self, trains):
        """
        列車一覧から列車毎の時刻表を取得する。
        :param trains: dict型、列車一覧、例：{'こだま723号': 'down', ... }
        :return: dict型、列車毎の時刻表
        """
        logger = getLogger(__name__)
        logger.info('get_trains_timetable() start.')
        trains_timetable = {}
        train_i = 0
        for train in trains.keys():
            train_i += 1
            if train[:3] not in TRAIN_TYPES:
                logger.error('対象外車種？：' + train)
                continue
            logger.info(train)
            trains_timetable[train] = ''
            train_type = TRAIN_TYPES[train[:3]]
            train_no = train[3:-1]
            file_name = os.path.join(self.cache_dir, trains[train]+'_'+train+'.html')
            if os.path.exists(file_name):
                with open(file_name, 'r') as t_h:
                    trains_timetable[train] = t_h.read()
            else:
                get_url = '%s?traintype=%s&train=%s' \
                            % (TRAIN_DIAGRAM_URL, train_type, train_no)
                logger.debug('列車URL：' + get_url)
                if True:
                    session = HTMLSession()
                    for try_i in range(self.__requests_retry_max):
                        try_ok = False
                        try:
                            res = session.get(get_url, headers=self.__request_headers, proxies=self.__proxies)
                            res.html.render()
                        except HTTPSConnectionPool as e:
                            time.sleep(self.__requests_retry_seconds)
                        if try_ok:
                            break
                    if res.status_code != requests.codes.ok:
                        logger.error('requests error(1): ' + str(res))
                    else:
                        logger.debug('response.encoding: ' + str(res.encoding))
                        trains_timetable[train] = res.html.html
                    res.close()
                    session.close()
                else:
                    for try_i in range(self.__requests_retry_max):
                        try_ok = False
                        try:
                            res = requests.get(get_url, headers=self.__request_headers, proxies=self.__proxies)
                            try_ok = True
                        except HTTPSConnectionPool as e:
                            time.sleep(self.__requests_retry_seconds)
                        if try_ok:
                            break
                    if res.status_code != requests.codes.ok:
                        logger.error('requests error(2): ' + str(res))
                    else:
                        logger.debug('response.encoding: ' + str(res.encoding))
                        trains_timetable[train] = res.content.decode('utf-8')
                    res.close()
                with open(file_name, 'w') as t_h:
                    t_h.write(trains_timetable[train])
                if train_i < len(trains):
                    time.sleep(WEBAPI_SLEEP_TIME)

        logger.info('trains_timetable keys:' + str(sorted(list(trains_timetable.keys()))))
        logger.info('get_trains_timetable() ended.')
        # 復帰
        return trains_timetable

    def get_remarks_file(self, remarks_file):
        """
        時刻表の特記事項を読み込む。
        :param remarks_file: str型、時刻表の特記事項を記載したCSVファイル、例：時刻表_210901_0930_記事.csv
                                    内容例：◆,こだま802,土曜・休日運休
        :return: dict型、特記事項、例：{'こだま802号': {'updown': 'up', '事項': '土曜・休日運休', '運転日': [], '運休日': [,,,]}}
        """
        logger = getLogger(__name__)
        logger.info('get_remarks_file() start.')
        remarks = {}
        remarks_csv = []
        with open(remarks_file, 'r') as rfh:
            rfh_csv = csv.reader(rfh)
            for rec in rfh_csv:
                remarks_csv.append(rec)
        for rec in remarks_csv:
            train = rec[0]+'号'
            if train not in remarks:
                remarks[train] = {'updown': rec[1], '事項': '', '運転日': [], '運休日': []}
            if rec[2] == '◆':
                if remarks[train]['事項'] != '':
                    remarks[train]['事項'] = rec[2] + rec[3] + '\n' + remarks[train]['事項']
                else:
                    remarks[train]['事項'] = rec[2] + rec[3]
                rem = rec[3]
                rems = rem.split('・但し、')
                if len(rems) > 1:
                    rem = rems[1]
                if rem[-3:] == '日運転' or rem[-4:] == '日は運転':
                    match = re.search(r'^([0-9]+)月([^日]+)日は?運転$', rem)
                    rem_month = ('0'+match.group(1))[-2:]
                    rem_array = match.group(2).split('・')
                    dates = []
                    for dt in rem_array:
                        dt_array = dt.split('～')
                        if len(dt_array) == 1:
                            dates.append(dt)
                        else:
                            dates.extend([str(d) for d in range(int(dt_array[0]), int(dt_array[1])+1)])
                    remarks[train]['運転日'] = [self.start[:4]+rem_month+('0'+d)[-2:] for d in dates]
                rem = rems[0]
                dates = []
                if rem == '土曜運休' or rem == '土曜・休日運休':    # 土曜日
                    for yyyymm in self.months:
                        dt = datetime.strptime(yyyymm+'01', '%Y%m%d')
                        (weekday1, days) = calendar.monthrange(dt.year, dt.month)
                        dates.extend([yyyymm+('0'+str(d))[-2:] for d in range(1, days+1) if ((weekday1+d-1)%7) == 5])
                if rem == '休日運休' or rem == '土曜・休日運休':    # 日曜日
                    for yyyymm in self.months:
                        dt = datetime.strptime(yyyymm+'01', '%Y%m%d')
                        (weekday1, days) = calendar.monthrange(dt.year, dt.month)
                        dates.extend([yyyymm+('0'+str(d))[-2:] for d in range(1, days+1) if ((weekday1+d-1)%7) == 6])
                if rem == '休日運休' or rem == '土曜・休日運休':    # 祝日
                    for yyyymm in self.months:
                        dt = datetime.strptime(yyyymm+'01', '%Y%m%d')
                        (weekday1, days) = calendar.monthrange(dt.year, dt.month)
                        for d in range(1, days+1):
                            dt = datetime.strptime(yyyymm+('0'+str(d))[-2:], '%Y%m%d')
                            if jpholiday.is_holiday(dt):
                                dates.append(yyyymm+('0'+str(d))[-2:])
                if len(dates) > 0:
                    remarks[train]['運休日'] = dates
            elif rec[2] == '☆':
                if remarks[train]['事項'] != '':
                    remarks[train]['事項'] += '\n'
                remarks[train]['事項'] += rec[2] + rec[3]

        logger.info('remarks keys: ' + str(sorted(list(remarks.keys()))))
        logger.info('get_remarks_file() ended.')
        # 復帰
        return remarks

    def append_trains_from_remarks(self, trains, remarks):
        """
        時刻表に特記事項がある列車を列車一覧に追加する
        :param trains: dict型、列車一覧、例：{'こだま723号': 'down', ... }
        :param remarks: dict型、特記事項、例：{'こだま802号': {'updown': 'up', '事項': '土曜・休日運休', '運転日': [], '運休日': [,,,]}}
        """
        logger = getLogger(__name__)
        logger.info('append_trains_from_remarks() start.')
        trains_append = []
        for train in remarks.keys():
            if train not in trains:
                trains[train] = remarks[train]['updown']
                trains_append.append(train + '(' + remarks[train]['updown'] + ')')

        logger.info('特記事項からの追加列車：' + str(trains_append))
        logger.info('append_trains_from_remarks() ended.')
        # 復帰
        return trains

    def make_timetable(self, trains, trains_timetable, remarks):
        """
        列車毎の時刻表から各列車の時刻表を作成する。
        :param trains: dict型、列車一覧、例：{'こだま723号': 'down', ... }
        :param trains_timetable: dict型、列車毎の時刻表
        :param remarks: dict型、特記事項、例：{'こだま802号': {'updown': 'up', '事項': '土曜・休日運休', '運転日': [], '運休日': [,,,]}}
        :return: dict型、各列車の時刻表
        """
        logger = getLogger(__name__)
        logger.info('make_timetable() start.')
        timetables_down = {
            'property': ['down', int(self.start), int(self.end)], # up/down, 開始日, 終了日
                                                        # '列車名': timetable
        }
        timetables_up = {
            'property': ['up', int(self.start), int(self.end)],   # up/down, 開始日, 終了日
                                                        # '列車名': timetable
        }
        for train in trains.keys():
            if train not in trains_timetable:
                continue
            file_name = os.path.join(self.cache_dir, trains[train]+'_'+train+'.html')
            soup = BeautifulSoup(trains_timetable[train], "lxml")
            contents_body = soup.find(class_=re.compile('contents-body'))
            if contents_body is None:
                os.rename(file_name, file_name + '.error')
                logger.error('時刻表HTMLにcontents-body無し？：' + train + '、' + file_name + '.error')
                continue
            info_area = contents_body.find(class_=re.compile('info-area'))
            if info_area is None:
                os.rename(file_name, file_name + '.error')
                logger.error('時刻表HTMLにinfo_area無し？：' + train + '、' + file_name + '.error')
                continue
            info_area = info_area.find_all('div')
            train_name = info_area[0].text.replace('<br>', '')
            if train_name == '':
                os.rename(file_name, file_name + '.error')
                logger.error('列車の運行日以外？：' + train + '、' + file_name + '.error')
                continue
            logger.info(train)
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
                'status': [None, -1, -1],
                'timeLine': []              # [[駅ID, 到着時刻, 出発時刻], ...]
            }
            if remarks != None and train in remarks:
                timetable['remarks'] = remarks[train]
                if 'updown' in timetable['remarks']:
                    del timetable['remarks']['updown']
            main_table = contents_body.find(class_=re.compile('main-table')).find_all('tr')
            table = [0, '00:00', '00:00']
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
                             self.plusTime(td_table[3].text, '00:00')]
                elif 'end' in attrs:
                    # 終着駅
                    if td_table[2].text not in STATIONS:
                        continue
                    table = [STATIONS.index(td_table[2].text),
                             self.plusTime(td_table[3].text, '00:00'),
                             self.plusTime(td_table[3].text, '00:05')]
                elif 'stop' in attrs or 'stopped' in attrs:
                    # 到着時刻
                    if td_table[2].text not in STATIONS:
                        continue
                    table = [STATIONS.index(td_table[2].text),
                             self.plusTime(td_table[3].text, '00:00'),
                             self.plusTime(td_table[3].text, '00:05')]
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
                    if table != [0, '00:00', '00:00']:
                        timetable['timeLine'].append(table)
                        table = [0, '00:00', '00:00']
            timetable['property'][1] = timetable['timeLine'][0][1]  # 入線時刻
            timetable['property'][2] = timetable['timeLine'][-1][2] # 退線時刻
            if trains[train] == 'down':
                # 下り
                timetables_down[train] = timetable
            else:
                # 上り
                timetables_up[train] = timetable
        # 下りと上りを１つにする
        timetables = {'down': timetables_down, 'up': timetables_up}

        logger.info('make_timetable() ended.')
        # 復帰
        return timetables

    def write_timetable(self, timetables, output_dir='./output', file=None, files_max=10):
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
        return file_name

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
def setup_logger_stderr(name, level):
    """
    ログ初期化
    :param name: str型、関数、__main__
    :param level: int型、INFO、DEBUG、...
    :return: logger
    """
    logger = getLogger(name)
    logger.parent.setLevel(level)
    log_stream_handler = StreamHandler()
    log_stream_handler.setLevel(level)
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_handler_format = Formatter(log_format)
    log_stream_handler.setFormatter(log_handler_format)
    logger.addHandler(log_stream_handler)
    return logger

# コマンド呼び出し
if __name__ == '__main__':
    # 初期化
    rc = 0
    logger = setup_logger_stderr(__name__, INFO)

    try:
        # コマンドのパラメタを取得する
        logger.debug('パラメタ取得開始')
        import argparse
        start_date = None
        end_date = None
        p = argparse.ArgumentParser()
        p.add_argument('start_date', type=str, help='開始日：YYYYMMDD形式')
        p.add_argument('end_date', type=str, help='終了日：YYYYMMDD形式')
        p.add_argument('-r', '--remarks_file', type=str, help='時刻表の記事ファイル名')
        args = p.parse_args(sys.argv[1:])
        try:
            start_date = datetime.strptime(args.start_date, '%Y%m%d')
        except:
            logger.error('開始日の指定に誤りがあります。' + args.start_date)
            rc = 1
        try:
            end_date = datetime.strptime(args.end_date, '%Y%m%d')
        except:
            logger.error('終了日の指定に誤りがあります。' + args.end_date)
            sys.exit(1)
        if args.remarks_file is None:
            args.remarks_file = '時刻表_' + args.start_date[2:] + '_' + args.end_date[4:] + '_記事.csv'
        if not os.path.exists(args.remarks_file):
            logger.error('時刻表の特記事項ファイルが存在しません。' + args.remarks_file)
            rc = 1
        if rc != 0:
            sys.exit(rc)
        logger.info('開始日=' + args.start_date + '、終了日=' + args.end_date + '、記事ファイル=' + args.remarks_file)

        # 実行
        ttobj = timetable(args.start_date, args.end_date)
        # 準備
        ttobj.initialize()
        # ①各駅の時刻表を取得する
        stt = ttobj.get_stations_timetable()
        # ②列車一覧を作成する
        trl = ttobj.get_trains_list(stt)
        # ③時刻表の特記事項を読み込む
        rem = None
        if args.remarks_file != '':
            rem = ttobj.get_remarks_file(args.remarks_file)
            # 列車一覧に特記事項の列車を追加する
            trl = ttobj.append_trains_from_remarks(trl, rem)
        # ④列車毎の時刻表を取得する
        trt = ttobj.get_trains_timetable(trl)
        # ⑤各列車の時刻表を作成する
        tt = ttobj.make_timetable(trl, trt, rem)
        # ⑥時刻表をファイルに出力する
        output_path = ttobj.write_timetable(tt)
        ttobj = None
        # WebAPIのcacheディレクトリに複写する
        shutil.copy2(output_path,
                     os.path.join('.', 'cache', 'timetables.json'))

    except Exception as e:
        logger.exception(f'{e}')
        rc = 99

    # 復帰
    sys.exit(rc)
