import glob
import os
import cv2
print(os.getcwd())
path = "images/2020070810/"
num = "v2"

img = cv2.imread(glob.glob(f"{path}*_{num}.png")[0], cv2.IMREAD_COLOR) 
print(type(img))