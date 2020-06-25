import os
import numpy as np
import pandas as pd
from PIL import Image
import cv2
import time
import datetime

rpi_x = []
rpi_y = []
distance = []


def read_pixel():
    global rpi_x
    global rpi_y
    global distance
    df = pd.read_csv("data/target_pixel.csv")
    rpi_x = df['x']
    rpi_y = df['y']
    distance = df['distance']
    print('target이 설정되었습니다.')

def get_rgb():
    read_pixel()
    col = ['x','y','r','g','b','distance']
    resultdf = pd.DataFrame(rpi_x,index=None,columns=col)
    resultdf['y'] = rpi_y
    r_list= []
    g_list= []
    b_list= []
    try:
        image = Image.open("images/20200611.png")
        image_RGB = image.convert("RGB")
        for i in range(0,len(rpi_x)):  
            image_RGB_value = image_RGB.getpixel((int(rpi_x[i]),int(rpi_y[i])))
            r_list.append(image_RGB_value[0])
            g_list.append(image_RGB_value[1])
            b_list.append(image_RGB_value[2])
        resultdf['r'] = r_list
        resultdf['g'] = g_list
        resultdf['b'] = b_list
        resultdf['distance'] = distance
        epoch = int(time.time())
        name = time.strftime("%Y%m%d%H%M",time.localtime(epoch))
        print(name)
        resultdf.to_csv("data/%s.csv" %name, mode='w',index=False)
        print('rgb값이 저장되었습니다.')
    except Exception as e:
        print('에러 내용 : ', e)

def main():
    get_rgb()
    # os.system('python hello.py')

if __name__ == '__main__': 
    main()
    