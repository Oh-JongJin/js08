from PyQt5.QtCore import QThread
from cv2 import VideoCapture, imwrite, destroyAllWindows


class FrameSave(QThread):
    def save_frame(self):
        try:
            image_path = os.path.join(self.filepath, "image", "PNM", f"{self.epoch[2:6]}")
            fileName = f"{self.epoch}"

            cap = VideoCapture('rtsp://admin:sijung5520@192.168.100.100/profile2/media.smp')
            if not cap.isOpened():
                sys.exit()
            ret, img = cap.read()
            if not os.path.isdir(image_path):
                os.makedirs(image_path)
            if not os.path.isfile(f"{image_path}/{fileName}.png"):
                imwrite(f'{image_path}/{fileName}.png', img)
            cap.release()
            destroyAllWindows()

        except Exception:
            err = traceback.format_exc()
            print(err)
            sys.exit()
