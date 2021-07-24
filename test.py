from numpy.core.numeric import True_
from riotwatcher import LolWatcher, ApiError

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import requests
import ssl

from tensorflow.python.ops.numpy_ops.np_math_ops import true_divide

#uses tensorflow 1.0 style coding not good 
lol_watcher = LolWatcher('RGAPI-1c342b1d-1c64-4075-b237-1f5c54023e4e')
my_region = 'na1'

#declare versions
versions = lol_watcher.data_dragon.versions_for_region(my_region)
champions_version = versions['n']['champion']
summoner_spells_version=versions['n']['summoner']
items_version=versions['n']['item']
champions = lol_watcher.data_dragon.champions(champions_version)['data']
me = lol_watcher.summoner.by_name(my_region, 'tomtom2352')
blueTeam = []
redTeam = []

matchId = lol_watcher.match.matchlist_by_account(my_region, me['accountId'])['matches'][0]['gameId']
matchDetail = lol_watcher.match.by_id(my_region, matchId)
print(matchDetail)

def analyzeGame():
    listSize = 0
    blueKills = 0
    redKills = 0
    while True:
        response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False).json()
        print(blueKills)
        print(redKills)
        if len(response['events']['Events']) > listSize:
            for event in response['events']['Events'][listSize:]:
                if event['EventName'] == "ChampionKill":
                    if event['KillerName'] in blueTeam:
                        blueKills += 1
                    elif event['KillerName'] in redTeam:
                        redKills += 1
            listSize = len(response['events']['Events'])


while True:
    try:
        response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False).json()
        for player in response['allPlayers']:
            if player['team'] == 'ORDER':
                blueTeam.append(player['summonerName'])
            else:
                redTeam.append(player['summonerName'])
        break
    except:
        print('error connecting')

print(blueTeam)
print(redTeam)
analyzeGame()