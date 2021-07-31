from riotwatcher import LolWatcher, ApiError

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tensorflow import keras


lol_watcher = LolWatcher('')
my_region = 'na1'

#declare versions
versions = lol_watcher.data_dragon.versions_for_region(my_region)
champions_version = versions['n']['champion']
summoner_spells_version=versions['n']['summoner']
items_version=versions['n']['item']
champions = lol_watcher.data_dragon.champions(champions_version)['data']

learnData = pd.concat(pd.read_excel('dataFolder/learnData.xlsx', sheet_name=None), ignore_index=True)
testData = pd.read_excel('dataFolder/testData.xlsx')
learnResult = learnData.pop('win')
testResult = testData.pop('win')


sns.pairplot(learnData[['goldDiff', 'killDif', 'blueTowerKills', 'redTowerKills']], diag_kind='kde')

model = tf.keras.Sequential([
    keras.layers.Dense(16),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(2, activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(learnData, learnResult, epochs=20)
test = model.evaluate(testData,  testResult, verbose=1) 
model.save('models/model1')

print(model.summary())
print('Test accuracy:', test)
x = model.predict(testData)
print(x[0:10])