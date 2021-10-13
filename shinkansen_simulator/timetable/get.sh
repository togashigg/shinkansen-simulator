#!/bin/bash
# get.sh: 時刻表作成を実行する
# Copyright (C) N.Togashi 2021

# パラメタチェック
if [ $# != 2 ]; then
    echo "ERR: パラメタの指定に誤りがあります。$@" 1>&2
    echo 'Usage: get.sh 時刻表開始日 時刻表終了日' 1>&2
    echo '              時刻表開始日：時刻表の有効期間の開始日でYYYYMMDDの形式で指定する。' 1>&2
    echo '              時刻表終了日：時刻表の有効期間の終了日でYYYYMMDDの形式で指定する。' 1>&2
    echo 'Note: このコマンドは毎日実行する必要があります。' 1>&2
    exit 1
fi
start_date=$1
end_date=$2
if [ ${#start_date} != 8 ]; then
    echo "ERR: 時刻表開始日の指定に誤りがあります。${start_date}" 1>&2
    exit 2
fi
dummy=`expr ${start_date} '+' 0`
if [ $? != 0 ]; then
    echo "ERR: 時刻表開始日の指定に誤りがあります。${start_date}" 1>&2
    exit 2
fi
if [ ${#end_date} != 8 ]; then
    echo "ERR: 時刻表終了日の指定に誤りがあります。${end_date}" 1>&2
    exit 3
fi
dummy=`expr ${end_date} '+' 0`
if [ $? != 0 ]; then
    echo "ERR: 時刻表終了日の指定に誤りがあります。${end_date}" 1>&2
    exit 3
fi
if [ ${start_date} -gt ${end_date} ]; then
    echo "ERR: 時刻表終了日は時刻表開始日以降の日付を指定してください。${start_date} <= ${end_date}?" 1>&2
    exit 4
fi

# 実行
python3 -u src/get_timetable.py ${start_date} ${end_date}
rc=$?
if [ $rc == 0 ]; then
    cp -p output/`ls -t output/ | head -n 1` ../../cache/timetables.json
    cp_rc=$?
    if [ $cp_rc == 0 ]; then
        echo "INFO: 時刻表を置き換えました。`ls -l ../../cache/timetables.json | sed -e 's#../../##'`" 1>&2
    fi
fi

# 復帰
exit $rc
