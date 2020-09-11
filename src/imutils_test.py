from imutils.video import FPS, VideoStream
import numpy as np
import imutils
import cv2

stream = VideoStream('rtsp://admin:sijung5520@192.168.100.121/profile2/media.smp').start()
fps = FPS().start()

while True:
    frame = stream.read()
    frame = imutils.resize(frame, width=1520, height=800)
    # frame = np.dstack([frame, frame, frame])
    cv2.imshow("frame", frame)
    cv2.waitKey(1)
    fps.update()

stream.release()
cv2.destroyAllWindows()