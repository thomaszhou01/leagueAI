from riotwatcher import LolWatcher, ApiError
from random import randint, seed
import numpy as np
import matplotlib as plt
import pandas as pd
import certifi


seed(1)

lol_watcher = LolWatcher('RGAPI-840107f5-71d7-4970-9a08-9e88614bf00f')
my_region = 'na1'
puuid_region = "AMERICAS"

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
        my_matches = lol_watcher.match.matchlist_by_puuid(puuid_region, me['puuid'])
        for i in my_matches:
            ids.append(i)
        return ids + generateMatchIds(lol_watcher.match.by_id(puuid_region, ids[randint(0,9)])["info"]['participants'][0]['summonerName'], num-1)

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
        matchDetail = lol_watcher.match.by_id(puuid_region, gameID)
        gameOutcome.append(1 if matchDetail["info"]['teams'][0]['win'] else 0)
        firstBlood.append(1 if matchDetail["info"]['teams'][0]['objectives']['champion']['first'] else 2)
        firstTower.append(1 if matchDetail["info"]['teams'][0]['objectives']['tower']['first'] else 2)
        firstInhib.append(1 if matchDetail["info"]['teams'][0]['objectives']['inhibitor']['first'] else 2)
        firstBaron.append(1 if matchDetail["info"]['teams'][0]['objectives']['baron']['first'] else 2)
        firstDrake.append(1 if matchDetail["info"]['teams'][0]['objectives']['dragon']['first'] else 2)
        firstRift.append(1 if matchDetail["info"]['teams'][0]['objectives']['riftHerald']['first'] else 2)
        blueTowersKills.append(matchDetail["info"]['teams'][0]['objectives']['tower']['kills'])
        blueInhibsKills.append(matchDetail["info"]['teams'][0]['objectives']['inhibitor']['kills'])
        blueBaronKills.append(matchDetail["info"]['teams'][0]['objectives']['baron']['kills'])
        blueDrakeKills.append(matchDetail["info"]['teams'][0]['objectives']['dragon']['kills'])
        redTowersKills.append(matchDetail["info"]['teams'][1]['objectives']['tower']['kills'])
        redInhibsKills.append(matchDetail["info"]['teams'][1]['objectives']['inhibitor']['kills'])
        redBaronKills.append(matchDetail["info"]['teams'][1]['objectives']['baron']['kills'])
        redDrakeKills.append(matchDetail["info"]['teams'][1]['objectives']['dragon']['kills'])
        blueGold = 0
        redGold = 0
        blueKills = 0
        redKills = 0
        for player in matchDetail["info"]['participants']:
            if player['teamId'] == 100:
                blueGold += player['goldEarned']
                blueKills += player['kills']
            else:
                redGold += player['goldEarned']
                redKills += player['kills']

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


learnData = generateGames('Sn1per1', 50)
gameDataPandas = pd.DataFrame(data=learnData)
gameDataPandas.set_index('win', inplace=True)

with pd.ExcelWriter('dataFolder/learnData.xlsx', mode='a') as writer:  
    gameDataPandas.to_excel(writer, sheet_name='Sheet')

