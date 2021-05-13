from PyQt5.QtCore import QThread
from cv2 import VideoCapture, imwrite, destroyAllWindows


class FrameSave(QThread):
    def __init__(self, epoch, filepath):
        super().__init__()
        self.epoch = epoch
        self.filepath = filepath

    def run(self):
        try:
            image_path = os.path.join(self.filepath, "image", "PNM", f"{self.epoch[2:6]}")
            fileName = f"{self.epoch}"

            cap = VideoCapture('rtsp://admin:sijung5520@192.168.100.100/profile2/media.smp')
            if not cap.isOpened():
                sys.exit()
            ret, img = cap.read()
            cap.release()
            destroyAllWindows()

        except Exception:
            err = traceback.format_exc()
            print(err)
            # sys.exit()
