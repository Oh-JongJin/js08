#!/usr/bin/env python3

"""Acquire images from CSI camera

Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
NVIDIA Jetson Nano Developer Kit using OpenCV drivers for the camera 
and OpenCV are included in the base image

gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
Defaults to 1280x720 @ 60fps
Flip the image by setting the flip_method (most common values: 0 and 2)
display_width and display_height determine the size of the window on the screen

Reference: https://github.com/JetsonHacksNano/CSI-Camera
"""

import cv2

def gstreamer_pipeline(capture_width: int = 1280,
                       capture_height: int = 720,
                       display_width: int = 1280,
                       display_height: int = 720,
                       framerate: int = 60,
                       flip_method: int = 0):
    return (f"nvarguscamerasrc ! "
            f"video/x-raw(memory:NVMM), "
            f"width=(int){capture_width:d}, height=(int){capture_height:d}, "
            f"format=(string)NV12, framerate=(fraction){framerate:d}/1 ! "
            f"nvvidconv flip-method={flip_method:d} ! "
            f"video/x-raw, width=(int){display_width:d}, "
            f"height=(int){display_height:d}, "
            f"format=(string)BGRx ! "
            f"videoconvert ! "
            f"video/x-raw, format=(string)BGR ! appsink")

def show_camera():
    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    print(gstreamer_pipeline(flip_method=0))
    cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    if cap.isOpened():
        window_handle = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
        # Window
        while cv2.getWindowProperty("CSI Camera", 0) >= 0:
            ret_val, img = cap.read()
            cv2.imshow("CSI Camera", img)
            # This also acts as
            keyCode = cv2.waitKey(30) & 0xFF
            # Stop the program on the ESC key
            if keyCode == 27:
                break
        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Unable to open camera")

if __name__ == "__main__":
    show_camera()
