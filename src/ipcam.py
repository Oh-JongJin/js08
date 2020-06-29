"""
Capture image from the IP camera.

TODO(경원): fails to execute on MacOS
"""

import argparse
import time
import datetime
import cv2
import numpy as np


# 어두운 영역 주위에 사각형 그리기    
def find_black_pixel(frame: np.ndarray, th: int, y_value: int):
    """Draw a rectangle around the dark area.    
            
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, th, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        # contour 영역 중에 사각형을 씌울 조건걸기
        if cv2.contourArea(contour) > 600 or y >= y_value:
            continue
        # 사각형 및 텍스트 표시하기
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        pixel = f"({x}, {y})"
        cv2.putText(frame, pixel, (x + 3, y - 10), cv2.FONT_HERSHEY_COMPLEX, 
                    0.5, (0, 0, 255))


def main(args: argparse.Namespace) -> str: 
    """Print and save the image and returns the status of the program

       Args: 

       Returns:
         String: Pressing the keyboard 'q' returns the character 'end'
    """

    try:
        _, frame = cap.read()
        find_black_pixel(frame, args.t, args.y)
        video = cv2.resize(frame, dsize=(1920, 1024))        
        cv2.imshow("IP Camera stream", video)

        secs = time.time()
        now = datetime.datetime.now()
        # Capture the video you are streaming and save it as an image
        if now.minute % args.m == 0 and now.second == 0:
            epoch = int(secs)

            print(f"Saved frame number: {int(cap.get(1))}")
            cv2.imwrite(f"images/{epoch}.png", frame)

            tm = time.gmtime(secs)
            print("[{}년{}월{}일 {}시 {}분] Saved frame - {}".format(tm.tm_year, tm.tm_mon,
                                                                  tm.tm_mday, tm.tm_hour + 9, tm.tm_min, epoch))

            time.sleep(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            global state
            state = 'end'
            print('0')            
        
    except Exception as E:
        print(E)
   
    return state
    

if __name__ == "__main__":
    # ADD is the address of IP camera.
    ADD = 'rtsp://admin:1234@192.168.100.253:554/1/1'
    # cap supports RTSP and video streams from cameras
    cap = cv2.VideoCapture(ADD)
    state = ''

    parser = argparse.ArgumentParser(description="Save imags with rectangles around dark pixels")
    parser.add_argument("-m", default=1, type=int, 
                        help="time interval for saving pictures (minutes)")
    parser.add_argument("-t", default=60, type=int, 
                        help="threshold to determine dark pixels")
    parser.add_argument("-y", default=1000, type=int, 
                        help="hide y-axis")
    args = parser.parse_args()
    while state != 'end':
       main(args)
