// train,js: 東海道新幹線なんちゃって運行シミュレーター
// Copyright (C) N.Togashi 2021-2022
// phina.js docs：https://phinajs.com/docs/
// phina.js Tips集：https://qiita.com/alkn203/items/bca3222f6b409382fe20
// [phina.js]オブジェクトの操作 -位置、移動、衝突・クリック判定など- について：https://horohorori.com/memo_phina_js/about_object2d/
// 吹き出し：https://github.com/pentamania/phina-talkbubble
// 緯度・経度：https://mapfan.com/map/spots/search
// JR東海アクセス検索：https://railway.jr-central.co.jp/timetable/nr_doc/search.html
// JR東海到着列車案内：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti09.html
// JR東海列車走行位置：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti08.html
// JR東海個別列車時刻表(こだま)：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti07.html?traintype=2&train=723
// JR東海個別列車時刻表(ひかり)：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti07.html?traintype=1&train=511
// JR東海個別列車時刻表(のぞみ)：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti07.html?traintype=6&train=31
// 素材Library.com > 無料イラストTOP > 地図, 日本地図 > 日本地図（ベクターデータ）のイラスト素材・白フチと海：https://www.sozai-library.com/sozai/2528

// phina.js をグローバル領域に展開
phina.globalize();

// 定数
var ENVIRONMENT = 'heroku';
// var ENVIRONMENT = 'VSC';
if(ENVIRONMENT == 'heroku') {
	STATIC_PATH = '/static/';
	CACHE_PATH = '/cache/';
} else {
	STATIC_PATH = '/shinkansen_simulator/static/'
	CACHE_PATH = '/cache/';
}
var PROGRAM_TITLE = '東海道新幹線なんちゃって運行シミュレーター';
var PROGRAM_VERSION = '0.1.3';
var COPYRIGHT = 'Copyright (C) N.Togashi 2021';
var THANKS = '謝辞：Heroku、GitHub、Docker、Phina.js、phina-talkbubble.js、ＪＲ東海(時刻表)、素材Library.com(日本地図)を使わせて頂きました。';
var DIAGRAM_VERSION = '20210901版';
var SCREEN_WIDTH  = 1920;	// 画面横サイズ(document.documentElement.clientWidth)
var SCREEN_HEIGHT = 992;	// 画面縦サイズ(document.documentElement.clientHeight)
var GRID_SIZE = 32;			// グリッドのサイズ
var PANEL_SIZE = GRID_SIZE;	// パネルの大きさ
var PANEL_OFFSET_X = GRID_SIZE*2;	// オフセット値
var PANEL_OFFSET_Y = 0;		// オフセット値
var PANEL_NUM_X = (SCREEN_WIDTH  - PANEL_OFFSET_X*2 - GRID_SIZE) / GRID_SIZE;	// 横のパネル数
var PANEL_NUM_Y = (SCREEN_HEIGHT - PANEL_OFFSET_Y*2 - GRID_SIZE) / GRID_SIZE;	// 縦のパネル数
var LINE_POS_Y = [20, 22];	// 線路のパネル位置縦
var TRAIN_UP = 19;			// 上り
var TRAIN_DOWN = 21;		// 下り
var STATION_Y = 6;			// 駅舎の縦位置
var STATION_SIZE = [56, 128];	// 駅舎のサイズ[X, Y]
var STATIONS = [			// 駅舎情報 ID,駅名,X
	[ 0, '東京',		PANEL_NUM_X-1,	STATION_Y, 6, [35.6809591+0.1, 139.7673068], 0, 0],
	[ 1, '品川',		0,				STATION_Y, 4, [35.6291112, 139.7389313], 0, 0],
	[ 2, '新横浜',		0,				STATION_Y, 4, [35.5067084, 139.6168805], 0, 0],
	[ 3, '小田原',		0,				STATION_Y, 4, [35.2562557, 139.1554675], 0, 0],
	[ 4, '熱海',		0,				STATION_Y, 2, [35.1038,    139.0778   ], 0, 0],
	[ 5, '三島',		0,				STATION_Y, 4, [35.126334,  138.9107634], 0, 0],
	[ 6, '新富士',		0,				STATION_Y, 4, [35.1420718, 138.6633979], 0, 0],
	[ 7, '静岡',		0,				STATION_Y, 4, [34.971698,  138.3890637], 0, 0],
	[ 8, '掛川',		0,				STATION_Y, 4, [34.7690914, 138.0146393], 0, 0],
	[ 9, '浜松',		0,				STATION_Y, 4, [34.7038438, 137.7349526], 0, 0],
	[10, '豊橋',		0,				STATION_Y, 4, [34.7629443, 137.3820671], 0, 0],
	[11, '三河安城',	0,				STATION_Y, 4, [34.9689643, 137.0604602], 0, 0],
	[12, '名古屋',		0,				STATION_Y, 4, [35.1706431, 136.8816945], 0, 0],
	[13, '岐阜羽島',	0,				STATION_Y, 4, [35.3156608, 136.6856194], 0, 0],
	[14, '米原',		0,				STATION_Y, 4, [35.3144414, 136.2897051], 0, 0],
	[15, '京都',		0,				STATION_Y, 4, [34.9851603, 135.7584294], 0, 0],
	[16, '新大阪',		2,				STATION_Y, 8, [34.7338219, 135.5014056], 0, 0],
];
var STATIONS_DISTANCE = calcStationsDistance(STATIONS);
// var STATIONS_DISTANCE = {"0-1": 17.078002122438473, "1-0": 17.078002122438473, "1-2": 17.52469759458355, "2-1": 17.52469759458355, "2-3": 50.253447218781254, "3-2": 50.253447218781254, "3-4": 18.3631940858771, "4-3": 18.3631940858771, "4-5": 15.398424481279315, "5-4": 15.398424481279315, "5-6": 22.56236879872776, "6-5": 22.56236879872776, "6-7": 31.343675567064256, "7-6": 31.343675567064256, "7-8": 40.91885277881738, "8-7": 40.91885277881738, "8-9": 26.5670383358072, "9-8": 26.5670383358072, "9-10": 32.90994118628989, "10-9": 32.90994118628989, "10-11": 37.225303218650915, "11-10": 37.225303218650915, "11-12": 27.70545223389335, "12-11": 27.70545223389335, "12-13": 24.02269079013669, "13-12": 24.02269079013669, "13-14": 35.92291310222524, "14-13": 35.92291310222524, "14-15": 60.61147446445845, "15-14": 60.61147446445845, "15-16": 36.48323051450204, "16-15": 36.48323051450204, "total": 494.8907064935329};
STATIONS = calcStationsGridX(STATIONS, STATIONS_DISTANCE);
var DIAGRAM_DOWN = {		// 下り時刻表
	'property': ['down', 20210701, 20210731],
	'こだま707号': {
		'property': ['down', '07:52', '11:56', '東京', '新大阪'],
		'remarks': {'運転日': [], '運休日': [], '事項': ''},
		'status': [null, -1, -1],
		'timeLine': [
			[ 0, '07:57'], [ 1, '08:04'], [ 2, '08:15'], [ 3, '08:35'],
			[ 4, '08:45'], [ 5, '08:55'], [ 6, '09:08'], [ 7, '09:21'],
			[ 8, '09:38'], [ 9, '09:51'], [10, '10:08'], [11, '10:25'],
			[12, '10:37', '10:43'],
			[13, '10:58'], [14, '11:16'], [15, '11:36'], [16, '11:51']],
	},
};
var DIAGRAM_UP = {			// 上り時刻表
	'property': ['up', 20210701, 20210731],
	'こだま708号': {
		'property': ['up', '07:49', '11:53', '新大阪', '東京'],
		'remarks': {'運転日': [], '運休日': [], '事項': ''},
		'status': [null, -1, -1],
		'timeLine': [
			[16, '07:54'], [15, '08:10'], [14, '08:33'], [13, '08:51'],
			[12, '09:02', '09:08'],
			[11, '09:24'], [10, '09:41'], [ 9, '09:58'], [ 8, '10:10'],
			[ 7, '10:25'], [ 6, '10:41'], [ 5, '10:54'], [ 4, '11:02'],
			[ 3, '11:14'], [ 2, '11:29'], [ 1, '11:40'], [ 0, '11:48']],
	},
};
var TRAIN_STATUS = [	// balloon_show, message, station, next
	[0, 0, false, '', 0, 1],
	[1, 0, true, '{{train}}\n{{to}}行きです', 0, 1],
	[2, 0, true, '{{train}}\n間もなく発車します', 0, 1],
	[3, 0, true, '{{train}}\n次は{{next}}に止まります', 0, 1],
	[4, 0, true, '{{train}}', 0, 1],
	[5, 0, true, '{{train}}\n間もなく{{next}}です', 0, 1],
	[6, 0, true, '{{train}}\n{{station}}です', 0, 1],
	[7, 0, true, '{{train}}\n{{station}}です', 0, 1],
	[8, 0, true, '{{train}}\n間もなく終点{{to}}です', 0, 1],
	[9, 0, true, '{{train}}\n終点{{to}}です', 0, 1]
];
var TRAIN_OUTOF_RAIL   = 0;	// 時間外
var TRAIN_INTO_RAIL    = 1;	// 停車中
var TRAIN_SOON_START   = 2;	// 停車中
var TRAIN_START        = 3;	// 走行中
var TRAIN_RUNNING      = 4;	// 走行中
var TRAIN_SOON_STOP    = 5;	// 走行中
var TRAIN_STOP_STATION = 6;	// 停車中
var TRAIN_STOPPING     = 7;	// 停車中
var TRAIN_SOON_ARRIVAL = 8;	// 停車中
var TRAIN_ARRIVAL      = 9;	// 停車中
var TS_ID = 0;
var TS_TIME = 1;
var TS_BALLOON = 2;
var TS_MESSAGE = 3;
var TS_STATION = 4;
var TS_NEXT = 5;
var ASSETS = {
	image: {
		'日本地図': STATIC_PATH + 'images/2528.png',
		'line':		STATIC_PATH + 'images/線路01.gif',
		'N700下りのぞみ':	STATIC_PATH + 'images/N700系下りのぞみ.png',
		'N700下りひかり':	STATIC_PATH + 'images/N700系下りひかり.png',
		'N700下りこだま':	STATIC_PATH + 'images/N700系下りこだま.png',
		'N700上りのぞみ':	STATIC_PATH + 'images/N700系上りのぞみ.png',
		'N700上りひかり':	STATIC_PATH + 'images/N700系上りひかり.png',
		'N700上りこだま':	STATIC_PATH + 'images/N700系上りこだま.png',
	},
}
WEEKDAYS = ['日','月','火','水','木','金','土'];
DEBUG_TRAINS = [];

// グローバル変数
var g_game_app = null;
var g_scene_main = null;
var g_demo = 1;
var g_real_date = new Date()
var g_start_date = getCurrentDate(1, 0);
var g_current_date = g_start_date;
// console.log('start:' + getCurrentTime(true));
var g_update_freauency = 2.0;
var g_stations = [];
var g_trains_down = [];
var g_trains_up = [];
// グリッド
var g_grids = Grid(GRID_SIZE * PANEL_NUM_X, PANEL_NUM_X);
// 列車数を初期化
var g_train_down_count = 0;
var g_train_up_count = 0;

// MainScene クラス定義：メインシーン
phina.define('MainScene', {
	// 継承
	superClass: 'DisplayScene',
		// コンストラクタ
		init: function() {
			// 親クラス初期化
			this.superInit({
				width: SCREEN_WIDTH,
				height: SCREEN_HEIGHT,
				backgroundColor: 'lightgreen',	// 'transparent' or 'white',
				// fill: 'transparent',	// 'white',
			});
			this.force_update = false;
			g_scene_main = this;
			// グループ作成
			var back_panel = DisplayElement().addChildTo(this);
			var group_panel = DisplayElement().addChildTo(this);
			var group_station = DisplayElement().addChildTo(this);
			var group_line = DisplayElement().addChildTo(this);
			this.group_train = DisplayElement().addChildTo(this);
			// 背景表示
			this.back_image = Sprite('日本地図').addChildTo(back_panel).setRotation(8);
			this.back_image.setPosition(1560, -10).setScale(12.5, 6.0);
			// Copyrightと謝辞を表示
			Label({
				text: COPYRIGHT + '  ' + THANKS,
				x: g_grids.span(PANEL_NUM_X/2) + 80,
				y: g_grids.span(PANEL_NUM_Y) + 16,
				fontSize: 24,
			}).addChildTo(back_panel);
			// タイトル表示
			this.title = Label({
				text: PROGRAM_TITLE + ' ' + PROGRAM_VERSION,
				x: g_grids.span(PANEL_NUM_X/2) + PANEL_OFFSET_X + 32*5,
				y: g_grids.span(1) + PANEL_OFFSET_Y,
			}).addChildTo(this);
			this.diagram_version = Label({
				text: '時刻表:' + DIAGRAM_VERSION + '(     )',
				x: g_grids.span(PANEL_NUM_X) + PANEL_OFFSET_X + 60 + 22,
				y: g_grids.span(1) + PANEL_OFFSET_Y,
				align: 'right',
			}).addChildTo(this);
			this.diagram_update1 = Label({
				text: '????',
				x: g_grids.span(PANEL_NUM_X) + PANEL_OFFSET_X + 60 + 8,
				y: g_grids.span(1) + PANEL_OFFSET_Y - 10,
				align: 'right',
				fill: 'blue',
				fontSize: 20,
				fontWeight: "bold",
			}).addChildTo(this);
			this.diagram_update2 = Label({
				text: '更新',
				x: g_grids.span(PANEL_NUM_X) + PANEL_OFFSET_X + 60 + 4,
				y: g_grids.span(1) + PANEL_OFFSET_Y + 8,
				align: 'right',
				fill: 'blue',
				fontSize: 20,
			}).addChildTo(this);
			this.date = Label({
				text: g_start_date.getFullYear()+'年'+('0'+(g_start_date.getMonth()+1)).slice(-2)+'月'+('0'+g_start_date.getDate()).slice(-2)+'日(' + WEEKDAYS[g_start_date.getDay()] + ')',
				x: g_grids.span(PANEL_NUM_X) + PANEL_OFFSET_X + 60,
				y: g_grids.span(2) + PANEL_OFFSET_Y,
				align: 'right',
			}).addChildTo(this);
			this.time = Label({
				text: (' '+g_start_date.getHours()).slice(-2)+'時'+(' '+g_start_date.getMinutes()).slice(-2)+'分',
				x: g_grids.span(PANEL_NUM_X) + PANEL_OFFSET_X,
				y: g_grids.span(3) + PANEL_OFFSET_Y,
				align: 'right',
			}).addChildTo(this);
			this.limitations = Label({
				text: '※運転日指定の列車は最初の運転日以降に運行可',
				fill: 'blue',
				fontSize: 20,
				fontWeight: "bold",
				x: g_grids.span(PANEL_NUM_X/2+18) + PANEL_OFFSET_X + 32,
				y: g_grids.span(2) + PANEL_OFFSET_Y,
				align: 'right',
			}).addChildTo(this);
			// 列車数表示
			this.train_count = Label('下り：0  上り：0').addChildTo(this);
			this.train_count.x = g_grids.span(PANEL_NUM_X/4*3) + PANEL_OFFSET_X;
			this.train_count.y = g_grids.span(3) + PANEL_OFFSET_Y;

			// 駅舎を表示する
			for(let i=0; i<STATIONS.length; i++) {
				var station = Station(STATIONS[i], group_line).addChildTo(group_station);
				g_stations.push(station);
			}

			// グリッドにパネル配置
			PANEL_NUM_X.times(function(spanX) {
				var xG = spanX + 1;
				PANEL_NUM_Y.times(function(spanY) {
					var yG = spanY + 1;
					// パネル作成
					var panel = Panel().addChildTo(group_panel);
					// Gridを利用して配置
					// panel.setOrigin(0, 0);
					panel.x = g_grids.span(xG) + PANEL_OFFSET_X;
					panel.y = g_grids.span(yG) + PANEL_OFFSET_Y;
					// パネルに線路を描画する
					panel.isLine = false;
					// if(LINE_POS_Y.indexOf(yG + 1) >= 0 && spanX >= (PANEL_OFFSET_X / GRID_SIZE)) {
					if(LINE_POS_Y.indexOf(yG + 1) >= 0 && (spanX > 0 && spanX < (PANEL_NUM_X - 1))) {
						panel.isLine = true;
					}
					if(panel.isLine) {
						Sprite('line').addChildTo(group_line).setPosition(panel.x - PANEL_SIZE/4, panel.y - PANEL_SIZE/2);
						Sprite('line').addChildTo(group_line).setPosition(panel.x + PANEL_SIZE/4, panel.y - PANEL_SIZE/2);
						// Sprite('line').addChildTo(group_line).setPosition(panel.x, panel.y);
						// Sprite('line').addChildTo(group_line).setPosition(panel.x + PANEL_SIZE/2, panel.y);
					}
				});
			});
			// 時刻表を取得する
			get_timetable();
			this.diagram_version.text = '時刻表:' + DIAGRAM_DOWN['property'][1] + '版(     )';
			if(DIAGRAM_DOWN['property'].length >= 4) {
				this.diagram_update1.text = (''+DIAGRAM_DOWN['property'][3]).substr(4,4);
			}
			// のぞみの列車数：吹き出しの位置調整用
			this.down_nozomi_count = 0;
			this.up_nozomi_count = 0;
			// 設定パネル作成
			show_setup_panel(this);
			// 時刻表表示用バルーン
			this.balloon_timetable_down = phina.ui.TalkBubbleLabel({
				text: '',
				fontSize: 22,
				tipDirection: 'top',
				tipProtrusion: 1,
				tipBottomSize: 1,
				bubbleFill: 'white',
			}).addChildTo(this).setPosition((SCREEN_WIDTH/8)*5+128, (SCREEN_HEIGHT/9)*5+32);
			this.balloon_timetable_down.hide();
			this.balloon_timetable_up = phina.ui.TalkBubbleLabel({
				text: '',
				fontSize: 22,
				tipDirection: 'top',
				tipProtrusion: 1,
				tipBottomSize: 1,
				bubbleFill: 'white',
			}).addChildTo(this).setPosition((SCREEN_WIDTH/8)*2+96, (SCREEN_HEIGHT/9)*5+32);
			this.balloon_timetable_up.hide();
			// this.setInteractive(true);
			this.balloon_timetable_down.setInteractive(true);
			this.balloon_timetable_up.setInteractive(true);
			this.onclick = function() {
				// console.log('MainScene.onclick()');
				if(! this.click_ignore) {
					this.balloon_timetable_down.onclick();
					this.click_ignore = false;
					this.balloon_timetable_up.onclick();
				}
				this.click_ignore = false;
			}
			this.balloon_timetable_down.onclick = function() {
				if(! this.parent.click_ignore) {
					this.parent.click_ignore = true;
					this.parent.balloon_timetable_down.text = '';
					this.parent.balloon_timetable_down.hide();
				}
			}
			this.balloon_timetable_up.onclick = function() {
				if(! this.parent.click_ignore) {
					this.parent.click_ignore = true;
					this.parent.balloon_timetable_up.text = '';
					this.parent.balloon_timetable_up.hide();
				}
			}
		},
		// 更新
		update: function() {
			// 現在時刻を更新
			var cDate = getCurrentDate(0, 1);
			var diff = cDate.getTime() - g_current_date.getTime();
			if(this.force_update == false
			&& (cDate.getFullYear() == g_current_date.getFullYear()
			 && cDate.getMonth() == g_current_date.getMonth()
			 && cDate.getDay() == g_current_date.getDay()
			 && cDate.getHours() == g_current_date.getHours()
			 && cDate.getMinutes() == g_current_date.getMinutes())) {
				// console.log('update pass: ' + diff + 'ms');
				return;
			}
			this.force_update = false;
			g_real_date.setTime(new Date());
			g_current_date = cDate;
			var cTime = getCurrentTime(true);
			var hm = cTime.split(':');
			this.date.text = g_current_date.getFullYear()+'年'+('0'+(g_current_date.getMonth()+1)).slice(-2)+'月'+('0'+g_current_date.getDate()).slice(-2)+'日('+WEEKDAYS[g_current_date.getDay()]+')';
			this.time.text = hm[0]+'時'+hm[1]+'分';
			// console.log('MainScene.update: ' + cTime);
			// 先に進んでいる列車を先に更新する
			let trains_update = [];
			for(let i=0; i<g_trains_down.length; i++)  {
				trains_update.push(g_trains_down[i]);
			}
			trains_update.sort((a, b) => {	// 降順ソート
				if(a.train_location < b.train_location) return 1;
				if(a.train_location > b.train_location) return -1;
				return 0;
			});
			for(let i=0; i<trains_update.length; i++) {
				updateTrain(trains_update[i]);
			}
			trains_update = [];
			for(let i=0; i<g_trains_up.length; i++)  {
				trains_update.push(g_trains_up[i]);
			}
			trains_update.sort((a, b) => {	// 降順ソート
				if(a.train_location < b.train_location) return 1;
				if(a.train_location > b.train_location) return -1;
				return 0;
			});
			for(let i=0; i<trains_update.length; i++) {
				updateTrain(trains_update[i]);
			}
			// 下り列車を新規追加
			for(let key in DIAGRAM_DOWN) {
				if(key == 'property') continue;
				// console.log(key + '.diagram.property:' + DIAGRAM_DOWN[key]['property'].join(','));
				if(DIAGRAM_DOWN[key]['status'][0] != null) {
					continue;
				}
				if(is_operating_datetime(DIAGRAM_DOWN[key], cDate, cTime)) {
					if(key.substr(0, 3) == 'のぞみ') {
						this.down_nozomi_count++;
					}
					// console.log('MainScene.update Train(down):' + DIAGRAM_DOWN[key]['property'].join(','));
					g_trains_down.push(Train(DIAGRAM_DOWN, key, this.down_nozomi_count).addChildTo(this.group_train));
				}
			}
			// 上り列車を新規追加
			for(let key in DIAGRAM_UP) {
				if(key == 'property') continue;
				// console.log(key + '.diagram.property:' + DIAGRAM_UP[key]['property'].join(','));
				if(DIAGRAM_UP[key]['status'][0] != null) {
					continue;
				}
				if(is_operating_datetime(DIAGRAM_UP[key], cDate, cTime)) {
					if(key.substr(0, 3) == 'のぞみ') {
						this.up_nozomi_count++;
					}
					// console.log('MainScene.update Train(up):' + DIAGRAM_UP[key]['property'].join(','));
					g_trains_up.push(Train(DIAGRAM_UP, key, this.up_nozomi_count).addChildTo(this.group_train));
				}
			}
			// 列車数を更新
			this.train_count.text = '下り：' + g_train_down_count + '本  上り：' + g_train_up_count + '本';
		},
});

// Panel クラス定義
phina.define('Panel', {
	// RectangleShapeを継承
	superClass: 'RectangleShape',
	// superClass: 'Shape',
		// コンストラクタ
		init: function() {
			// 親クラス初期化
			if(true) {
				this.superInit({
					width: PANEL_SIZE,
					height: PANEL_SIZE,
					backgroundColor: 'transparent',
					fill: 'transparent',	// 'white',
					stroke: 'transparent',	// 'white',
				});
			} else {
				this.superInit({
					width: PANEL_SIZE,
					height: PANEL_SIZE,
					fill: 'silver',		// 塗りつぶし色
					stroke: 'white',	// 枠の色
					cornerRadius: 2,	// 角の丸み
				});
			}
		},
});

// 列車クラス
phina.define('Train', {
	// Shapeを継承
	superClass: 'Shape',
		// コンストラクタ
		init: function(diagram_all, name, count) {
			// 親クラス初期化
			this.superInit({
				width: GRID_SIZE,
				height: GRID_SIZE,
				backgroundColor: 'transparent',
			});
			this.diagram_all = diagram_all;
			this.name = name;
			this.diagram = diagram_all[this.name];
			this.diagram['status'][0] = this;
			this.status = TRAIN_STATUS[TRAIN_OUTOF_RAIL].slice();
			this.cDate = g_current_date;
			this.running_plan = null;
			this.force_update = false;
			this.train_location = -1.0;
			this.train_st_id = -1;
			// イメージ表示
			let image_name = 'N700';
			let image_position = [0, 0];
			if(this.diagram['property'][0] == 'down') {
				this.x = g_grids.span(PANEL_NUM_X - 1) + PANEL_OFFSET_X;
				this.y = g_grids.span(TRAIN_DOWN - 1) + PANEL_OFFSET_Y;
				image_name += '下り';
				image_position = [-2, -10];
				// this.train_image = Sprite('N700下り').addChildTo(this).setPosition(-2, -10);
			} else {
				this.y = g_grids.span(TRAIN_UP - 1) + PANEL_OFFSET_Y;
				image_name += '上り';
				image_position = [46, -9];
				// this.train_image = Sprite('N700上り').addChildTo(this).setPosition(46, -9);
			}
			image_name += this.name.substr(0, 3);
			this.train_image = Sprite(image_name).addChildTo(this).setPosition(image_position[0], image_position[1]);
			this.train_image.scaleX = 0.6;
			this.train_image.scaleY = 0.6;
			// 案内表示吹き出し
			this.name_msg = this.name;
			if('remarks' in this.diagram) {
				if('事項' in this.diagram['remarks']) {
					if(this.diagram['remarks']['事項'] != '') {
						this.name_msg += this.diagram['remarks']['事項'].substr(0,1);
						if(this.diagram['remarks']['事項'].substr(1).indexOf('☆') >= 0) {
							this.name_msg += '☆';
						}
					}
				}
			}
			// バルーン表示
			var balloon_color = "khaki";	// khaki=#f0e68c
			var tipProtrusion = 32;
			var balloon_posX = 0;
			var balloon_posY = 90;
			var balloon_posY_sign = 1;
			var nozomi_near = 1;
			var balloon_tipDirection = 'top';
			this.balloon_timetable = g_scene_main.balloon_timetable_down;
			if(this.diagram['property'][0] == 'up') {
				balloon_posX = 48;
				balloon_posY = -96;
				balloon_posY_sign = -1;
				nozomi_near = 0;
				balloon_tipDirection = 'bottom';
				this.balloon_timetable = g_scene_main.balloon_timetable_up;
			}
			if(this.name.substr(0, 3) == 'のぞみ') {
				if((count % 2) == nozomi_near) {
					tipProtrusion += 64;
					balloon_posY += balloon_posY_sign * 64;
				}
			} else if(this.name.substr(0, 3) == 'ひかり') {
				balloon_color = "tomato";	// tomato=#ff6347
				tipProtrusion += 128;
				balloon_posY += balloon_posY_sign * 128;
			} else if(this.name.substr(0, 3) == 'こだま') {
				balloon_color = "lightsteelblue";	// lightsteelblue=#e6e6fa
				tipProtrusion += 192;
				balloon_posY += balloon_posY_sign * 192;
			}
			this.balloon = phina.ui.TalkBubbleLabel({
				text: '',
				fontSize: 22,
				tipDirection: balloon_tipDirection,
				tipProtrusion: tipProtrusion,
				tipBottomSize: 24,
				bubbleFill: balloon_color,
			}).addChildTo(this).setPosition(balloon_posX, balloon_posY);
			// 列車時刻表表示
			this.setInteractive(true);
			this.balloon.setInteractive(true);
			this.onclick = function() {
				if(! g_scene_main.click_ignore) {
					g_scene_main.click_ignore = true;
					this.balloon_timetable.text = get_train_taimetable(this.name, this.diagram['property'][0]);
					this.balloon_timetable.show();
				}
			}
			this.balloon.onclick = function() {
				this.parent.onclick();
			}
			// 列車位置調整、表示列車数
			updateTrain(this);
		},
});

// 駅舎クラス
phina.define('Station', {
	// RectangleShapeを継承
	superClass: 'RectangleShape',
		// コンストラクタ
		init: function(st, group_line) {
			this.station_id = st[0];
			this.station_name = st[1];
			var x = st[2];
			var y = st[3];
			var homes = st[4];
			// 親クラス初期化
			this.superInit({
				width: STATION_SIZE[0],
				height: STATION_SIZE[1],
				fill: 'white',		// 塗りつぶし色
				stroke: 'black',	// 枠の色
				cornerRadius: 2,	// 角の丸み
			});
			this.x = g_grids.span(x) + PANEL_OFFSET_X;
			this.y = g_grids.span(y) + PANEL_OFFSET_Y;
			this.setInteractive(true);
			this.onclick = function() {
				if(! g_scene_main.click_ignore) {
					g_scene_main.click_ignore = true;
					if(this.station_id == (STATIONS.length-1)) {
						g_scene_main.balloon_timetable_down.text = '';
						g_scene_main.balloon_timetable_down.hide();
					} else {
						g_scene_main.balloon_timetable_down.text = get_station_taimetable(this.station_id, 'down');
						g_scene_main.balloon_timetable_down.show();
					}
					if(this.station_id == 0) {
						g_scene_main.balloon_timetable_up.text = '';
						g_scene_main.balloon_timetable_up.hide();
					} else {
						g_scene_main.balloon_timetable_up.text = get_station_taimetable(this.station_id, 'up');
						g_scene_main.balloon_timetable_up.show();
					}
				}
			}
			// 駅名表示
			var label = Label(this.station_name.split('').join('\n')).addChildTo(this);
			// label.fontFamily = 'sans-serif';
			label.fontSize = 26;
			label.fill = 'black';
			// 駅名とホームを線で繋ぐ
			var station_home_line = RectangleShape({
				width: 2,
				height: 300,
				fill: 'background',
				stroke: 'black',
				strokeWidth: 1,
			}).addChildTo(this).setOrigin(0.5, 1.0).setPosition(0, GRID_SIZE*(STATION_Y+6)-10);
			// ホームを表示
			var home = RectangleShape({
				width: PANEL_SIZE*1.5,
				height: PANEL_SIZE*(homes+2) + 8,
				fill: 'silver',
				padding: 1,
				stroke: 'black',
			}).addChildTo(this).setPosition(-2, (LINE_POS_Y[0]-STATION_Y-1)*PANEL_SIZE+15);
			// パネルにホームを描画する
			if(homes > 2) {
				for(let i=1; i<(homes/2); i++) {
					// 上り用
					var xL = g_grids.span(x) + PANEL_OFFSET_X;
					var yL = g_grids.span(LINE_POS_Y[0] - i - 1) + PANEL_OFFSET_Y;
					Sprite('line').addChildTo(group_line).setPosition(xL - PANEL_SIZE/4, yL - PANEL_SIZE/2);
					Sprite('line').addChildTo(group_line).setPosition(xL + PANEL_SIZE/4, yL - PANEL_SIZE/2);
					if(this.station_id != 0) {
						Sprite('line').addChildTo(group_line).setPosition(xL + PANEL_SIZE/2, yL - PANEL_SIZE/2).setRotation(90);
						Sprite('line').addChildTo(group_line).setPosition(xL + PANEL_SIZE/2, yL - PANEL_SIZE/2 + (PANEL_SIZE/2*1)).setRotation(90);
					}
					if(this.station_id != (STATIONS.length-1)) {
						Sprite('line').addChildTo(group_line).setPosition(xL-(PANEL_SIZE/4)*3, yL - PANEL_SIZE/2).setRotation(90);
						Sprite('line').addChildTo(group_line).setPosition(xL-(PANEL_SIZE/4)*3, yL - PANEL_SIZE/2 + (PANEL_SIZE/2*1)).setRotation(90);
					}
					// 下り用
					xL = g_grids.span(x) + PANEL_OFFSET_X;
					yL = g_grids.span(LINE_POS_Y[1] + i - 2) + PANEL_OFFSET_Y;
					Sprite('line').addChildTo(group_line).setPosition(xL - PANEL_SIZE/4, yL + PANEL_SIZE/2);
					Sprite('line').addChildTo(group_line).setPosition(xL + PANEL_SIZE/4, yL + PANEL_SIZE/2);
					if(this.station_id != 0) {
						Sprite('line').addChildTo(group_line).setPosition(xL + PANEL_SIZE/2, yL + PANEL_SIZE/2 - PANEL_SIZE/4).setRotation(90);
						Sprite('line').addChildTo(group_line).setPosition(xL + PANEL_SIZE/2, yL + PANEL_SIZE/2 - PANEL_SIZE/4 - (PANEL_SIZE/2*1)).setRotation(90);
					}
					if(this.station_id != (STATIONS.length-1)) {
						Sprite('line').addChildTo(group_line).setPosition(xL-(PANEL_SIZE/4)*3, yL + PANEL_SIZE/2 - PANEL_SIZE/4).setRotation(90);
						Sprite('line').addChildTo(group_line).setPosition(xL-(PANEL_SIZE/4)*3, yL + PANEL_SIZE/2 - PANEL_SIZE/4 - (PANEL_SIZE/2*1)).setRotation(90);
					}
				}
			}
		},
});

// メイン処理
phina.main(function() {
	// アプリケーション生成
	g_game_app = GameApp({
		title: '東海道新幹線なんちゃって運行シミュレーター',
		fps: 2.0,				// fps指定
		startLabel: 'main',		// メインシーンから開始する
		width: SCREEN_WIDTH + GRID_SIZE,
		height: SCREEN_HEIGHT + GRID_SIZE,
		assets: ASSETS,
	});
	// アプリケーション実行
	g_game_app.run();
});

// 設定パネルを表示する
function show_setup_panel(scene) {
	var isAndroid = navigator.userAgent.indexOf("Android") > 0;
	var setup_panel1 = Shape({
		x: 0,
		y: 0,
		width: GRID_SIZE * 21,
		height: GRID_SIZE * 3,
		backgroundColor: 'white',
		stroke: 'black',	// 枠の色
		cornerRadius: 2,	// 角の丸み
	}).addChildTo(scene).setOrigin(0, 0);
	var setup_panel2 = Shape({
		x: 0 + GRID_SIZE * 21 + 32,
		y: 0 + (GRID_SIZE * 2) - 8,
		width: GRID_SIZE * 11 + 16,
		height: GRID_SIZE + 8,
		backgroundColor: 'white',
		stroke: 'black',	// 枠の色
		cornerRadius: 2,	// 角の丸み
	}).addChildTo(scene).setOrigin(0, 0);
	// 更新頻度
	var label_updfreq_label = Label({
		text: '更新頻度：1分=',
		x: 6,
		y: 32,
		fontSize: 28,
	}).addChildTo(setup_panel1).setOrigin(0.0, 0.5);
	var label_updfreq_value = Label({
		text: g_update_freauency + '秒',
		x: 6 + 16*13,
		y: 32,
		fontSize: 28,
	}).addChildTo(setup_panel1).setOrigin(0.0, 0.5);
	var button_updfreq_minus = Button({
		x: 6 + 16*18,
		y: 32,
		width: 64,	// 横サイズ
		height: 38,	// 縦サイズ
		text: '－',	// 表示文字
		fontSize: 28,		// 文字サイズ
		fontColor: 'black',	// 文字色
		cornerRadius: 10,	// 角丸み
		backgroundColor: 'transparent',
		fill: 'silver',		// ボタン色
		stroke: 'gray',		// 枠色
		strokeWidth: 5,		// 枠太さ
	}).addChildTo(setup_panel1).setOrigin(0.0, 0.5).setInteractive(true);;
	var button_updfreq_plus = Button({
		x: 6 + 16*18 + 16*5,
		y: 32,
		width: 64,	// 横サイズ
		height: 38,	// 縦サイズ
		text: '＋',	// 表示文字
		fontSize: 28,		// 文字サイズ
		fontColor: 'black',	// 文字色
		cornerRadius: 10,	// 角丸み
		backgroundColor: 'transparent',
		fill: 'silver',		// ボタン色
		stroke: 'gray',		// 枠色
		strokeWidth: 5,		// 枠太さ
	}).addChildTo(setup_panel1).setOrigin(0.0, 0.5).setInteractive(true);
	var button_updfreq_second = Button({
		x: 6 + 16*18 + 16*5 + 16*5,
		y: 32,
		width: 80,	// 横サイズ
		height: 38,	// 縦サイズ
		text: '1秒',	// 表示文字
		fontSize: 24,		// 文字サイズ
		fontColor: 'black',	// 文字色
		cornerRadius: 10,	// 角丸み
		backgroundColor: 'transparent',
		fill: 'silver',		// ボタン色
		stroke: 'gray',		// 枠色
		strokeWidth: 5,		// 枠太さ
	}).addChildTo(setup_panel1).setOrigin(0.0, 0.5);
	var button_updfreq_real = Button({
		x: 6 + 16*18 + 16*5 + 16*5 + 16*6,
		y: 32 + ((70-24)/2+1),
		width: 112,	// 横サイズ
		height: 92,	// 縦サイズ
		text: '',	// 表示文字
		fontSize: 24,		// 文字サイズ
		fontColor: 'black',	// 文字色
		cornerRadius: 10,	// 角丸み
		backgroundColor: 'transparent',
		fill: 'silver',		// ボタン色
		stroke: 'gray',		// 枠色
		strokeWidth: 5,		// 枠太さ
	}).addChildTo(setup_panel1).setOrigin(0.0, 0.5).setInteractive(true);
	Label({
		text: '実時間\n現在日時',
		x: 64,
		fontSize: 24,
	}).addChildTo(button_updfreq_real);
	button_updfreq_minus.onclick = function() {
		g_scene_main.click_ignore = true;
		// －ボタンが押されたときの処理
		if(g_update_freauency <= 1.0) {
			if(! isAndroid) {
				alert('更新頻度を1秒未満に設定することはできません。');
			}
			// console.log('更新頻度を1秒未満に設定することはできません。');
			return;
		}
		let answer = true;
		if(! isAndroid) {
			answer = confirm('更新頻度を更新しますか？：1分=' + (g_update_freauency-1.0) + '秒');
		}
		if(answer) {
			g_update_freauency -= 1.0;
			g_demo = 0;
			if(g_update_freauency != 60.0) {
				g_demo = 1;
			}
			label_updfreq_value.text = g_update_freauency + '秒';
			// console.log('accept updfreq_minus, ' + g_update_freauency + '秒');
			clearAllTrainStatus();
			g_scene_main.force_update = true;
			g_scene_main.update();
		}
	}
	button_updfreq_plus.onclick = function() {
		g_scene_main.click_ignore = true;
		// ＋ボタンが押されたときの処理
		let answer = true;
		if(! isAndroid) {
			answer = confirm('更新頻度を更新しますか？：1分=' + (g_update_freauency+1.0) + '秒');
		}
		if(answer) {
			g_update_freauency += 1.0;
			g_demo = 0;
			if(g_update_freauency != 60.0) {
				g_demo = 1;
			}
			label_updfreq_value.text = g_update_freauency + '秒';
			// console.log('accept updfreq_plus, ' + g_update_freauency + '秒');
			g_scene_main.force_update = true;
			g_scene_main.update();
		}
	}
	button_updfreq_second.onclick = function() {
		g_scene_main.click_ignore = true;
		// 1秒ボタンが押されたときの処理
		let answer = true;
		if(! isAndroid) {
			answer = confirm('更新頻度を更新しますか？：1分=1秒');
		}
		if(answer) {
			g_update_freauency = 1.0;
			g_demo = 1;
			label_updfreq_value.text = g_update_freauency + '秒';
			// console.log('accept updfreq_second, ' + g_update_freauency + '秒');
			g_scene_main.force_update = true;
			g_scene_main.update();
		}
	}
	button_updfreq_real.onclick = function() {
		g_scene_main.click_ignore = true;
		// 現在時刻＆実時間ボタンが押されたときの処理
		var curDate = new Date();
		var dt = curDate.getFullYear()+'年'+('0'+(curDate.getMonth()+1)).slice(-2)+'月'+('0'+curDate.getDate()).slice(-2)+'日';
		var tm = (' '+curDate.getHours()).slice(-2)+'時'+(' '+curDate.getMinutes()).slice(-2)+'分';
		let answer = true;
		if(! isAndroid) {
			answer = confirm('更新頻度を更新しますか？：実時間(60秒)＆現在時刻：' + dt + ' ' + tm);
		}
		if(answer) {
			g_demo = 0;
			g_update_freauency = 60.0;
			g_current_date = new Date(curDate.getTime() - 60000);
			g_start_date = g_current_date;
			scene.date.text = g_start_date.getFullYear()+'年'+('0'+(g_start_date.getMonth()+1)).slice(-2)+'月'+('0'+g_start_date.getDate()).slice(-2)+'日('+WEEKDAYS[g_start_date.getDay()]+')';
			scene.time.text = (' '+g_start_date.getHours()).slice(-2)+'時'+(' '+g_start_date.getMinutes()).slice(-2)+'分';
			label_updfreq_value.text = g_update_freauency + '秒';
			// console.log('accept updfreq_real, ' + g_update_freauency + '秒, ' + scene.date.text + ' ' + scene.time.text);
			clearAllTrainStatus();
			g_scene_main.force_update = true;
			g_scene_main.update();
		}
	}
	// 時刻設定
	var label_time = Label({
		text: '日時設定：',
		x: 6,
		y: 32 + 38 + 14,
		fontSize: 28,
	}).addChildTo(setup_panel1).setOrigin(0.0, 0.5);
	if(isAndroid) {
		// androidでは動作が停止してしまう！
		var button_date_update = Label({
			text: '日付変更',	// 表示文字
			x: 6 + 16*9,
			y: 32 + 38 + 14,
			fontSize: 24,		// 文字サイズ
			fontColor: 'black',	// 文字色
			fill: 'silver',		// ボタン色
			stroke: 'gray',		// 枠色
		}).addChildTo(setup_panel1).setOrigin(0.0, 0.5);
		var button_time_update = Label({
			text: '時刻変更',	// 表示文字
			x: 6 + 16*9 + 16*9,
			y: 32 + 38 + 14,
			width: 16*8,	// 横サイズ
			height: 32,	// 縦サイズ
			fontSize: 24,		// 文字サイズ
			fontColor: 'black',	// 文字色
			fill: 'silver',		// ボタン色
			stroke: 'gray',		// 枠色
		}).addChildTo(setup_panel1).setOrigin(0.0, 0.5);
	} else {
		var button_date_update = Button({
			text: '日付変更',	// 表示文字
			x: 6 + 16*9,
			y: 32 + 38 + 14,
			width: 16*8,	// 横サイズ
			height: 38,	// 縦サイズ
			fontSize: 24,		// 文字サイズ
			fontColor: 'black',	// 文字色
			cornerRadius: 10,	// 角丸み
			backgroundColor: 'transparent',
			fill: 'silver',		// ボタン色
			stroke: 'gray',		// 枠色
			strokeWidth: 5,		// 枠太さ
		}).addChildTo(setup_panel1).setOrigin(0.0, 0.5).setInteractive(true);
		var button_time_update = Button({
			text: '時刻変更',	// 表示文字
			x: 6 + 16*9 + 16*9,
			y: 32 + 38 + 14,
			width: 16*8,	// 横サイズ
			height: 38,	// 縦サイズ
			fontSize: 24,		// 文字サイズ
			fontColor: 'black',	// 文字色
			cornerRadius: 10,	// 角丸み
			backgroundColor: 'transparent',
			fill: 'silver',		// ボタン色
			stroke: 'gray',		// 枠色
			strokeWidth: 5,		// 枠太さ
		}).addChildTo(setup_panel1).setOrigin(0.0, 0.5);
		button_date_update.onclick = function() {
			g_scene_main.click_ignore = true;
			// 日付ボタンが押されたときの処理
			let answer = prompt('日付を入力して下さい(yyyy-mm-dd)：', g_current_date.getFullYear()+'-'+(g_current_date.getMonth()+1)+'-'+g_current_date.getDate());
			if(answer) {
				if(setCurrentDate(answer)) {
					// console.log('accept date_update, ' + answer);
					g_demo = 1;
					clearAllTrainStatus();
					g_scene_main.force_update = true;
					g_scene_main.update();
				} else {
					alert('日付の形式に誤りがあります。' + answer);
				}
				scene.date.text = g_current_date.getFullYear()+'年'+('0'+(g_current_date.getMonth()+1)).slice(-2)+'月'+('0'+g_current_date.getDate()).slice(-2)+'日('+WEEKDAYS[g_current_date.getDay()]+')';
			}
		}
		button_time_update.onclick = function() {
			g_scene_main.click_ignore = true;
			// 時刻変更ボタンが押されたときの処理
			let answer = prompt('時刻を入力して下さい(hh:mm)：', getCurrentTime(false));
			if(answer) {
				if(setCurrentTime(minusTime(answer, '00:01'))) {
					// console.log('accept time_update, ' + answer);
					g_demo = 1;
					clearAllTrainStatus();
					g_scene_main.force_update = true;
					g_scene_main.update();
				} else {
					alert('時刻の形式に誤りがあります。' + answer);
				}
			}
		}
	}
	var button_balloon_show = Button({
		x: 6,
		y: 28,
		text: '☒ 走行時のバルーン表示',	// 表示文字
		width: 32*11,	// 横サイズ
		height: 32,	// 縦サイズ
		fontSize: 28,		// 文字サイズ
		fontColor: 'black',	// 文字色
		cornerRadius: 10,	// 角丸み
		backgroundColor: 'transparent',
		fill: 'silver',		// ボタン色
		stroke: 'gray',		// 枠色
		strokeWidth: 5,		// 枠太さ
	}).addChildTo(setup_panel2).setOrigin(0.0, 0.5).setInteractive(true);
	button_balloon_show.onclick = function() {
		g_scene_main.click_ignore = true;
		// 走行時バルーン表示ボタンが押されたときの処理
		let answer = true;
		if(! isAndroid) {
			answer = confirm('走行時のバルーン表示を変更しますか？');
		}
		if(answer) {
			if(this.text.substr(0, 1) == '□') {
				this.text = '☒ 走行時のバルーン表示';
				TRAIN_STATUS[TRAIN_RUNNING][TS_BALLOON] = true;
			} else {
				this.text = '□ 走行時のバルーン表示';
				TRAIN_STATUS[TRAIN_RUNNING][TS_BALLOON] = false;
			}
			// console.log('accept balloon_show, ' + this.text);
			g_scene_main.force_update = true;
			g_scene_main.update();
		}
	}
	return true;
}

/*------------------------*/
/* 以降は普通のJavaScript */
/*------------------------*/
// 駅舎の距離を緯度・経度から計算する（単位はKm）
function calcStationsDistance(stations) {
	var distance = {};
	var total_distance = 0;
	for(let i=1; i<STATIONS.length; i++) {
		var d = calcDistance(stations[i][5], stations[i-1][5]);
		distance[(i-1)+'-'+i] = d;
		distance[i+'-'+(i-1)] = d;
		total_distance += d;
	}
	distance['total'] = total_distance;
	// console.log(distance);
	return distance
}
// 駅舎の位置(X)を緯度・経度から計算する
function calcStationsGridX(stations, distance) {
	var panel_distance = distance['total']
			/ (stations[0][2]-stations[stations.length-1][2]);
	var station_distance = 0;
	for(let i=(STATIONS.length-2); i>0; i--) {
		station_distance += distance[i+'-'+(i+1)];
		stations[i][2] = station_distance / panel_distance
				+ stations[stations.length-1][2];
	}
	return stations;
}
function calcDistance(LatLng1, LatLng2) {
	const R = Math.PI / 180;
	return 6371 * Math.acos(
			Math.cos(LatLng1[0]*R) * Math.cos(LatLng2[0]*R)
			* Math.cos(LatLng2[1]*R - LatLng1[1]*R)
			+ Math.sin(LatLng1[0]*R) * Math.sin(LatLng2[0]*R)
	);
}

// 運転日および運転時刻を確認する
function is_operating_datetime(diagram, cDate, cTime) {
	var operation = null;
	var suspension = null;
	var cDate_str = cDate.getFullYear() + ('0'+(cDate.getMonth()+1)).slice(-2) + ('0'+cDate.getDate()).slice(-2);
	if('remarks' in diagram) {
		if('運転日' in diagram['remarks']) {
			if(diagram['remarks']['運転日'].length > 0) {
				operation = (diagram['remarks']['運転日'].indexOf(cDate_str) >= 0);
			}
		}
		if('運休日' in diagram['remarks']) {
			if(diagram['remarks']['運休日'].length > 0) {
				suspension = (diagram['remarks']['運休日'].indexOf(cDate_str) >= 0);
			}
		}
	}
	//             suspension
	// operation   null  false  true
	//      null   運行  運行   運休
	//      false  運休  運休   運休
	//      true   運行  運行   運行
	if(operation == false || (operation == null && suspension == true)) {
		return false;
	}
	if(diagram['property'][1] > cTime
	|| diagram['property'][2] < cTime) {
		return false;
	}
	return true;
}

// 時刻表を取得する
function get_timetable() {
	// console.log('get_timetable() start.');
	var get_url = CACHE_PATH + 'timetables.json';
	var tt_json = '';
	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function() {
		switch ( xhr.readyState ) {
			case 0: // 未初期化状態.
				// console.log('XMLHttpRequest(): uninitialized!');
				break;
			case 1: // データ送信中.
				// console.log('XMLHttpRequest(): loading...');
				break;
			case 2: // 応答待ち.
				// console.log('XMLHttpRequest(): loaded.');
				break;
			case 3: // データ受信中.
				// console.log('XMLHttpRequest(): interactive... ' + xhr.responseText.length + ' bytes.');
				break;
			case 4: // データ受信完了.
				if(xhr.status == 200 || xhr.status == 304) {
					// console.log('XMLHttpRequest(): COMPLETE!');
					tt_json = JSON.parse(xhr.responseText);
				} else {
					alert('時刻表の取得に失敗しました！' + xhr.statusText);
					console.log('XMLHttpRequest(): FAILED! HttpStatus=' + xhr.statusText);
				}
				break;
		}
	}
	xhr.open('GET', get_url, false);
	// xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xhr.setRequestHeader('Access-Control-Allow-Origin', '*');
	xhr.send();
	xhr.abort();
	DIAGRAM_DOWN = tt_json['down'];
	DIAGRAM_UP = tt_json['up'];
	// console.log(DIAGRAM_DOWN);
	// console.log(DIAGRAM_UP);
	// console.log('get_timetable() ended.');
}

// 全列車の状態をクリアする
function clearAllTrainStatus() {
	for(let i=0; i<g_trains_down.length; i++) {
		clearTrainStatus(g_trains_down[i]);
	}
	for(let i=0; i<g_trains_up.length; i++) {
		clearTrainStatus(g_trains_up[i]);
	}
	g_train_down_count = 0;
	g_train_up_count = 0;
	return true;
}
function clearTrainStatus(train) {
	train.status = TRAIN_STATUS[TRAIN_OUTOF_RAIL].slice();
	train.train_location = -1.0;
	train.train_st_id = -1;
	train.balloon.hide();
	train.balloon.setInteractive(false);
	train.hide();
	return true;
}

// 列車を更新する
function updateTrain(train) {
	var show_count = 0;
	var cDate = getCurrentDate(0, 0);
	var cTime = getCurrentTime(false);
	if(!is_operating_datetime(train.diagram, cDate, cTime)) {
		// 走行時間外
		if(train.status[TS_ID] != TRAIN_OUTOF_RAIL) {
			clearTrainStatus(train);
			show_count = -1;
		}
	} else {
		if(train.status[TS_ID] == TRAIN_OUTOF_RAIL) {
			train.status = TRAIN_STATUS[TRAIN_INTO_RAIL].slice();
			train.balloon.hide();
			train.balloon.setInteractive(false);
			train.show();
			show_count = 1;
		}
		var xPos = calcTrainPosition(train);
		if(xPos != -1) {
			train.moveTo(xPos, train.y, 1000);
		}
		if(train.status[TS_BALLOON]) {
			var msg = train.status[TS_MESSAGE];
			msg = msg.replace('{{train}}', train.name_msg);
			msg = msg.replace('{{from}}', train.diagram['property'][3]);
			msg = msg.replace('{{to}}', train.diagram['property'][4]);
			msg = msg.replace('{{station}}', STATIONS[train.status[TS_STATION]][1].replace('\n', ''));
			if(train.status[TS_NEXT] >= 0) {
				msg = msg.replace('{{next}}', STATIONS[train.status[TS_NEXT]][1].replace('\n', ''));
			}
			train.balloon.text = msg;
			train.balloon.show();
			train.balloon.setInteractive(true);
		} else {
			train.balloon.hide();
			train.balloon.setInteractive(false);
		}
	}
	// 列車位置調整、表示列車数
	if(train.diagram['property'][0] == 'down') {
		g_train_down_count += show_count;
	} else {
		g_train_up_count += show_count;
	}
	return 0;
}

// 現在日時を取得する
function getCurrentDate(start, update) {
	var cDate = new Date();
	if(g_demo == 1) {
		if(start == 1) {
			cDate.setHours(5);
			cDate.setMinutes(53);
		} else {
			var diff = cDate.getTime() - g_real_date.getTime();
			cDate.setTime(g_current_date.getTime());
			if((diff/1000) >= g_update_freauency) {
				if(update == 1) {
					cDate.setMinutes(cDate.getMinutes() + 1);
				}
			}
		}
	}
	return cDate;
}

// 現在日付を変更する
function setCurrentDate(dt) {
	var dt_array = dt.split('-');
	if(dt_array.length != 3) {
		// alert('日付の形式に誤りがあるます。' + dt);
		return false;
	}
	if(parseInt(dt_array[0],10) < 1900 || parseInt(dt_array[0],10) > 2099) {
		// alert('日付の形式に誤りがあるます。' + dt);
		return false;
	}
	if(parseInt(dt_array[1],10) < 1 || parseInt(dt_array[1],10) > 12) {
		// alert('日付の形式に誤りがあるます。' + dt);
		return false;
	}
	if(parseInt(dt_array[2],10) < 1 || parseInt(dt_array[2],10) > 31) {
		// alert('日付の形式に誤りがあるます。' + dt);
		return false;
	}
	g_current_date.setFullYear(parseInt(dt_array[0],10));
	g_current_date.setMonth(parseInt(dt_array[1],10)-1);
	g_current_date.setDate(parseInt(dt_array[2],10));
	return true;
}

// 現在時刻を取得する
function getCurrentTime(sec) {
	if(sec) {
		return ('0'+g_current_date.getHours()).slice(-2)
				+':'+('0'+g_current_date.getMinutes()).slice(-2)
				+':'+('0'+g_current_date.getSeconds()).slice(-2);
	} else {
		return ('0'+g_current_date.getHours()).slice(-2)
				+':'+('0'+g_current_date.getMinutes()).slice(-2);
	}
}

// 現在時刻を更新する
function setCurrentTime(tm) {
	var tm_array = tm.split(':');
	if(tm_array.length != 2 && tm_array.length != 3) {
		// alert('時刻の形式に誤りがあるます。' + tm);
		return false;
	}
	if(parseInt(tm_array[0],10) < 0 || parseInt(tm_array[0],10) > 23) {
		// alert('時刻の形式に誤りがあるます。' + tm);
		return false;
	}
	if(parseInt(tm_array[1],10) < 0 || parseInt(tm_array[1],10) > 59) {
		// alert('時刻の形式に誤りがあるます。' + tm);
		return false;
	}
	if(tm_array.length == 3
	&& parseInt(tm_array[2],10) < 0 || parseInt(tm_array[2],10) > 59) {
		// alert('時刻の形式に誤りがあるます。' + tm);
		return false;
	}
	g_current_date.setHours(parseInt(tm_array[0],10));
	g_current_date.setMinutes(parseInt(tm_array[1],10));
	if(tm_array.length == 3) {
		g_current_date.setSeconds(parseInt(tm_array[2],10));
	}
	return true;
}

// 時刻の加算
function plusTime(base, plus) {
	var cTime = new Date();
	var base_hm = base.split(':');
	var plus_hm = plus.split(':');
	cTime.setTime(new Date(cTime.getFullYear(), cTime.getMonth(), cTime.getDate(),
			parseInt(base_hm[0],10)+parseInt(plus_hm[0],10),
			parseInt(base_hm[1],10)+parseInt(plus_hm[1],10), 0).getTime());
	return ('0'+cTime.getHours()).slice(-2)
			+':'+('0'+cTime.getMinutes()).slice(-2);
}

// 時刻の減算
function minusTime(base, minus) {
	var cTime = new Date();
	var base_hm = base.split(':');
	var minus_hm = minus.split(':');
	cTime.setTime(new Date(cTime.getFullYear(), cTime.getMonth(), cTime.getDate(),
			parseInt(base_hm[0],10)-parseInt(minus_hm[0],10),
			parseInt(base_hm[1],10)-parseInt(minus_hm[1],10), 0).getTime());
	return ('0'+cTime.getHours()).slice(-2)
			+':'+('0'+cTime.getMinutes()).slice(-2);
}

// 列車のX座標を求める
function calcTrainPosition(train) {
	var xPos = -1;
	// 現在時刻を取得する
	var cDate = getCurrentDate(0, 0);
	var cTime = getCurrentTime(false);
	// console.log('calcTrainPosition() start, train=' + train.name + ', cTime=' + cTime);
	if(! is_operating_datetime(train.diagram, cDate, cTime)) {
		return xPos;
	}
	var msg = '';
	var st_id = 0;
	for(let tl_i=0; tl_i<train.diagram['timeLine'].length; tl_i++) {
		var st_key = '';
		if(train.diagram['timeLine'][tl_i][1] <= cTime
		&& train.diagram['timeLine'][tl_i][2] >= cTime) {
			// 駅に停車中
			st_id = train.diagram['timeLine'][tl_i][0];
			train.train_st_id = st_id;
			let from_st_id = 0;
			let to_st_id = st_id;
			if(train.diagram['property'][0] == 'up') {
				from_st_id = st_id;
				to_st_id = STATIONS.length - 1;
			}
			train.train_location = 0.0;
			for(let id=from_st_id; id<to_st_id; id++) {
				let key = id + '-' + (id+1);
				train.train_location += STATIONS_DISTANCE[key];
			}
			if(train.diagram['timeLine'][tl_i][3] == 1) {
				// 通過駅
				xPos = g_stations[train.diagram['timeLine'][tl_i][0]].x;
				if(train.diagram['property'][0] == 'up') {
					xPos -= (STATION_SIZE[0]/2) + (GRID_SIZE/2);
				}
				return xPos;
			}
			if(train.diagram['timeLine'][tl_i][2] == cTime
			&& tl_i+1 < train.diagram['timeLine'].length) {
				// 発車
				train.status = TRAIN_STATUS[TRAIN_START].slice();
				msg = '停車中（発車時刻）';
			} else
			if(minusTime(train.diagram['timeLine'][tl_i][2], '0:01') == cTime
			&& tl_i+1 < train.diagram['timeLine'].length) {
				// 発車１分前
				train.status = TRAIN_STATUS[TRAIN_SOON_START].slice();
				msg = '停車中（発車１分前）';
			} else
			if(tl_i == 0) {
				// 始発駅に入線
				train.status = TRAIN_STATUS[TRAIN_INTO_RAIL].slice();
				msg = '停車中（始発駅）';
			} else
			if(tl_i+1 == train.diagram['timeLine'].length
			&& STATIONS[train.diagram['timeLine'][tl_i][0]][1] == train.diagram['property'][4]) {
				// 終着駅に停車中
				train.status = TRAIN_STATUS[TRAIN_ARRIVAL].slice();
				msg = '停車中（終着駅）';
			} else
			if(train.diagram['timeLine'][tl_i][1] == cTime) {
				// 到着
				train.status = TRAIN_STATUS[TRAIN_STOP_STATION].slice();
				msg = '停車中（到着時刻）';
			} else {
				// 停車中
				train.status = TRAIN_STATUS[TRAIN_STOPPING].slice();
				msg = '停車中（停車中）';
			}
			train.status[TS_STATION] = st_id;
			train.status[TS_NEXT] = -1;
			for(let j=tl_i+1; j<train.diagram['timeLine'].length; j++) {
				if(train.diagram['timeLine'][j][3] == 0) {
					train.status[TS_NEXT] = train.diagram['timeLine'][j][0];
					break;
				}
			}
			if(train.diagram['property'][0] == 'up') {
				xPos = g_stations[st_id].x - (STATION_SIZE[0]/2) - (GRID_SIZE/2) - 4;
			} else {
				xPos = g_stations[st_id].x;
			}
			// console.log('stoping xPos=' + xPos + ', ' + train.diagram['timeLine'][tl_i].join(','));
			break;
		} else
		if((tl_i+1) < train.diagram['timeLine'].length) {
			if(train.diagram['timeLine'][tl_i][2] < cTime
			&& cTime < train.diagram['timeLine'][tl_i+1][1]) {
				// 次の駅の間
				st_id = train.diagram['timeLine'][tl_i][0];
				let st_id_next = train.diagram['timeLine'][tl_i+1][0];
				train.train_st_id = st_id;
				for(let j=tl_i+1; j<train.diagram['timeLine'].length; j++) {
					if(train.diagram['timeLine'][j][3] == 0) {
						st_id_next = train.diagram['timeLine'][j][0];
						break;
					}
				}
				if(train.diagram['timeLine'][tl_i+1][3] == 0
				&& minusTime(train.diagram['timeLine'][tl_i+1][1], '0:03') <= cTime) {
					// 到着３分前
					train.status = TRAIN_STATUS[TRAIN_SOON_STOP].slice();
					train.status[TS_TIME] = parseInt(minusTime(cTime,
								minusTime(train.diagram['timeLine'][tl_i+1][1], '0:03')).slice(-1),10);
					if(tl_i+1 == train.diagram['timeLine'].length
					&& STATIONS[train.diagram['timeLine'][tl_i+1][0]][1] == train.diagram['property'][4]) {
						train.status = TRAIN_STATUS[TRAIN_SOON_ARRIVAL].slice();
					}
					msg = '走行中（到着３分前）';
				} else
				if(train.diagram['timeLine'][tl_i][3] == 0
				&& plusTime(train.diagram['timeLine'][tl_i][2], '0:01') == cTime) {
					// 駅を出発直後
					train.status = TRAIN_STATUS[TRAIN_RUNNING].slice();
					msg = '走行中（出発直後）';
				} else {
					// 駅間を走行中
					train.status = TRAIN_STATUS[TRAIN_RUNNING].slice();
					msg = '走行中（駅間を走行中）';
				}
				train.status[TS_STATION] = st_id;
				train.status[TS_NEXT] = st_id_next;
				// 列車の位置を計算する
				let from_st_id = 0;
				let to_st_id = st_id;
				if(train.diagram['property'][0] == 'up') {
					from_st_id = st_id;
					to_st_id = STATIONS.length - 1;
				}
				let new_location = 0.0;
				for(let id=from_st_id; id<to_st_id; id++) {
					let key = id + '-' + (id+1);
					new_location += STATIONS_DISTANCE[key];
				}
				// console.log('new_location(1)=' + new_location);
				from_st_id = st_id;
				to_st_id = st_id_next;
				if(train.diagram['property'][0] == 'up') {
					from_st_id = st_id_next;
					to_st_id = st_id;
				}
				let distance = 0.0;
				for(let id=from_st_id; id<to_st_id; id++) {
					let key = id + '-' + (id+1);
					distance += STATIONS_DISTANCE[key];
				}
				let save_location = new_location;
				xPos_ratio = getPositionByTime(distance,
						train.diagram['timeLine'][tl_i][2],
						train.diagram['timeLine'][tl_i+1][1],
						cTime);
				new_location += xPos_ratio[0];
				if(DEBUG_TRAINS.indexOf(train.name) != -1) {
					console.log(train.name + ': train_location=' + train.train_location + ', new_location=' + new_location + ', train_st_id=' + train.train_st_id + ', save_location=' + save_location + ', distance=' + distance + ', times=(' + train.diagram['timeLine'][tl_i][2] + ',' + train.diagram['timeLine'][tl_i+1][1] + ',' + cTime + ')' + ', xPos_ratio=' + xPos_ratio.join(','));
				}
				let key = st_id + '-' + st_id_next;
				// ToDo:現在のlocationから新ロケーションの間のこだま号が居たら駅で停車中かを確認する！
				if(train.train_location != -1.0) {
					let trains = g_trains_down;
					if(train.diagram['property'][0] == 'up') {
						trains = g_trains_up;
					}
					for(let j=0; j<trains.length; j++) {
						if(trains[j].status[TS_ID] == TRAIN_OUTOF_RAIL
						|| trains[j].name == train.name
						|| trains[j].name.substr(0,3) == 'のぞみ') {
							continue;
						}
						if(trains[j].train_location <= new_location
						&& trains[j].train_location >= train.train_location) {
							// 前方車両を追い抜こうとしている！
							if(DEBUG_TRAINS.indexOf(train.name) != -1) {
								console.log(train.name + 'が' + trains[j].name + 'を追い抜こうとしている！' + ' st=' + STATIONS[st_id][1]);
								console.log(train.name + ': train_location=' + train.train_location + ', new_location=' + new_location + ', train_st_id=' + train.train_st_id + ', key=' + key + ', distance=' + distance);
								console.log(trains[j].name + ': trains[' + j + '].train_location=' + trains[j].train_location + ', train_st_id=' + trains[j].train_st_id + ', status=' + trains[j].status.join(','));
							}
							if((trains[j].status[TS_ID] == TRAIN_SOON_START
							 || trains[j].status[TS_ID] == TRAIN_STOP_STATION
							 || trains[j].status[TS_ID] == TRAIN_STOPPING)
							&& STATIONS[trains[j].status[TS_STATION]][1] != '熱海') {
								// 熱海以外で停車中の列車は追い抜ける！→そのまま
							} else
							if(trains[j].status[TS_ID] == TRAIN_START
							|| trains[j].status[TS_ID] == TRAIN_RUNNING
							|| trains[j].status[TS_ID] == TRAIN_SOON_STOP) {
								// 列車が走行中は抜けない！→2,4,6Km後方に着ける
								new_location = trains[j].train_location - 6;
								if(trains[j].status[TS_ID] == TRAIN_SOON_STOP) {
									new_location = trains[j].train_location - (trains[j].status[TS_TIME] * 2);
								}
								// console.log(train.name + ':' + trains[j].name + 'が走行中は抜けない！→2,4,6Km後方に着ける=' + cTime + ', new_location=' + new_location);
							} else {
								// その他は抜けない！
								new_location = trains[j].train_location - 2;
							}
						} else
						if(trains[j].train_location <= (new_location + 14)
						&& trains[j].train_location >= train.train_location
						&& train.train_st_id != 0
						&& trains[j].status[TS_STATION] != st_id_next
						&& trains[j].status[TS_ID] == TRAIN_SOON_START
						&& (STATIONS[trains[j].status[TS_STATION]][1] != '品川'
						 && STATIONS[trains[j].status[TS_STATION]][1] != '新横浜'
						 && STATIONS[trains[j].status[TS_STATION]][1] != '熱海'
						 && STATIONS[trains[j].status[TS_STATION]][1] != '名古屋')) {
							// 発車前ぎりぎりの場合は抜く！
							new_location = trains[j].train_location + 2;
							if(DEBUG_TRAINS.indexOf(train.name) != -1) {
								console.log(train.name + ':' + trains[j].name + 'が発車前ぎりぎりで抜く！→2Km先に着ける=' + cTime + ', st_id=' + st_id + ', st_id_next=' + st_id_next + ', new_location=' + new_location + ', [j].status=' + trains[j].status.join(','));
							}
						}
					}
				}
				if(new_location >= train.train_location) {
					train.train_location = new_location;
				} else {
					train.train_location += 3;
				}
				let xSpan = g_stations[0].x - g_stations[g_stations.length-1].x;
				xPos = getPositionByLocation(xSpan, train.train_location);
				if(train.diagram['property'][0] == 'up') {
					xPos += g_stations[g_stations.length-1].x - STATION_SIZE[0]/2 - (GRID_SIZE/2) - 4;
				} else {
					xPos = g_stations[0].x - xPos;
				}
				// console.log('running xPos=' + xPos + ', ' + [span, train.diagram['timeLine'][tl_i][2], train.diagram['timeLine'][tl_i+1][1], cTime].join(','));
				break;
			}
		}
	}
	// console.log('calcTrainPosition() ended, ' + train.name + ' ' + train.diagram['property'][0] + ' ' + cTime + ' ' + msg + ', xPos=' + xPos);
	return xPos;
}

// 駅間の描画位置を時間差から求める
function getPositionByTime(span, time1, time2, ctime) {
	// console.log('getPositionByTime() start.');
	var hm1 = time1.split(':');
	var hm2 = time2.split(':');
	var hmc = ctime.split(':');
	var ct = new Date();
	var t1 = new Date(ct.getFullYear(), ct.getMonth(), ct.getDate(),
				parseInt(hm1[0],10), parseInt(hm1[1],10), ct.getSeconds());
	var t2 = new Date(ct.getFullYear(), ct.getMonth(), ct.getDate(),
				parseInt(hm2[0],10), parseInt(hm2[1],10), ct.getSeconds());
	var tc = new Date(ct.getFullYear(), ct.getMonth(), ct.getDate(),
				parseInt(hmc[0],10), parseInt(hmc[1],10), ct.getSeconds());
	var ratio = (tc.getTime() - t1.getTime()) / (t2.getTime() - t1.getTime());
	var xPos = span * ratio;
	// console.log('getPositionByTime() ended, xPos=' + xPos + ', ratio=' + ratio);
	return [xPos, ratio];
}

// 駅間の描画位置を現在距離から求める
function getPositionByLocation(span, loc) {
	// console.log('getPositionByLocation() start.');
	var xPos = span * (loc / STATIONS_DISTANCE['total']);
	// console.log('getPositionByLocation() ended, xPos=' + xPos);
	return xPos;
}

// 駅の時刻表作成
function get_station_taimetable(id, up_down) {
	// console.log('get_station_taimetable() start, id=' + id + ', up_down=' + up_down);
	var diagram = DIAGRAM_DOWN;
	if(up_down == 'up') {
		diagram = DIAGRAM_UP;
	}
	var tt = STATIONS[id][1].replace('\n', '') + '駅 ';
	if(up_down == 'up') {
		tt += '上り';
	} else {
		tt += '下り';
	}
	tt += ' ' + diagram['property'][1] + '～' + diagram['property'][2];
	tt += '\n  時 ｜列車';
	var tt_hm = {};
	var tt_h = {'06': [], '23': []};
	var rem = {};
	for(let key in diagram) {
		if(key == 'property') continue;
		for(let i=0; i<(diagram[key]['timeLine'].length-1); i++) {
			if(diagram[key]['timeLine'][i][0] == id) {
				tt_hm[diagram[key]['timeLine'][i][2]] = [diagram[key]['timeLine'][i][1], key];
			}
		}
	}
	for(const hm of Object.keys(tt_hm).sort()) {
		var hm_array = hm.split(':');
		if(!(hm_array[0] in tt_h)) {
			tt_h[hm_array[0]] = Array();
		}
		tt_h[hm_array[0]].push([hm_array[1], tt_hm[hm][0], tt_hm[hm][1]]);
	}
	for(const h of Object.keys(tt_h).sort()) {
		var tt_m = '';
		for(let i=0; i<tt_h[h].length; i++) {
			if(tt_m != '') {
				tt_m += ' ';
			}
			// tt_m += tt_h[h][i][0] + '(' + tt_h[h][i][2].substr(0,1) + tt_h[h][i][2].substr(0,tt_h[h][i][2].length-1).substr(3,3) + ')';
			tt_m += tt_h[h][i][0] + tt_h[h][i][2].substr(0,1);
			if('remarks' in diagram[tt_h[h][i][2]]) {
				if('事項' in diagram[tt_h[h][i][2]]['remarks']) {
					if(diagram[tt_h[h][i][2]]['remarks']['事項'] != '') {
						tt_m += diagram[tt_h[h][i][2]]['remarks']['事項'].substr(0,1);
						if(diagram[tt_h[h][i][2]]['remarks']['事項'].substr(0,1) == '◆') {
							rem['◆'] = '◆運転日注意';
						} else {
							rem[diagram[tt_h[h][i][2]]['remarks']['事項'].substr(0,1)] = diagram[tt_h[h][i][2]]['remarks']['事項'];
						}
					}
				}
			}
		}
		tt += '\n' + h + '時｜' + tt_m;
	}
	tt += '\n-------';
	for(let key in rem) {
		tt += '\n' + rem[key];
	}
	// console.log('get_station_taimetable() ended, rc=' + tt);
	return tt;
}

// 列車の時刻表作成
function get_train_taimetable(name, up_down) {
	// console.log('get_train_taimetable() start, name=' + name + ', up_down=' + up_down);
	var tt = name;
	var diagram = null;
	if(up_down == 'up') {
		diagram = DIAGRAM_UP;
		tt += ' 上り ';
	} else {
		diagram = DIAGRAM_DOWN;
		tt += ' 下り ';
	}
	tt += diagram[name]['property'][3] + '発 ' + diagram[name]['property'][4] + '行';
	tt += '\n-------';
	for(let i=0; i<diagram[name]['timeLine'].length; i++) {
		if(diagram[name]['timeLine'][i][3] == 1) {
			continue;
		}
		tt += '\n' + ('　　'+STATIONS[diagram[name]['timeLine'][i][0]][1]).slice(-4) + '駅：';
		if(i == 0) {
			tt += '　　　　　';
		} else {
			tt += diagram[name]['timeLine'][i][1] + '着　';
		}
		if(i < (diagram[name]['timeLine'].length-1)) {
			tt += diagram[name]['timeLine'][i][2] + '発';
		}
	}
	tt += '\n-------';
	if('remarks' in diagram[name]) {
		if('事項' in diagram[name]['remarks']) {
			tt += '\n' + diagram[name]['remarks']['事項'];
		}
	}
	// console.log('get_train_taimetable() ended, rc=' + tt);
	return tt;
}
