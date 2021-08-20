// train,js
// phina.js docs：https://phinajs.com/docs/
// phina.js Tips集：https://qiita.com/alkn203/items/bca3222f6b409382fe20
// [phina.js]オブジェクトの操作 -位置、移動、衝突・クリック判定など- について：https://horohorori.com/memo_phina_js/about_object2d/
// 吹き出し：https://github.com/pentamania/phina-talkbubble
// 古い！グループ管理の基本テクニック：https://qiita.com/alkn203/items/8ad0b80175d23d03bd49
// 緯度・経度：https://mapfan.com/map/spots/search
// JRアクセス検索：https://railway.jr-central.co.jp/timetable/nr_doc/search.html
// JR到着列車案内：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti09.html
// JR列車走行位置：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti08.html
// JR個別列車時刻表(こだま)：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti07.html?traintype=2&train=723
// JR個別列車時刻表(ひかり)：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti07.html?traintype=1&train=511
// JR個別列車時刻表(のぞみ)：https://traininfo.jr-central.co.jp/shinkansen/pc/ja/ti07.html?traintype=6&train=31

// phina.js をグローバル領域に展開
phina.globalize();

// 定数
var SCREEN_WIDTH  = 1920;	// 画面横サイズ(document.documentElement.clientWidth)
var SCREEN_HEIGHT = 992;	// 画面縦サイズ(document.documentElement.clientHeight)
var GRID_SIZE = 32;			// グリッドのサイズ
var PANEL_SIZE = GRID_SIZE;	// パネルの大きさ
var PANEL_OFFSET_X = GRID_SIZE*2;	// オフセット値
var PANEL_OFFSET_Y = 0;		// オフセット値
var PANEL_NUM_X = (SCREEN_WIDTH  - PANEL_OFFSET_X*2 - GRID_SIZE) / GRID_SIZE;	// 横のパネル数
var PANEL_NUM_Y = (SCREEN_HEIGHT - PANEL_OFFSET_Y*2 - GRID_SIZE) / GRID_SIZE;	// 縦のパネル数
var LINE_POS_Y = [21, 22];	// 線路のパネル位置縦
var TRAIN_UP = 20;			// 上り
var TRAIN_DOWN = 21;		// 下り
var STATION_Y = 6;			// 駅舎の縦位置
var STATION_SIZE = 64;		// 駅舎のサイズ
var STATIONS = [			// 駅舎情報 ID,駅名,X
	[ 0, '東京',		PANEL_NUM_X-1,				STATION_Y, 6, [35.6809591, 139.7673068], 0, 0],
	[ 1, '品川',		((PANEL_NUM_X-3)/16)*15+2,	STATION_Y, 4, [35.6291112, 139.7389313], 0, 0],
	[ 2, '新横浜',		((PANEL_NUM_X-3)/16)*14+2,	STATION_Y, 4, [35.5067084, 139.6168805], 0, 0],
	[ 3, '小田原',		((PANEL_NUM_X-3)/16)*13+2,	STATION_Y, 4, [35.2562557, 139.1554675], 0, 0],
	[ 4, '熱海',		((PANEL_NUM_X-3)/16)*12+2,	STATION_Y, 2, [35.0415591, 139.1696865], 0, 0],
	[ 5, '三島',		((PANEL_NUM_X-3)/16)*11+2,	STATION_Y, 4, [35.126334,  138.9107634], 0, 0],
	[ 6, '新富士',		((PANEL_NUM_X-3)/16)*10+2,	STATION_Y, 4, [35.1420718, 138.6633979], 0, 0],
	[ 7, '静岡',		((PANEL_NUM_X-3)/16)*9+2,	STATION_Y, 4, [34.971698,  138.3890637], 0, 0],
	[ 8, '掛川',		((PANEL_NUM_X-3)/16)*8+2,	STATION_Y, 4, [34.7690914, 138.0146393], 0, 0],
	[ 9, '浜松',		((PANEL_NUM_X-3)/16)*7+2,	STATION_Y, 4, [34.7038438, 137.7349526], 0, 0],
	[10, '豊橋',		((PANEL_NUM_X-3)/16)*6+2,	STATION_Y, 4, [34.7629443, 137.3820671], 0, 0],
	[11, '三河安城',	((PANEL_NUM_X-3)/16)*5+2,	STATION_Y, 4, [34.9689643, 137.0604602], 0, 0],
	[12, '名古屋',		((PANEL_NUM_X-3)/16)*4+2,	STATION_Y, 4, [35.1706431, 136.8816945], 0, 0],
	[13, '岐阜羽島',	((PANEL_NUM_X-3)/16)*3+2,	STATION_Y, 4, [35.3156608, 136.6856194], 0, 0],
	[14, '米原',		((PANEL_NUM_X-3)/16)*2+2,	STATION_Y, 4, [35.3144414, 136.2897051], 0, 0],
	[15, '京都',		((PANEL_NUM_X-3)/16)*1+2,	STATION_Y, 4, [34.9851603, 135.7584294], 0, 0],
	[16, '新大阪',		2,							STATION_Y, 8, [34.7338219, 135.5014056], 0, 0],
];
var DIAGRAM_DOWN = {		// 下り時刻表
	'property': ['down', 20210701, 20210731],
	'こだま707号': {
		'property': ['down', '07:52', '11:56', '東京', '新大阪'],
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
	[0, false, '', 0, 1],
	[1, true, '{{train}}\n{{to}}行きです', 0, 1],
	[2, true, '{{train}}\n間もなく発車します', 0, 1],
	[3, true, '{{train}}\n次は{{next}}に止まります', 0, 1],
	[4, true, '{{train}}', 0, 1],
	[5, true, '{{train}}\n間もなく{{next}}です', 0, 1],
	[6, true, '{{train}}\n{{station}}です', 0, 1],
	[7, true, '{{train}}\n{{station}}です', 0, 1],
	[8, true, '{{train}}\n間もなく終点{{to}}です', 0, 1],
	[9, true, '{{train}}\n終点{{to}}です', 0, 1]
];
var TRAIN_OUTOF_RAIL   = 0;
var TRAIN_INTO_RAIL    = 1;
var TRAIN_SOON_START   = 2;
var TRAIN_START        = 3;
var TRAIN_RUNNING      = 4;
var TRAIN_SOON_STOP    = 5;
var TRAIN_STOP_STATION = 6;
var TRAIN_STOPPING     = 7;
var TRAIN_SOON_ARRIVAL = 8;
var TRAIN_ARRIVAL      = 9;
var ASSETS = {
	image: {
		'line':		'images/線路01.gif',
		'300up':	'images/300系上り.gif',
		'300down':	'images/300系下り.gif',
		'balloon_1':	'images/balloon_下り.png',
		'balloon_2':	'images/balloon_上り.png',
	},
}

// グローバル変数
var game_app = null;
var demo = 1;
var startDate = getCurrentDate(1);
var currentDate = startDate;
console.log('start:' + getCurrentTime(true));
var stations = [];
var trains = [];
// グリッド
var grid = Grid(GRID_SIZE * PANEL_NUM_X, PANEL_NUM_X);
// 列車数を初期化
var train_down_count = 0;
var train_up_count = 0;

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
			// グループ作成
			var groupPanel = DisplayElement().addChildTo(this);
			var groupStation = DisplayElement().addChildTo(this);
			var groupLine = DisplayElement().addChildTo(this);
			this.groupTrain = DisplayElement().addChildTo(this);
			// タイトル表示
			this.title = Label('東海道新幹線運行シミュレーター').addChildTo(this);
			this.title.x = grid.span(PANEL_NUM_X/2) + PANEL_OFFSET_X;
			this.title.y = grid.span(1) + PANEL_OFFSET_Y;
			this.date = Label(startDate.getFullYear()+'年'+('0'+(startDate.getMonth()+1)).slice(-2)+'月'+('0'+startDate.getDate()).slice(-2)+'日').addChildTo(this);
			this.date.align = 'right';
			this.date.x = grid.span(PANEL_NUM_X) + PANEL_OFFSET_X;
			this.date.y = grid.span(2) + PANEL_OFFSET_Y;
			this.time = Label((' '+startDate.getHours()).slice(-2)+'時'+(' '+startDate.getMinutes()).slice(-2)+'分').addChildTo(this);
			this.time.align = 'right';
			this.time.x = grid.span(PANEL_NUM_X) + PANEL_OFFSET_X;
			this.time.y = grid.span(3) + PANEL_OFFSET_Y;
			// 列車数表示
			this.train_count = Label('下り：0  上り：0').addChildTo(this);
			this.train_count.x = grid.span(PANEL_NUM_X/2) + PANEL_OFFSET_X;
			this.train_count.y = grid.span(3) + PANEL_OFFSET_Y;

			// 駅舎を表示する
			for(i=0; i<STATIONS.length; i++) {
				var station = Station(STATIONS[i], groupLine).addChildTo(groupStation);
				stations.push(station);
			}

			// グリッドにパネル配置
			PANEL_NUM_X.times(function(spanX) {
				var xG = spanX + 1;
				PANEL_NUM_Y.times(function(spanY) {
					var yG = spanY + 1;
					// パネル作成
					var panel = Panel().addChildTo(groupPanel);
					// Gridを利用して配置
					// panel.setOrigin(0, 0);
					panel.x = grid.span(xG) + PANEL_OFFSET_X;
					panel.y = grid.span(yG) + PANEL_OFFSET_Y;
					// パネルに線路を描画する
					panel.isLine = false;
					// if(LINE_POS_Y.indexOf(yG + 1) >= 0 && spanX >= (PANEL_OFFSET_X / GRID_SIZE)) {
					if(LINE_POS_Y.indexOf(yG + 1) >= 0 && (spanX > 0 && spanX < (PANEL_NUM_X - 1))) {
						panel.isLine = true;
					}
					if(panel.isLine) {
						Sprite('line').addChildTo(groupLine).setPosition(panel.x - PANEL_SIZE/4, panel.y - PANEL_SIZE/2);
						Sprite('line').addChildTo(groupLine).setPosition(panel.x + PANEL_SIZE/4, panel.y - PANEL_SIZE/2);
						// Sprite('line').addChildTo(groupLine).setPosition(panel.x, panel.y);
						// Sprite('line').addChildTo(groupLine).setPosition(panel.x + PANEL_SIZE/2, panel.y);
					}
				});
			});
			// 時刻表を取得する
			get_timetable();
			// のぞみの列車数：吹き出しの位置調整用
			this.down_nozomi_count = 0;
			this.up_nozomi_count = 0;
			// 設定ボタン作成
/*
			var chkAndroid = navigator.userAgent.indexOf("Android") > 0;
			var button = Button({
				x: grid.span(PANEL_NUM_X) + PANEL_OFFSET_X + (GRID_SIZE/2)*3,	// x座標
				y: grid.span(3) + PANEL_OFFSET_Y,	// y座標
				width: GRID_SIZE*2,	// 横サイズ
				height: GRID_SIZE,	// 縦サイズ
				text: '設定',		// 表示文字
				fontSize: 28,		// 文字サイズ
				fontColor: 'black',	// 文字色
				cornerRadius: 10,	// 角丸み
				fill: 'silver',		// ボタン色
				stroke: 'gray',		// 枠色
				strokeWidth: 5,		// 枠太さ
			}).addChildTo(this);
			button.onpointend = function() {
				// ボタンが押されたときの処理
				document.getElementById('setup_dialog').style.visibility = 'visible';
			}
			button.onpointover = function(e){
				// Android端末使用時のタップ遅延対策
				if (!e.pointer.getPointing() && chkAndroid) {
					this.onpointend();
				}
			}
*/
		},
		// 更新
		update: function() {
			// 現在時刻を更新
			currentDate = getCurrentDate(0);
			var cTime = getCurrentTime(true);
			var hm = cTime.split(':');
			this.time.text = hm[0]+'時'+hm[1]+'分';
			console.log('MainScene.update: ' + cTime);
			// 列車数を更新
			this.train_count.text = '下り：' + train_down_count + '  上り：' + train_up_count;
			// 下り列車を更新
			for(let key in DIAGRAM_DOWN) {
				if(key == 'property') continue;
				// console.log(key + '.diagram.property:' + DIAGRAM_DOWN[key]['property'].join(','));
				if(DIAGRAM_DOWN[key]['status'][0] != null) continue;
				if(DIAGRAM_DOWN[key]['property'][1] > cTime
				|| DIAGRAM_DOWN[key]['property'][2] < cTime) continue;
				if(key.substr(0, 3) == 'のぞみ') {
					this.down_nozomi_count++;
				}
				console.log('MainScene.update Train_down:' + DIAGRAM_DOWN[key]['property'].join(','));
				Train_down(key, this.down_nozomi_count).addChildTo(this.groupTrain);
			}
			// 上り列車を更新
			for(let key in DIAGRAM_UP) {
				if(key == 'property') continue;
				// console.log(key + '.diagram.property:' + DIAGRAM_UP[key]['property'].join(','));
				if(DIAGRAM_UP[key]['status'][0] != null) continue;
				if(DIAGRAM_UP[key]['property'][1] > cTime
				|| DIAGRAM_UP[key]['property'][2] < cTime) continue;
				if(key.substr(0, 3) == 'のぞみ') {
					this.up_nozomi_count++;
				}
				console.log('MainScene.update Train_up:' + DIAGRAM_UP[key]['property'].join(','));
				Train_up(key, this.up_nozomi_count).addChildTo(this.groupTrain);
			}
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

// 下り列車クラス
phina.define('Train_down', {
	// Shapeを継承
	superClass: 'Shape',
		// コンストラクタ
		init: function(name, count) {
			// 親クラス初期化
			this.superInit({
				width: GRID_SIZE,
				height: GRID_SIZE,
				backgroundColor: 'transparent',
			});
			this.name = name;
			this.diagram = DIAGRAM_DOWN[this.name];
			this.diagram['status'][0] = null;
			DIAGRAM_DOWN[this.name]['status'][0] = this;
			// イメージ表示
			this.x = grid.span(PANEL_NUM_X - 1) + PANEL_OFFSET_X;
			this.y = grid.span(TRAIN_DOWN - 1) + PANEL_OFFSET_Y;
			var sprite = Sprite('300down').addChildTo(this).origin.set(0.5, 0.5);
			// テキスト入りフキダシ
			var balloon_color = "khaki";	// khaki=#f0e68c
			var tipProtrusion = 32;
			var posY = 120;
			if(this.name.substr(0, 3) == 'のぞみ') {
				if((count % 2) == 1) {
					tipProtrusion += 64;
					posY += 64;
				}
			} else if(this.name.substr(0, 3) == 'ひかり') {
				balloon_color = "tomato";	// tomato=#ff6347
				tipProtrusion += 128;
				posY += 128;
			} else if(this.name.substr(0, 3) == 'こだま') {
				balloon_color = "lightsteelblue";	// lightsteelblue=#e6e6fa
				tipProtrusion += 192;
				posY += 192;
			}
			this.balloon = phina.ui.TalkBubbleLabel({
				text: '',
				tipDirection: 'top',
				tipProtrusion: tipProtrusion,
				tipBottomSize: 24,
				bubbleFill: balloon_color,
			}).addChildTo(this).setPosition(0, posY);
			this.balloon.fontFamily = 'sans-serif';
			this.balloon.fontSize = 12;
			// 列車位置調整：下り列車数
			train_down_count += updateTrain(this, DIAGRAM_DOWN);
		},
		// 更新
		update: function() {
			// console.log('Train_down.update');
			// 列車位置調整：下り列車数
			train_down_count += updateTrain(this, DIAGRAM_DOWN);
		},
});

// 上り列車クラス
phina.define('Train_up', {
	// Shapeを継承
	superClass: 'Shape',
		// コンストラクタ
		init: function(name, count) {
			// 親クラス初期化
			this.superInit({
				width: GRID_SIZE,
				height: GRID_SIZE,
				backgroundColor: 'transparent',
			});
			this.name = name;
			this.diagram = DIAGRAM_UP[this.name];
			this.diagram['status'][0] = null;
			DIAGRAM_UP[this.name]['status'][0] = this;
			// イメージ表示
			this.y = grid.span(TRAIN_UP - 1) + PANEL_OFFSET_Y;
			var sprite = Sprite('300up').addChildTo(this).origin.set(-1.0, 0.5);
			// テキスト入りフキダシ
			var balloon_color = "khaki";	// khaki=#f0e68c
			var tipProtrusion = 32;
			var posY = -96;
			if(this.name.substr(0, 3) == 'のぞみ') {
				if((count % 2) == 0) {
					tipProtrusion += 64;
					posY -= 64;
				}
			} else if(this.name.substr(0, 3) == 'ひかり') {
				balloon_color = "tomato";	// tomato=#ff6347
				tipProtrusion += 128;
				posY -= 128;
			} else if(this.name.substr(0, 3) == 'こだま') {
				balloon_color = "lightsteelblue";	// lightsteelblue=#e6e6fa
				tipProtrusion += 192;
				posY -= 192;
			}
			this.balloon = phina.ui.TalkBubbleLabel({
				text: '',
				tipDirection: 'bottom',
				tipProtrusion: tipProtrusion,
				tipBottomSize: 24,
				bubbleFill: balloon_color,
			}).addChildTo(this).setPosition(58, posY);
			this.balloon.fontFamily = 'sans-serif';
			this.balloon.fontSize = 12;
			// 列車位置調整：上り列車数
			train_up_count += updateTrain(this, DIAGRAM_UP);
		},
		// 更新
		update: function() {
			// console.log('Train_up.update');
			// 列車位置調整：上り列車数
			train_up_count += updateTrain(this, DIAGRAM_UP);
		},
});

// 駅舎クラス
phina.define('Station', {
	// RectangleShapeを継承
	superClass: 'RectangleShape',
		// コンストラクタ
		init: function(st, groupLine) {
			var id = st[0];
			var name = st[1];
			var x = st[2];
			var y = st[3];
			var homes = st[4];
			// 親クラス初期化
			this.superInit({
				width: STATION_SIZE,
				height: STATION_SIZE*2,
				fill: 'white',		// 塗りつぶし色
				stroke: 'black',	// 枠の色
				cornerRadius: 2,	// 角の丸み
			});
			this.x = grid.span(x) + PANEL_OFFSET_X;
			this.y = grid.span(y) + PANEL_OFFSET_Y;
			// 駅名表示
			var label = Label(name.split('').join('\n')).addChildTo(this);
			label.fontFamily = 'sans-serif';
			label.fontSize = 26;
			label.fill = 'black';
			// ホームを表示
			var home = Shape({
				width: PANEL_SIZE,
				height: PANEL_SIZE,
				stroke: 'black',
				backgroundColor: 'peru',	// peru=#cd853f
			}).addChildTo(this).setPosition(0, (LINE_POS_Y[0]-STATION_Y-1)*PANEL_SIZE);
			// パネルにホームを描画する
			if(homes > 2) {
				for(var i=1; i<(homes/2); i++) {
					// 上り用
					var xL = grid.span(x) + PANEL_OFFSET_X;
					var yL = grid.span(LINE_POS_Y[0] - i - 1) + PANEL_OFFSET_Y;
					Sprite('line').addChildTo(groupLine).setPosition(xL - PANEL_SIZE/4, yL - PANEL_SIZE/2);
					Sprite('line').addChildTo(groupLine).setPosition(xL + PANEL_SIZE/4, yL - PANEL_SIZE/2);
					if(id != 0) {
						Sprite('line').addChildTo(groupLine).setPosition(xL + PANEL_SIZE/2, yL - PANEL_SIZE/2).setRotation(90);
						Sprite('line').addChildTo(groupLine).setPosition(xL + PANEL_SIZE/2, yL - PANEL_SIZE/2 + (PANEL_SIZE/2*1)).setRotation(90);
//						Sprite('line').addChildTo(groupLine).setPosition(xL + PANEL_SIZE/2, yL - PANEL_SIZE/2 + (PANEL_SIZE/2*2)).setRotation(90);
//						Sprite('line').addChildTo(groupLine).setPosition(xL + PANEL_SIZE/2, yL - PANEL_SIZE/2 + (PANEL_SIZE/2*3)).setRotation(90);
					}
					if(id != 16) {
						Sprite('line').addChildTo(groupLine).setPosition(xL-(PANEL_SIZE/4)*3, yL - PANEL_SIZE/2).setRotation(90);
						Sprite('line').addChildTo(groupLine).setPosition(xL-(PANEL_SIZE/4)*3, yL - PANEL_SIZE/2 + (PANEL_SIZE/2*1)).setRotation(90);
//						Sprite('line').addChildTo(groupLine).setPosition(xL-(PANEL_SIZE/4)*3, yL - PANEL_SIZE/2 + (PANEL_SIZE/2*2)).setRotation(90);
//						Sprite('line').addChildTo(groupLine).setPosition(xL-(PANEL_SIZE/4)*3, yL - PANEL_SIZE/2 + (PANEL_SIZE/2*3)).setRotation(90);
					}
					// 下り用
					xL = grid.span(x) + PANEL_OFFSET_X;
					yL = grid.span(LINE_POS_Y[1] + i - 2) + PANEL_OFFSET_Y;
					Sprite('line').addChildTo(groupLine).setPosition(xL - PANEL_SIZE/4, yL + PANEL_SIZE/2);
					Sprite('line').addChildTo(groupLine).setPosition(xL + PANEL_SIZE/4, yL + PANEL_SIZE/2);
					if(id != 0) {
						Sprite('line').addChildTo(groupLine).setPosition(xL + PANEL_SIZE/2, yL + PANEL_SIZE/2 - PANEL_SIZE/4).setRotation(90);
						Sprite('line').addChildTo(groupLine).setPosition(xL + PANEL_SIZE/2, yL + PANEL_SIZE/2 - PANEL_SIZE/4 - (PANEL_SIZE/2*1)).setRotation(90);
//						Sprite('line').addChildTo(groupLine).setPosition(xL + PANEL_SIZE/2, yL + PANEL_SIZE/2 - PANEL_SIZE/4 - (PANEL_SIZE/2*2)).setRotation(90);
//						Sprite('line').addChildTo(groupLine).setPosition(xL + PANEL_SIZE/2, yL + PANEL_SIZE/2 - PANEL_SIZE/4 - (PANEL_SIZE/2*3)).setRotation(90);
					}
					if(id != 16) {
						Sprite('line').addChildTo(groupLine).setPosition(xL-(PANEL_SIZE/4)*3, yL + PANEL_SIZE/2 - PANEL_SIZE/4).setRotation(90);
						Sprite('line').addChildTo(groupLine).setPosition(xL-(PANEL_SIZE/4)*3, yL + PANEL_SIZE/2 - PANEL_SIZE/4 - (PANEL_SIZE/2*1)).setRotation(90);
//						Sprite('line').addChildTo(groupLine).setPosition(xL-(PANEL_SIZE/4)*3, yL + PANEL_SIZE/2 - PANEL_SIZE/4 - (PANEL_SIZE/2*2)).setRotation(90);
//						Sprite('line').addChildTo(groupLine).setPosition(xL-(PANEL_SIZE/4)*3, yL + PANEL_SIZE/2 - PANEL_SIZE/4 - (PANEL_SIZE/2*3)).setRotation(90);
					}
				}
			}
		},
});

// メイン処理
phina.main(function() {
	// アプリケーション生成
	game_app = GameApp({
		title: '東海道新幹線運行シミュレーター',
		fps: 0.5,				// fps指定
		startLabel: 'main',		// メインシーンから開始する
		width: SCREEN_WIDTH + GRID_SIZE,
		height: SCREEN_HEIGHT + GRID_SIZE,
		assets: ASSETS,
	});
	// アプリケーション実行
	game_app.run();
});


// 時刻表を取得する
function get_timetable() {
	console.log('get_timetable() start.');
	var get_url = './timetables.json';
	var tt_json = '';
	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function() {
		switch ( xhr.readyState ) {
			case 0: // 未初期化状態.
				console.log('XMLHttpRequest(): uninitialized!');
				break;
			case 1: // データ送信中.
				console.log('XMLHttpRequest(): loading...');
				break;
			case 2: // 応答待ち.
				console.log('XMLHttpRequest(): loaded.');
				break;
			case 3: // データ受信中.
				console.log('XMLHttpRequest(): interactive... ' + xhr.responseText.length + ' bytes.');
				break;
			case 4: // データ受信完了.
				if(xhr.status == 200 || xhr.status == 304) {
					console.log('XMLHttpRequest(): COMPLETE!');
					tt_json = JSON.parse(xhr.responseText);
				} else {
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
	console.log('get_timetable() ended.');
}

// 列車を更新する
function updateTrain(train, diagram) {
	var rc = 0;
	var cTime = getCurrentTime(false);
	if(train.diagram['property'][1] > cTime
	|| train.diagram['property'][2] < cTime) {
		if(train.diagram['status'][0] != null) {
			diagram[train.name]['status'][0] = null;
			train.diagram['status'][0] = null;
			train.status = TRAIN_STATUS[TRAIN_OUTOF_RAIL];
			train.balloon.hide();
			train.hide();
			rc = -1;
		}
	} else {
		if(train.diagram['status'][0] == null) {
			train.diagram['status'][0] = train;
			train.balloon.hide();
			train.show();
			rc = 1;
		}
		var xPos = calcTrainPosition(train);
		if(xPos != -1) {
			train.moveTo(xPos, train.y, 1000);
		}
		if(train.status[1]) {
			var msg = train.status[2];
			msg = msg.replace('{{train}}', train.name);
			msg = msg.replace('{{from}}', train.diagram['property'][3]);
			msg = msg.replace('{{to}}', train.diagram['property'][4]);
			msg = msg.replace('{{station}}', STATIONS[train.status[3]][1].replace('\n', ''));
			if(train.status[4] >= 0) {
				msg = msg.replace('{{next}}', STATIONS[train.status[4]][1].replace('\n', ''));
			}
			train.balloon.text = msg;
			train.balloon.show();
		} else {
			train.balloon.hide();
		}
	}
	return rc;
}

// 現在日時を取得する
function getCurrentDate(start) {
	var cDate = new Date();
	if(demo == 1) {
		if(start == 1) {
			cDate.setHours(5);
			cDate.setMinutes(53);
		} else {
			cDate = currentDate;
			cDate.setMinutes(cDate.getMinutes() + 1);
		}
	}
	return cDate;
}

// 現在時刻を取得する
function getCurrentTime(sec) {
	if(sec) {
		return ('0'+currentDate.getHours()).slice(-2)
				+':'+('0'+currentDate.getMinutes()).slice(-2)
				+':'+('0'+currentDate.getSeconds()).slice(-2);
	} else {
		return ('0'+currentDate.getHours()).slice(-2)
				+':'+('0'+currentDate.getMinutes()).slice(-2);
	}
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
	var cTime = getCurrentTime(false);
	// console.log('calcTrainPosition() start, train=' + train.name + ', cTime=' + cTime);
	if(train.diagram['property'][1] > cTime
	|| train.diagram['property'][2] < cTime) {
		return xPos;
	}
	var msg = '';
	var st_id = 0;
	for(var i=0; i<train.diagram['timeLine'].length; i++) {
		if(train.diagram['timeLine'][i][1] <= cTime
		&& train.diagram['timeLine'][i][2] >= cTime) {
			// 駅に停車中
			st_id = train.diagram['timeLine'][i][0];
			if(train.diagram['timeLine'][i][2] == cTime
			&& i+1 < train.diagram['timeLine'].length) {
				// 発車
				train.status = TRAIN_STATUS[TRAIN_START];
				msg = '停車中（発車時刻）';
			} else
			if(minusTime(train.diagram['timeLine'][i][2], '0:01') == cTime
			&& i+1 < train.diagram['timeLine'].length) {
				// 発車１分前
				train.status = TRAIN_STATUS[TRAIN_SOON_START];
				msg = '停車中（発車１分前）';
			} else
			if(i == 0) {
				// 始発駅に入線
				train.status = TRAIN_STATUS[TRAIN_INTO_RAIL];
				msg = '停車中（始発駅）';
			} else
			if(i+1 == train.diagram['timeLine'].length
			&& STATIONS[train.diagram['timeLine'][i][0]][1] == train.diagram['property'][4]) {
				// 終着駅に停車中
				train.status = TRAIN_STATUS[TRAIN_ARRIVAL];
				msg = '停車中（終着駅）';
			} else
			if(train.diagram['timeLine'][i][1] == cTime) {
				// 到着
				train.status = TRAIN_STATUS[TRAIN_STOP_STATION];
				msg = '停車中（到着時刻）';
			} else {
				// 停車中
				train.status = TRAIN_STATUS[TRAIN_STOPPING];
				msg = '停車中（停車中）';
			}
			train.status[3] = st_id;
			train.status[4] = -1;
			if(i+1 < train.diagram['timeLine'].length) {
				train.status[4] = train.diagram['timeLine'][i+1][0];
			}
			if(train.diagram['property'][0] == 'up') {
				xPos = stations[st_id].x - (STATION_SIZE/2) - (GRID_SIZE/2);
			} else {
				xPos = stations[st_id].x;
			}
			// console.log('stoping xPos=' + xPos + ', ' + train.diagram['timeLine'][i].join(','));
			break;
		} else if(i+1 < train.diagram['timeLine'].length) {
			if(train.diagram['timeLine'][i][2] < cTime
			&& train.diagram['timeLine'][i+1][1] > cTime) {
				// 次の駅の間
				st_id = train.diagram['timeLine'][i][0];
				if(minusTime(train.diagram['timeLine'][i+1][1], '0:03') <= cTime) {
					// 到着３分前
					train.status = TRAIN_STATUS[TRAIN_SOON_STOP];
					if(i+1 == train.diagram['timeLine'].length
					&& STATIONS[train.diagram['timeLine'][i+1][0]][1] == train.diagram['property'][4]) {
						train.status = TRAIN_STATUS[TRAIN_SOON_ARRIVAL];
					}
					msg = '走行中（到着３分前）';
				} else
				if(plusTime(train.diagram['timeLine'][i][2], '0:01') == cTime) {
					// 駅を出発直後
					train.status = TRAIN_STATUS[TRAIN_RUNNING];
					msg = '走行中（出発直後）';
				} else {
					// 駅間を走行中
					train.status = TRAIN_STATUS[TRAIN_RUNNING];
					msg = '走行中（駅間を走行中）';
				}
				train.status[3] = st_id;
				train.status[4] = train.diagram['timeLine'][i+1][0];
				var st_id2 = train.diagram['timeLine'][i+1][0];
				var xPos1 = stations[st_id].x;
				var xPos2 = stations[st_id2].x;
				var span = xPos2 - xPos1 - 1;
				if(train.diagram['property'][0] == 'down') {
					span = xPos1 - xPos2 - 1;
				}
				xPos = getPositionTime(span,
						train.diagram['timeLine'][i][2],
						train.diagram['timeLine'][i+1][1],
						cTime
				);
				if(train.diagram['property'][0] == 'up') {
					xPos += stations[st_id].x - (STATION_SIZE/2) - (GRID_SIZE/2);
				} else {
					xPos = stations[st_id].x - xPos;
				}
				// console.log('running xPos=' + xPos + ', ' + [span, train.diagram['timeLine'][i][2], train.diagram['timeLine'][i+1][1], cTime].join(','));
				break;
			}
		}
	}
	// console.log('calcTrainPosition() ended, ' + train.name + ' ' + train.diagram['property'][0] + ' ' + cTime + ' ' + msg + ', xPos=' + xPos);
	return xPos;
}

// 駅間の場所を求める
function getPositionTime(span, time1, time2, ctime) {
	// console.log('getPositionTime() start.');
	var hm1 = time1.split(':');
	var hm2 = time2.split(':');
	var hmc = ctime.split(':');
	var ct = new Date();
	var t1 = new Date(ct.getFullYear(), ct.getMonth(), ct.getDate(),
				parseInt(hm1[0],10), parseInt(hm1[1],10)+1, ct.getSeconds());
	var t2 = new Date(ct.getFullYear(), ct.getMonth(), ct.getDate(),
				parseInt(hm2[0],10), parseInt(hm2[1],10)+1, ct.getSeconds());
	var tc = new Date(ct.getFullYear(), ct.getMonth(), ct.getDate(),
				parseInt(hmc[0],10), parseInt(hmc[1],10)+1, ct.getSeconds());
	var xPos = span * ((tc.getTime() - t1.getTime()) / (t2.getTime() - t1.getTime()));
	// console.log('getPositionTime() ended, xPos=' + xPos);
	return xPos;
}
