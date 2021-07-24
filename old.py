from riotwatcher import LolWatcher, ApiError

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd



#uses tensorflow 1.0 style coding not good 
lol_watcher = LolWatcher('')
my_region = 'na1'

#declare versions
versions = lol_watcher.data_dragon.versions_for_region(my_region)
champions_version = versions['n']['champion']
summoner_spells_version=versions['n']['summoner']
items_version=versions['n']['item']
champions = lol_watcher.data_dragon.champions(champions_version)['data']


def getGamePlayers(summonerName, gameNum):
    me = lol_watcher.summoner.by_name(my_region, summonerName)
    matchId = lol_watcher.match.matchlist_by_account(my_region, me['accountId'])['matches'][gameNum]['gameId']
    matchDetail = lol_watcher.match.by_id(my_region, matchId)
    '''
    for players in matchDetail['participantIdentities']:
        print(players['player']['summonerName'])
    '''
    print("Match Result: " + matchDetail['teams'][0]['win'])

def doSmartTensorflowThings(learningPlayer, testPlayer):
    learnData = pd.read_excel('dataFolder/learnData.xlsx')
    testData = pd.read_excel('dataFolder/testData.xlsx')
    learnResult = learnData.pop('win')
    testResult = testData.pop('win')
    print(learnData)

    gameDataPandas = pd.DataFrame(data=learnData)
    testDataPandas = pd.DataFrame(data=testData)

    NUMERIC_COLUMNS = ['firstBlood', 'firstTower', 'firstInhibitor', 'firstBaron', 'firstDragon', 'firstHerald', 'blueTowerKills', 'blueInhibKills', 'blueBaronKills', 'blueDrakeKills',
    'redTowerKills', 'redInhibKills', 'redBaronKills', 'redDrakeKills', 'blueTotalGold', 'redTotalGold']

    feature_columns = []
    for feature_name in NUMERIC_COLUMNS:
        feature_columns.append(tf.feature_column.numeric_column(feature_name, dtype=tf.float32))

    def make_input_fn(data_df, label_df, num_epochs=10, shuffle=True, batch_size=32):
        def input_function():
            ds = tf.data.Dataset.from_tensor_slices((dict(data_df), label_df))
            if shuffle:
                ds = ds.shuffle(1000)
            ds = ds.batch(batch_size).repeat(num_epochs)
            return ds
        return input_function
    
    train_input_fn = make_input_fn(gameDataPandas, learnResult)
    eval_input_fn = make_input_fn(testDataPandas, testResult, num_epochs=1, shuffle=False)

    linear_est = tf.estimator.LinearClassifier(feature_columns=feature_columns)
    linear_est.train(train_input_fn)  # train
    result = linear_est.evaluate(eval_input_fn)

    print(result)
    result = list(linear_est.predict(eval_input_fn))
    for game in range(10):
        print(result[game]['probabilities'])
        getGamePlayers(testPlayer, game)


doSmartTensorflowThings('TL Armao', 'biofrost')