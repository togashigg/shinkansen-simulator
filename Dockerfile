# Dockerfile for 東海道新幹線なんちゃって運行シミュレーター
# Copyright (C) N.Togashi 2021
# build command: docker build -t shinkansen-simulator:latest -t shinkansen-simulator:0.1.2 .
# run command: docker run -d --name shinkansen-simulator -p 80:8080 \
#                     -v ~/timetable/cache:/app/shinkansen_simulator/timetable/cache \
#                     -v ~/timetable/log_docker:/app/shinkansen_simulator/timetable/log \
#                     -v ~/timetable/output:/app/shinkansen_simulator/timetable/output \
#                     -v ~/timetable/remarks:/app/shinkansen_simulator/timetable/remarks \
#                     shinkansen-simulator
# get timetable: docker exec shinkansen-simulator /bin/bash -c 'cd /app/shinkansen_simulator/timetable/; ./get.sh 20211001 20211031'
# base image
FROM ubuntu:18.04
MAINTAINER togashigg <KGG03575@nifty.com>
RUN apt update && apt -y upgrade
# タイムゾーン設定
RUN apt install -y tzdata
ENV TZ Asia/Tokyo
# 時刻同期
# RUN apt install -y ntp \
#     && cp -p /etc/ntp.conf /etc/ntp.conf.back \
#     && sed -i -e 's/^pool /# pool /g' /etc/ntp.conf \
#     && echo 'server ntp.nict.jp' >> /etc/ntp.conf \
#     && systemctl restart ntp
# 日本語化
RUN apt install -y language-pack-ja-base language-pack-ja locales \
    && locale-gen ja_JP.UTF-8 \
    && echo 'LANG=ja_JP.UTF-8' > /etc/default/locale
ENV LANG ja_JP.UTF-8
# スクレイピングに必要なパッケージをインストール(for requests_html library)
RUN apt install -yq gconf-service libasound2 libatk1.0-0 libc6 libcairo2 \
    libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 \
    libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 \
    libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 \
    libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 \
    libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation \
    libappindicator1 libnss3 lsb-release xdg-utils wget
# Python3パッケージをインストール
RUN apt install -y python3 python3-pip
# アプリケーションをインストール
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
# 必須pythonライブラリをインストール
RUN pip3 install -r requirements.txt
ADD . /app/
# herokuと同様の構成変更
RUN mkdir /app/static \
    && cp -pr /app/shinkansen_simulator/static /app/
# Djangoを常駐化
ENTRYPOINT /usr/bin/python3 manage.py runserver 0.0.0.0:8080
EXPOSE 8080
