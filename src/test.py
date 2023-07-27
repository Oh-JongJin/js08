import os
import time
import pandas as pd

now = pd.Timestamp.now()
current_time = now.timestamp()
print("current_time : ", current_time)
# print("time.time : ", time.strftime('%Y%m%d%H%M00', time.localtime(time.time())))