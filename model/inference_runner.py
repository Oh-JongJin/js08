#!/usr/bin/env python3

from PyQt5.QtCore import QRunnable, pyqtSlot

class Js06InferenceRunner(QRunnable):
    def __init__(self, i):
        super().__init__()
        self.i = i
        self.setAutoDelete(True)

    @pyqtSlot()
    def run(self):
        print(f"{self.i}: Sleeping 3 seconds")
        import time
        time.sleep(3)

# end of Js06InferenceRunner

if __name__ == '__main__':
    from PyQt5.QtCore import QThreadPool # pylint: disable=no-name-in-module

    threadpool = QThreadPool()
    print("Multithreading with maximum "
    f"{threadpool.maxThreadCount()} threads")

    NUM_RUNNER = 2 * threadpool.maxThreadCount()
    print(f"Starting {NUM_RUNNER}:")
    for i in range(NUM_RUNNER):
        worker = Js06InferenceRunner(i)
        threadpool.start(worker)

# end of inference_runner.py