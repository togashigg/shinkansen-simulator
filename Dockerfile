# Dockerfile for 東海道新幹線なんちゃって運行シミュレーター
# Copyright (C) N.Togashi 2021-2022
# build: docker build -t shinkansen-simulator:latest .
# run: docker run -d --name shinkansen-simulator -p 80:8080 \
#             --mount type=bind,src=${HOME}/timetable/cache,dst=/app/shinkansen_simulator/timetable/cache \
#             --mount type=bind,src=${HOME}/timetable/log,dst=/app/shinkansen_simulator/timetable/log \
#             --mount type=bind,src=${HOME}/timetable/output,dst=/app/shinkansen_simulator/timetable/output \
#             --mount type=bind,src=${HOME}/timetable/remarks,dst=/app/shinkansen_simulator/timetable/remarks \
#             shinkansen-simulator
# timetable: docker exec shinkansen-simulator /app/shinkansen_simulator/timetable/get.sh
# base image
FROM   ubuntu:22.04
MAINTAINER togashigg <KGG03575@nifty.com>
RUN    apt update && apt -y upgrade \
    && apt clean
# タイムゾーン設定
RUN    apt update \
    && apt install -y tzdata \
    && apt clean
ENV    TZ Asia/Tokyo
# 時刻同期
# RUN    apt update \
#     && apt install -y ntp \
#     && cp -p /etc/ntp.conf /etc/ntp.conf.back \
#     && sed -i -e 's/^pool /# pool /g' /etc/ntp.conf \
#     && echo 'server ntp.nict.jp' >> /etc/ntp.conf \
#     && systemctl restart ntp \
#     && apt clean
# 日本語化
RUN    apt update \
    && apt install -y language-pack-ja-base language-pack-ja locales \
    && locale-gen ja_JP.UTF-8 \
    && echo 'LANG=ja_JP.UTF-8' > /etc/default/locale \
    && apt clean
ENV    LANG ja_JP.UTF-8
# スクレイピングに必要なパッケージをインストール(for requests_html library)
# RUN    apt update \
#     && apt install -yq gconf-service libasound2 libatk1.0-0 libc6 libcairo2 \
#            libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 \
#            libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 \
#            libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 \
#            libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 \
#            libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation \
#            libappindicator1 libnss3 lsb-release xdg-utils wget \
#     && apt clean
# Python3パッケージをインストール
RUN    apt update \
    && apt install -y python3 python3-pip \
    && apt clean
# Python3必須ライブラリをインストール
RUN    mkdir /app
WORKDIR /app
ADD    requirements.txt /app/
RUN    pip3 install -r requirements.txt
# RUN    pyppeteer-install
# アプリケーションをインストール
ADD    . /app/
# Herokuと同様の構成変更
RUN    mkdir /app/static \
    && cp -pr /app/shinkansen_simulator/static /app/
# Djangoを常駐化
ENTRYPOINT python3 manage.py runserver 0.0.0.0:8080
EXPOSE 8080
