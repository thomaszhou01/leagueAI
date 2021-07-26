import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tensorflow import keras

model = tf.keras.models.load_model('models/model1')

x = model.predict([[2,1,1,2,1,4,2,0,0,2,3,1,1,2,2000,5]])
print(x)
print(x[0][0])