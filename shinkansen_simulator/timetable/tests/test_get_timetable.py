#!/usr/bin/env python3
# test_get_timetable.py: get_timetable.py用ユニットテスト

import os
import sys
import shutil
import unittest

package_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(package_path, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from get_timetable import Timetable

class TestTimetable(unittest.TestCase):

    TMP_GET_TIMETABLE_CACHE_DIR = '/tmp/get_timetable_cache'
    TMP_CACHE_FILES = [
        'down_こだま701号.html', 'up_こだま700号.html',
        'down_のぞみ1号.html', 'up_のぞみ2号.html',
        'down_ひかり501号.html', 'up_ひかり500号.html',
        'down_こだま999号.html.error', 'up_こだま998号.html.error',
        '品川_20210901_down.html', '品川_20210901_up.html',
        '京都_20210901_down.html', '京都_20210901_up.html',
        'timetables.json', 'trains.json'
    ]

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        if os.path.exists(self.TMP_GET_TIMETABLE_CACHE_DIR):
            shutil.rmtree(self.TMP_GET_TIMETABLE_CACHE_DIR)

    def tearDown(self):
        if os.path.exists(self.TMP_GET_TIMETABLE_CACHE_DIR):
            shutil.rmtree(self.TMP_GET_TIMETABLE_CACHE_DIR)

    def test___init___001(self):
        testid = sys._getframe().f_code.co_name
        # 全パラメタ省略
        exp = None
        try:
            testobj = Timetable()
        except Exception as e:
            exp = e.args[0]
        self.assertEqual(exp, "__init__() missing 2 required positional arguments: 'start' and 'end'")
        # endパラメタ省略
        exp = None
        try:
            testobj = Timetable('20210901')
        except Exception as e:
            exp = e.args[0]
        self.assertEqual(exp, "__init__() missing 1 required positional argument: 'end'")
        # start=None
        exp = ''
        try:
            testobj = Timetable(None, '20210930')
        except Exception as e:
            exp = e.args[0]
        self.assertEqual(exp, 'start parameter is invalid, None')
        # start=数値
        exp = ''
        try:
            testobj = Timetable(20210901, '20210930')
        except Exception as e:
            exp = e.args[0]
        self.assertEqual(exp, 'start parameter is invalid, 20210901')
        # start=7文字
        exp = ''
        try:
            testobj = Timetable('2021090', '20210930')
        except Exception as e:
            exp = e.args[0]
        self.assertEqual(exp, 'start parameter is invalid, 2021090')
        # end=None
        exp = ''
        try:
            testobj = Timetable('20210901', None)
        except Exception as e:
            exp = e.args[0]
        self.assertEqual(exp, 'end parameter is invalid, None')
        # start=数値
        exp = ''
        try:
            testobj = Timetable('20210901', 20210930)
        except Exception as e:
            exp = e.args[0]
        self.assertEqual(exp, 'end parameter is invalid, 20210930')
        # start=7文字
        exp = ''
        try:
            testobj = Timetable('20210901', '2021093')
        except Exception as e:
            exp = e.args[0]
        self.assertEqual(exp, 'end parameter is invalid, 2021093')
        # start > end
        exp = ''
        try:
            testobj = Timetable('20210930', '20210901')
        except Exception as e:
            exp = e.args[0]
        self.assertEqual(exp, 'start parameter is big from end paramter, 20210930 20210901')
        # cache_dir=None
        exp = ''
        try:
            testobj = Timetable('20210901', '20210930', cache_dir=None)
        except Exception as e:
            exp = e.args[0]
        self.assertEqual(exp, 'cache_dir parameter is invalid, None')
        # cache_dir=数値
        exp = ''
        try:
            testobj = Timetable('20210901', '20210930', cache_dir=12345)
        except Exception as e:
            exp = e.args[0]
        self.assertEqual(exp, 'cache_dir parameter is invalid, 12345')
        # cache_dir=''
        exp = ''
        try:
            testobj = Timetable('20210901', '20210930', cache_dir='')
        except Exception as e:
            exp = e.args[0]
        self.assertEqual(exp, 'cache_dir parameter is invalid, ')
        # 正しいパラメタ指定
        testobj = Timetable('20210901', '20210930')
        self.assertEqual(type(testobj) is Timetable, True)
        testobj = None
        # 正しいパラメタ指定cache_dir指定
        testobj = Timetable('20210901', '20210930', cache_dir=self.TMP_GET_TIMETABLE_CACHE_DIR)
        self.assertEqual(type(testobj) is Timetable, True)
        testobj = None
        # 終了

    def test___del___001(self):
        testid = sys._getframe().f_code.co_name
        # 環境設定
        testobj = Timetable('20210901', '20210930')
        self.assertEqual(type(testobj) is Timetable, True)
        # パラメタ無し・復帰値無し
        testobj.__del__()
        self.assertEqual(True, True)
        # 終了
        testobj = None

    def test_initialize_001(self):
        testid = sys._getframe().f_code.co_name
        # 環境設定
        testobj = Timetable('20210901', '20210930', cache_dir=self.TMP_GET_TIMETABLE_CACHE_DIR)
        self.assertEqual(type(testobj) is Timetable, True)
        # パラメタ無し
        rc = testobj.initialize()
        self.assertEqual(rc, 0)
        self.assertEqual(os.path.exists(self.TMP_GET_TIMETABLE_CACHE_DIR), True)
        # 終了
        testobj = None

    def test_initialize_002(self):
        testid = sys._getframe().f_code.co_name
        # 環境設定
        testobj = Timetable('20210901', '20210930', cache_dir=self.TMP_GET_TIMETABLE_CACHE_DIR)
        self.assertEqual(type(testobj) is Timetable, True)
        # 各月の1日のキャッシュクリア
        testobj.today = '20210901'
        os.mkdir(self.TMP_GET_TIMETABLE_CACHE_DIR)
        for f in self.TMP_CACHE_FILES:
            with open(os.path.join(self.TMP_GET_TIMETABLE_CACHE_DIR, f), 'w') as fh:
                fh.write('')
        rc = testobj.initialize()
        self.assertEqual(rc, 0)
        file_list = os.listdir(self.TMP_GET_TIMETABLE_CACHE_DIR)
        self.assertEqual(len(file_list), 1)
        self.assertEqual(file_list[0], 'cleared_' + testobj.today)
        # 終了
        testobj = None

    def test_get_stations_timetable_001(self):
        testid = sys._getframe().f_code.co_name
        # 環境設定
        testobj = Timetable('20210901', '20210930', cache_dir=self.TMP_GET_TIMETABLE_CACHE_DIR)
        self.assertEqual(type(testobj) is Timetable, True)
        # 終了
        testobj = None

    def test_interpret_remark_001(self):
        testid = sys._getframe().f_code.co_name
        # 環境設定
        testobj = Timetable('20211201', '20220110', cache_dir=self.TMP_GET_TIMETABLE_CACHE_DIR)
        self.assertEqual(type(testobj) is Timetable, True)
        # 実行
        trains = ['のぞみ001',
                'のぞみ002',
                'のぞみ003',
                'のぞみ004',
                'のぞみ005',
                'のぞみ006',
                'のぞみ007',
                'のぞみ008',
                'のぞみ009',
                'のぞみ010',
                'のぞみ011',
                'のぞみ012',
                'のぞみ013',
                'のぞみ014',
                'のぞみ015',
                'のぞみ016',
                'のぞみ017',
        ]
        rems = ['',
                'N700S車両で運転',
                '12月25日運転',
                '12月4・11・18・29・30日運転',
                '12月29～31日・1月2～4日運転',
                '休日運休',
                '休日と12月28～31日、1月8日は運休',
                '休日運休・但し、12月5・12・19・26・30・31・1月1・9日は運転',
                '休日と12月28～31日、1月8日は運休・但し、12月26日・1月1～3・9日は運転',
                '土曜運休',
                '土曜運休・但し、1月8日は運転',
                '土曜と12月3・5・10・12・28日は運休',
                '土曜と12月3・5・10・12・26・28～31日、1月2～5日は運休・但し、12月4・11・18日・1月8日は運転',
                '土曜・休日運休',
                '12月29日は運休',
                '12月29・31日は運休',
                '12月28～31日、1月2～4日は運休'
        ]
        start = '20211201'
        end = '20220110'
        months = ['202112', '202201']
        results = [{'運転日': [], '運休日': []},
                {'運転日': [], '運休日': []},
                {'運転日': ['20211225'], '運休日': []},
                {'運転日': ['20211204', '20211211', '20211218', '20211229', '20211230'], '運休日': []},
                {'運転日': ['20211229', '20211230', '20211231', '20220102', '20220103', '20220104'], '運休日': []},
                {'運転日': [], '運休日': ['20211205', '20211212', '20211219', '20211226', '20220101', '20220102', '20220109', '20220110']},
                {'運転日': [], '運休日': ['20211205', '20211212', '20211219', '20211226', '20211228', '20211229', '20211230', '20211231', '20220101', '20220102', '20220108', '20220109', '20220110']},
                {'運転日': ['20211205', '20211212', '20211219', '20211226', '20211230', '20211231', '20220101', '20220109'], '運休日': ['20211205', '20211212', '20211219', '20211226', '20220101', '20220102', '20220109', '20220110']},
                {'運転日': ['20211226', '20220101', '20220102', '20220103', '20220109'], '運休日': ['20211205', '20211212', '20211219', '20211226', '20211228', '20211229', '20211230', '20211231', '20220101', '20220102', '20220108', '20220109', '20220110']},
                {'運転日': [], '運休日': ['20211204', '20211211', '20211218', '20211225', '20220101', '20220108']},
                {'運転日': ['20220108'], '運休日': ['20211204', '20211211', '20211218', '20211225', '20220101', '20220108']},
                {'運転日': [], '運休日': ['20211203', '20211204', '20211205', '20211210', '20211211', '20211212', '20211218', '20211225', '20211228', '20220101', '20220108']},
                {'運転日': ['20211204', '20211211', '20211218', '20220108'], '運休日': ['20211203', '20211204', '20211205', '20211210', '20211211', '20211212', '20211218', '20211225', '20211226', '20211228', '20211229', '20211230', '20211231', '20220101', '20220102', '20220103', '20220104', '20220105', '20220108']},
                {'運転日': [], '運休日': ['20211204', '20211205', '20211211', '20211212', '20211218', '20211219', '20211225', '20211226', '20220101', '20220102', '20220108', '20220109', '20220110']},
                {'運転日': [], '運休日': ['20211229']},
                {'運転日': [], '運休日': ['20211229', '20211231']},
                {'運転日': [], '運休日': ['20211228', '20211229', '20211230', '20211231', '20220102', '20220103', '20220104']}
        ]
        for i in range(len(rems)):
            # print(testid, i, trains[i], rems[i], start, end, months)
            result = testobj.interpret_remark(trains[i], rems[i], start, end, months)
            self.assertEqual(result is None, False)
            self.assertEqual(list(result.keys()), ['運転日', '運休日'])
            self.assertEqual(result['運転日'], results[i]['運転日'])
            self.assertEqual(result['運休日'], results[i]['運休日'])
        # 終了
        testobj = None


if __name__ == "__main__":
    unittest.main()
