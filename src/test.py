from datetime import datetime, timedelta
import os
import time
import pandas as pd
from PySide6.QtCore import (Qt, Slot, QRect,
                            QTimer, QObject, QDateTime)

now = pd.Timestamp.now()
current_time = now.timestamp()
print("now", now)
print("current_time : ", current_time)
# print("time.time : ", time.strftime('%Y%m%d%H%M00', time.localtime(time.time())))
epoch = QDateTime.currentSecsSinceEpoch()
current_time = time.strftime('%Y-%m-%d %H:%M:00', time.localtime(epoch))
print(epoch)
print(current_time)

# 문자열로 된 timestamp를 datetime 객체로 변환
timestamp_datetime = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")

print(timestamp_datetime.timestamp())

epoch_value = 1690518240.0
timestamp_datetime = datetime.fromtimestamp(epoch_value)
print(epoch_value)
new_datetime = timestamp_datetime + timedelta(minutes=10)
print(new_datetime)