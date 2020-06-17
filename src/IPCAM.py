"""
To do IP camera output and image capture.
"""

import time
import datetime
import cv2

# ADD is the address to access IP camera.
ADD = 'rtsp://admin:1234@192.168.100.253:554/1/1'
# Cap can call protocols to RTSP and stream videos from cameras.
cap = cv2.VideoCapture(ADD)


def run_ipcam(timer):
    """It has one parameter, 'timer' is the number that sets the capture time period."""

    try:
        ret, frame = cap.read()
        video = cv2.resize(frame, dsize=(1920, 1080))
        cv2.imshow("IP Camera stream", video)

        secs = time.time()

        if datetime.datetime.now().minute % timer == 0 and datetime.datetime.now().second == 0:
            """Capture the video you are streaming and save it as an image."""

            epoch = int(secs)

            print('Saved frame number : ' + str(int(cap.get(1))))
            cv2.imwrite("images/%d.png" % epoch, frame)

            tm = time.gmtime(secs)
            print("[{0}년 {1}월 {2}일 {3}시 {4}분] Saved frame - {5}".format(tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour +
                                                                      9, tm.tm_min, epoch))

            time.sleep(1)
        # Enter 'q' to exit a program in progress.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            print('Close IP Cam')
            exit()

    except Exception as E:
        print(E)


if __name__ == "__main__":
    while True:
        # run_ipcam parameter sets the frequency of video capture.
        run_ipcam(1)
