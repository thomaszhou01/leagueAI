from riotwatcher import LolWatcher, ApiError

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tensorflow import keras


lol_watcher = LolWatcher('')
my_region = 'na1'

#declare versions
versions = lol_watcher.data_dragon.versions_for_region(my_region)
champions_version = versions['n']['champion']
summoner_spells_version=versions['n']['summoner']
items_version=versions['n']['item']
champions = lol_watcher.data_dragon.champions(champions_version)['data']

learnData = pd.read_excel('dataFolder/learnData.xlsx')
testData = pd.read_excel('dataFolder/testData.xlsx')
learnResult = learnData.pop('win')
testResult = testData.pop('win')
learnData = learnData.to_numpy()
testData = testData.to_numpy()

model = tf.keras.Sequential([
    tf.keras.layers.Dense(18),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(2, activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(learnData, learnResult, epochs=100)
test = model.evaluate(testData,  testResult, verbose=1) 

print(model.summary())
print('Test accuracy:', test)
x = model.predict(testData)
print(x[0:10])