from riotwatcher import LolWatcher, ApiError

import numpy as np
import matplotlib as plt
import pandas as pd

lol_watcher = LolWatcher('RGAPI-9b445774-93e0-47ac-b668-c275e9545474')
my_region = 'euw1'

#declare versions
versions = lol_watcher.data_dragon.versions_for_region(my_region)
champions_version = versions['n']['champion']
summoner_spells_version=versions['n']['summoner']
items_version=versions['n']['item']
champions = lol_watcher.data_dragon.champions(champions_version)['data']


def generateMatchIds(name, num):
    if num == 0:
        return []
    else:
        print(num)
        ids = []
        me = lol_watcher.summoner.by_name(my_region, name)
        my_matches = lol_watcher.match.matchlist_by_account(my_region, me['accountId'])['matches']
        for i in my_matches:
            ids.append(i['gameId'])
        return ids + generateMatchIds(lol_watcher.match.by_id(my_region, ids[0])['participantIdentities'][0]['player']['summonerName'], num-1)

#gather data
def generateGames(summonerName, gamesX100):
    
    gameOutcome = []
    firstBlood = []
    firstTower = []
    firstInhib = []
    firstBaron = []
    firstDrake = []
    firstRift = []
    blueTowersKills = []
    blueInhibsKills = []
    blueBaronKills = []
    blueDrakeKills = []
    redTowersKills = []
    redInhibsKills = []
    redBaronKills = []
    redDrakeKills = []
    goldDifference = []
    killDifference = []

    matchIDs = generateMatchIds(summonerName, gamesX100)
    print(len(matchIDs))
    
    for gameID in matchIDs:
        matchDetail = lol_watcher.match.by_id(my_region, gameID)
        gameOutcome.append(1 if matchDetail['teams'][0]['win'] == "Win" else 0)
        firstBlood.append(1 if matchDetail['teams'][0]['firstBlood'] else 2)
        firstTower.append(1 if matchDetail['teams'][0]['firstTower'] else 2)
        firstInhib.append(1 if matchDetail['teams'][0]['firstInhibitor'] else 2)
        firstBaron.append(1 if matchDetail['teams'][0]['firstBaron'] else 2)
        firstDrake.append(1 if matchDetail['teams'][0]['firstDragon'] else 2)
        firstRift.append(1 if matchDetail['teams'][0]['firstRiftHerald'] else 2)
        blueTowersKills.append(matchDetail['teams'][0]['towerKills'])
        blueInhibsKills.append(matchDetail['teams'][0]['inhibitorKills'])
        blueBaronKills.append(matchDetail['teams'][0]['baronKills'])
        blueDrakeKills.append(matchDetail['teams'][0]['dragonKills'])
        redTowersKills.append(matchDetail['teams'][1]['towerKills'])
        redInhibsKills.append(matchDetail['teams'][1]['inhibitorKills'])
        redBaronKills.append(matchDetail['teams'][1]['baronKills'])
        redDrakeKills.append(matchDetail['teams'][1]['dragonKills'])
        blueGold = 0
        redGold = 0
        blueKills = 0
        redKills = 0
        for player in matchDetail['participants']:
            if player['teamId'] == 100:
                blueGold += player['stats']['goldSpent']
                blueKills += player['stats']['kills']
            else:
                redGold += player['stats']['goldSpent']
                redKills += player['stats']['kills']

        goldDifference.append(blueGold-redGold)
        killDifference.append(blueKills-redKills)



    gameData = {
        'win': gameOutcome,
        'firstBlood': firstBlood,
        'firstTower': firstTower,
        'firstInhibitor': firstInhib,
        'firstBaron': firstBaron,
        'firstDragon': firstDrake,
        'firstHerald': firstRift,
        'blueTowerKills': blueTowersKills,
        'blueInhibKills': blueInhibsKills,
        'blueBaronKills': blueBaronKills,
        'blueDrakeKills': blueDrakeKills,
        'redTowerKills': redTowersKills,
        'redInhibKills': redInhibsKills,
        'redBaronKills': redBaronKills,
        'redDrakeKills': redDrakeKills,
        'goldDiff' : goldDifference,
        'killDif': killDifference,
    }
    return gameData

learnData = generateGames('MSF Sertuss', 10)
gameDataPandas = pd.DataFrame(data=learnData)
gameDataPandas.set_index('win', inplace=True)

with pd.ExcelWriter('dataFolder/learnData.xlsx', mode='a') as writer:  
    gameDataPandas.to_excel(writer, sheet_name='Sheet2')
