#!/bin/bash
# get.sh: 時刻表作成を実行する
# Copyright (C) N.Togashi 2021

# 初期設定
OPTIONS="-j"

# パラメタチェック
function print_usage {
    rc=$1
    echo 'Usage: get.sh [-h] [-j|-t]' 1>&2
    echo '              -h：この使用方法を出力する。' 1>&2
    echo '              -j：JSON形式のデータを取得する。省略時の指定です。' 1>&2
    echo '              -t：HTML形式のデータを取得する。' 1>&2
    echo '              記事ファイルパス：時刻表の記事ファイルのパスを指定する。' 1>&2
    echo '                                省略時はremarksディレクトリ内の該当ファイルを探す。' 1>&2
    echo 'Note: 事前に時刻表の記事ファイルをremarksディレクトリ内に格納してください。' 1>&2
    echo '      このコマンドは毎日実行する必要があります。' 1>&2
    exit $rc
}
if [ "$1" == "-h" ]; then
    print_usage 0
fi
if [ "$1" == "-j" ]; then
    OPTIONS="-j"
    shift
fi
if [ "$1" == "-t" ]; then
    OPTIONS=""
    shift
fi
if [ $# != 0 ]; then
    echo 'ERR: パラメタの指定に誤りがあります。' 1>&2
    print_usage 0
fi

# 実行
current_dir=`pwd`
if [ "$current_dir" == "/app" ]; then
    cd /app/shinkansen_simulator/timetable
fi
python3 -u src/get_timetable.py ${OPTIONS}
rc=$?
if [ $rc == 0 ]; then
    if [ "$current_dir" == "/app" ]; then
        cp -p output/`ls -t output/ | head -n 1` /app/cache/timetables.json
        cp_rc=$?
        if [ $cp_rc == 0 ]; then
            echo "INFO: 時刻表を置き換えました。`ls -l /app/cache/timetables.json`" 1>&2
        fi
    fi
fi
cd $current_dir

# 復帰
exit $rc
