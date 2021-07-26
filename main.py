from riotwatcher import LolWatcher, ApiError

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
from tensorflow import keras
import requests
import warnings
warnings.filterwarnings("ignore")
lol_watcher = LolWatcher('')
my_region = 'na1'

versions = lol_watcher.data_dragon.versions_for_region(my_region)
champions_version = versions['n']['champion']
summoner_spells_version=versions['n']['summoner']
items_version=versions['n']['item']
champions = lol_watcher.data_dragon.champions(champions_version)['data']
items = lol_watcher.data_dragon.items(items_version)['data']

blueTeam = []
redTeam = []

model = tf.keras.models.load_model('models/model1')

def getTotalItemValue(player):
    totalGold = 0
    for i in player:
        itemID = str(i['itemID'])
        totalGold += items[itemID]['gold']['total']
    return totalGold

def analyzeGame():
    listSize = 0
    data = [0]*16
    firstInhib = False
    firstBaron = False
    firstDragon = False
    firstHerald = False
    blueKills = 0
    redKills = 0
    
    
    while True:
        try:
            time.sleep(3)
            response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False).json()
            if len(response['events']['Events']) > listSize:
                blueSpentGold = 0
                redSpentGold = 0
                #calculate item value
                for player in response['allPlayers']:
                    if player['summonerName'] in blueTeam:
                        blueSpentGold += getTotalItemValue(player['items'])
                    elif player['summonerName'] in redTeam:
                        redSpentGold += getTotalItemValue(player['items'])
                data[14] = blueSpentGold-redSpentGold
                #calculate events
                for event in response['events']['Events'][listSize:]:
                    if event['EventName'] == "FirstBlood":
                        if event['Recipient'] in blueTeam:
                            data[0] = 1
                        elif event['Recipient'] in redTeam:
                            data[0] = 2
                    elif event['EventName'] == "FirstBrick":
                        if event['KillerName'] in blueTeam:
                            data[1] = 1
                        elif event['KillerName'] in redTeam:
                            data[1] = 2
                    elif event['EventName'] == "TurretKilled":
                        if event['KillerName'] in blueTeam:
                            data[6] += 1
                        elif event['KillerName'] in redTeam:
                            data[10] += 1
                    elif event['EventName'] == "InhibKilled":
                        if event['KillerName'] in blueTeam:
                            if not firstInhib:
                                data[2] = 1
                            data[7] += 1
                        elif event['KillerName'] in redTeam:
                            if not firstInhib:
                                data[2] = 2
                            data[11] += 1
                    elif event['EventName'] == "BaronKill":
                        if event['KillerName'] in blueTeam:
                            if not firstBaron:
                                data[3] = 1
                            data[8] += 1
                        elif event['KillerName'] in redTeam:
                            if not firstBaron:
                                data[3] = 2
                            data[12] += 1
                    elif event['EventName'] == "DragonKill":
                        if event['KillerName'] in blueTeam:
                            if not firstDragon:
                                data[4] = 1
                            data[9] += 1
                        elif event['KillerName'] in redTeam:
                            if not firstDragon:
                                data[4] = 2
                            data[13] += 1
                    elif event['EventName'] == "HeraldKill":
                        if event['KillerName'] in blueTeam:
                            if not firstHerald:
                                data[5] = 1
                        elif event['KillerName'] in redTeam:
                            if not firstHerald:
                                data[5] = 2
                    elif event['EventName'] == "ChampionKill":
                        if event['KillerName'] in blueTeam:
                            blueKills += 1
                        elif event['KillerName'] in redTeam:
                            redKills += 1
                        data[15] = blueKills-redKills
                listSize = len(response['events']['Events'])
                x = model.predict([data])
                print(data)
                print(x)
                if x[0][0] > x[0][1]:
                    print("Red Advantage")
                else:
                    print("Blue Advantage")
        except:
            print("program finished")
            break
            
            



#attempt to connect to live game
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
        print('waiting for game to start...')

print(blueTeam)
print(redTeam)
analyzeGame()