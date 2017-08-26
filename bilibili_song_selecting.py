#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: pnck
# @Date:   2017-08-26 20:34:55

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import sys
from urllib.request import *
import json
import time
import re

from NEMbox.api import NetEaseAPI
from NEMbox.player import Player
from NEMbox import logger
from NEMbox import utils

log = logger.getLogger(__name__)
api = NetEaseAPI()
player = Player()

default_song_id = 753521
default_room_id = 946041

g_playing = False

def find_song(s):
    try:
        data = api.search(s, stype=1)
        if type(s) is type(1):
            songs = api.songs_detail([s])
            return [api.dig_info(songs, 'songs')[0]]
        song_ids = []
        if 'songs' in data['result']:
            if 'mp3Url' in data['result']['songs']:
                songs = data['result']['songs']
            # if search song result do not has mp3Url
            # send ids to get mp3Url
            else:
                for i in range(0, len(data['result']['songs'])):
                    song_ids.append(data['result']['songs'][i]['id'])
                songs = api.songs_detail(song_ids)
            return [api.dig_info(songs, 'songs')[0]]
    except Exception as e:
        log.error(e)
        return []


def make_notify(summary, song, album, artist):
    content = ''
    if(summary != 'stop'):
        body = '%s\n专辑 %s 歌手 %s' % (song, album, artist)
        content = summary + ': ' + body
    else:
        content = '停止播放'
    utils.notify(content)


def quit():
    print('quit...')
    global player
    player.playing_flag = False
    global g_playing
    g_playing  = False



if __name__ == '__main__':
    player.end_callback = quit
    datalist = {}
    player.new_player_list('songs', '点歌列表', datalist, -1)
    #__import__('time').sleep(5)
    # player.next()
    #__import__('time').sleep(5)
    #print (player.songs[str(player.playing_id)]['lyric'])
    # player.popen_recall(callback,song).join()
    room_id = ''
    try:
        room_id = str(int(sys.argv[1]))
    except:
        room_id = str(default_room_id)

    data = json.loads(urlopen(Request('https://api.live.bilibili.com/ajax/msg',
                                      b'roomid=' + room_id.encode('utf8'))).read().decode('utf-8'))['data']['room']
    latest_time = 0
    if data:
        msgs = {}
        [msgs.update({time.mktime(time.strptime(msg['timeline'],
                                                '%Y-%m-%d %H:%M:%S')):msg['text']}) for msg in data]
        msglist = [(time, text) for time, text in map(
            lambda k:(k, msgs.get(k)), sorted(msgs.keys()))]
        latest_time = msglist[-1][0]

    player.end_callback = quit
    player.append_songs(find_song(default_song_id))
    player.play_and_pause(0)
    first_play = True
    g_playing = True

    while(g_playing):
        data = json.loads(urlopen(Request('https://api.live.bilibili.com/ajax/msg',
                                          b'roomid=' + room_id.encode('utf8'))).read().decode('utf-8'))['data']['room']
        if data:
            msgs = {}
            [msgs.update({time.mktime(time.strptime(msg['timeline'],
                                                    '%Y-%m-%d %H:%M:%S')):(msg['nickname'],msg['text'])}) for msg in data]
            msglist = [(time, content) for time, content in map(
                lambda k:(k, msgs.get(k)), sorted(msgs.keys()))]
            # find new added msgs
            for i in range(len(msglist)):
                msg = msglist[i]
                if msg[0] <= latest_time:
                    continue
                m = re.match('^点歌 .*', msg[1][1])  # msg[content]['text']
                if m:
                    s = m.group()[3:].strip()
                    latest_time = msg[0] # time
                    print('%s 点歌: %s' % (msg[1][0],s))
                    new_song = find_song(s[:60])
                    player.append_songs(new_song)
                    log.info('append new song %s to list' % (new_song,))
                    if first_play:
                        player.next()
                        time.sleep(0.5)
                    first_play = False
                    continue
                m = re.match('^切歌',msg[1][1])# msg[content]['text']
                if m:
                    latest_time = msg[0]
                    player.next()
                    time.sleep(0.5)

        time.sleep(0.8)
