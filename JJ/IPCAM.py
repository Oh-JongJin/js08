import cv2
import time
import datetime
from matplotlib import pyplot as plt
import numpy as np

cap = cv2.VideoCapture('rtsp://admin:1234@192.168.100.253:554/1/1')
# count = 0

while True:
    ret, frame = cap.read()
    video = cv2.resize(frame, dsize=(640, 480), interpolation=cv2.INTER_AREA)
    #cv2.imshow("IP Camera stream", frame)
    cv2.imshow("IP Camera stream", video)

    secs = time.time()

    #전체 프레임 중 1/100의 프레임만 저장한다.
    if datetime.datetime.now().minute % 5 == 0 and datetime.datetime.now().second == 00:
        # TIME

        epoch = int(secs)

        print('Saved frame number : ' + str(int(cap.get(1))))
        cv2.imwrite("images/frame.png", frame)
        gray_img = cv2.imread('images/frame.png', cv2.IMREAD_GRAYSCALE)
        cv2.imwrite("images/%d.png" % epoch, gray_img)
        print('Saved new frame.png')

        print(int(secs))

        tm = time.gmtime(secs)
        print("year:", tm.tm_year)
        print("month:", tm.tm_mon)
        print("day:", tm.tm_mday)
        print("hour:", tm.tm_hour+9)
        print("minute:", tm.tm_min)
        print("second:", tm.tm_sec)
        # count += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
