import os
from numpy import random
from tensorflow.python.ops.gen_math_ops import sqrt
from riotwatcher import LolWatcher, ApiError

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tensorflow import keras
y = [23.45/60,12.5/60]
print(y)
model = tf.keras.models.load_model('models/model1')

x = model.predict([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6]])

def test():
    return printFunction

def printFunction():
    print("hello")
    print("this is a function called inside a function")


def calculatePi(n):
    pointCirc = 0
    for i in range(n):
        x = random.uniform(0,1)
        y = random.uniform(0,1)
        dist = sqrt(x*x + y*y)
        if dist <= 1:
            pointCirc += 1   
        
    return 4*pointCirc/n

y = test()

