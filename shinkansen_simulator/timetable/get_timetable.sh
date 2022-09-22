#!/bin/bash
# get_timetable.sh:  時刻表自動取得用シェルスクリプト
# Copyright (C) N.Togashi 2021-2022
# 事前に「~/.netrc」に以下を設定済であること。
#   machine github.com
#     login ＜githubユーザID＞
#     password ＜githubユーザIDのAPI Key＞

# 定数
USER_HOME=${HOME}/
TIMETABLE_DIR=${USER_HOME}timetable/
TIMETABLE_OUTPUT=${TIMETABLE_DIR}output/
GITHUB_CACHE=${USER_HOME}github/shinkansen-simulator/cache/
TIMETABLES_JSON=timetables.json
BACKUP_DIR=${USER_HOME}backup/
BACKUP_FILE=${BACKUP_DIR}timetable_data_`date "+%Y%m%d"`.tgz

# 時刻表を取得する
function exec_func() {
    # 開始時刻を出力
    date
    # Dockerコンテナを起動する
    docker start shinkansen-simulator
    rc=$?
    sleep 5
    if [ $rc -ne 0 ]; then
        echo "`date '+%Y/%m/%d %H:%M:%S'` ERROR in docker start, rc=$rc"
        return $rc
    fi
    # シェルを実行する
    docker exec shinkansen-simulator /app/shinkansen_simulator/timetable/get.sh
    rc=$?
    sleep 5
    if [ $rc -ne 0 ]; then
        echo "`date '+%Y/%m/%d %H:%M:%S'` ERROR in docker exec get.sh, rc=$rc"
        return $rc
    fi
    # Dockerコンテナを停止する
    docker stop shinkansen-simulator
    rc=$?
    sleep 5
    if [ $rc -ne 0 ]; then
        echo "`date '+%Y/%m/%d %H:%M:%S'` ERROR in docker stop, rc=$rc"
        return $rc
    fi
    # 作業ディレクトリをバックアップする
    (cd $USER_HOME; tar zcvf $BACKUP_FILE ./timetable/) > /dev/null
    rc=$?
    if [ $rc -ne 0 ]; then
        echo "`date '+%Y/%m/%d %H:%M:%S'` ERROR in docker stop, rc=$rc"
        return $rc
    fi
    # 終了時刻を出力
    date

    return $rc
}

# 時刻表に差分があれば更新する
function diff_func() {
    # 開始時刻を出力
    date
    # 時刻表が存在するディレクトリまで移動
    cd $TIMETABLE_OUTPUT
    # 差分を確認する
    timetable_new=`ls -tr *.json | tail -1`
    diff ${GITHUB_CACHE}$TIMETABLES_JSON $timetable_new
    diff_rc=$?
    if [ $diff_rc -ne 0 ]; then
        diff_wcl=`diff ${GITHUB_CACHE}$TIMETABLES_JSON $timetable_new | wc -l`
        if [ $diff_wcl -ne 8 ]; then
            # GitHubを更新する
            cd $GITHUB_CACHE
            git pull
            cp -p ${TIMETABLE_OUTPUT}$timetable_new ./$TIMETABLES_JSON
            git add $TIMETABLES_JSON
            git commit -m "update $TIMETABLES_JSON by get_timetable.sh"
            git push
        fi
    fi
    sleep 5
    # 終了時刻を出力
    date

    return $rc
}

# 実行
rc=0
echo "`date '+%Y/%m/%d %H:%M:%S'` get_timetable.sh start."
exec_func
diff_func
echo "`date '+%Y/%m/%d %H:%M:%S'` get_timetable.sh ended, rc=$rc"
exit $rc
