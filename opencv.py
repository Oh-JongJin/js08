import cv2
import time
import datetime
from matplotlib import pyplot as plt
import numpy as np

cap = cv2.VideoCapture('rtsp://admin:1234@192.168.100.253:554/1/1')
# count = 0

while True:
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # threshold : 임의의 경계값을 넘기면 모두 white로 바꾼다. 
    # adaptiveThreshold : threshold은 이미지 음영이 다르면 일부 영역이 모두 변하는 문제가 있다. threshold 보다 작은 영역별로 thresholding해 이미지를 더 선명하게 구분할 수 있다. 
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,15,2)
    # dilate : 이미지를 팽창시키는 함수, 검은색 부분이 넓게 커질것이다. (iterations : 반복횟수)
    dilated = cv2.dilate(thresh, None, iterations=3)
    # findContours : 이미지의 폐곡선을 만들어주는 함수 (입력 이미지는 흑백사진이어야 된다.)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        #contour 영역이 600 이상인곳에 사각형 그리기
        if cv2.contourArea(contour) < 60:
            continue
        # 사각형 및 텍스트 표시하기
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        cv2.putText(frame, 'object', (x+3, y-10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))  
    # cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
    video = cv2.resize(frame, dsize=(1620, 980), interpolation=cv2.INTER_AREA)

    #cv2.imshow("IP Camera stream", frame)
    cv2.imshow("IP Camera stream", video)

    secs = time.time()

    #5분이 지나면 캡쳐.
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
