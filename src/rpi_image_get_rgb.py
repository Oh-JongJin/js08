import glob
import os
import pandas as pd
from PIL import Image
import cv2
import time
import datetime

rpi_x = []
rpi_y = []
distance = []
path = "images/2020070810/"

def read_pixel(camnumber : str):
    global rpi_x
    global rpi_y
    global distance
    df = pd.read_csv(f"{path}{camnumber}.csv")
    rpi_x = df["x"]
    rpi_y = df["y"]
    distance = df["distance"]
    print("target settings.")

def get_rgb(foldername: str, camnumber: str):
    read_pixel(camnumber)
    col = ["x", "y", "r", "g", "b", "distance"]
    resultdf = pd.DataFrame(rpi_x,index=None,columns=col)
    resultdf["y"] = rpi_y
    r_list= []
    g_list= []
    b_list= []
    try:
        image = Image.open(glob.glob(f"{path}*_{camnumber}.png")[0])
        image_RGB = image.convert("RGB")
        for i in range(0, len(rpi_x)):  
            image_RGB_value = image_RGB.getpixel((int(rpi_x[i]), int(rpi_y[i])))
            r_list.append(image_RGB_value[0])
            g_list.append(image_RGB_value[1])
            b_list.append(image_RGB_value[2])
        resultdf["r"] = r_list
        resultdf["g"] = g_list
        resultdf["b"] = b_list
        resultdf["distance"] = distance
        resultdf.to_csv(f"{path}{camnumber}.csv", mode="w", index=False)
        print("rgb save.")
    except Exception as e:
        print("error: ", e)

def main():
    get_rgb()

if __name__ == "__main__": 
    main()
    