# !/usr/bin/env python3
import numpy as np
import cv2
import time
# import pyautogui


def main(current_time: str):
    # The duration in seconds of the video captured
    ADD = 'rtsp://admin:sijung5520@192.168.100.133/profile2/media.smp'

    cap = cv2.VideoCapture(ADD)

    ret, frame = cap.read()
    if ret:
        cv2.imwrite(f"AI_Camera/{current_time}.png", frame)
        # img = pyautogui.screenshot()
        # img.save(f"temperature/{current_time}.png")


if __name__ == "__main__":
    print("Start capture program..")
    while True:
        epoch = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        #if epoch[-2:] == "10":
        time.sleep(10)
        main(epoch)
