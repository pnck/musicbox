#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: pnck
# @Date:   2017-08-26 20:34:55

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()


from NEMbox.api import NetEaseAPI
from NEMbox.player import Player
from NEMbox import logger
from NEMbox.utils import notify

log = logger.getLogger(__name__)
api = NetEaseAPI()
player = Player()

def find_songs(s):
    try:
        data = api.search(s, stype=1)
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
            return api.dig_info(songs, 'songs')
    except Exception as e:
        log.error(e)
        return []

def make_notify(summary,song, album, artist):
    body = '%s\n专辑 %s 歌手 %s' % (song, album, artist)
    content = summary + ': ' + body
    notify(content)

def callback():
    player.playing_flag = False
    
if __name__ == '__main__':
    player.end_callback = callback
    datalist = {}
    player.new_player_list('songs','点歌列表',datalist, -1)
    player.append_songs([find_songs('pink-series 1')[0]])
    #player.append_songs([find_songs('irenes theme-series 2')[0]])
    player.append_songs([find_songs('kong')[0]])
    player.play_and_pause(0)
    __import__('time').sleep(5)
    player.next()
    __import__('time').sleep(5)
    print (player.songs[str(player.playing_id)]['lyric'])
    #player.popen_recall(callback,song).join()

