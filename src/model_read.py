
import os
import time
import tensorflow.keras as keras

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def read_model():
    print("모델을 불러옵니다.")
    timer = time.time()
    print()    
    model = keras.models.load_model("andrew-1583797361/andrew-1583797361", compile=False)
    print(time.time() - timer)
    return model


    
