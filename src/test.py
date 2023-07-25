import os
import time
import pandas as pd

current_time = time.strftime('%Y%m%d%H%M00', time.localtime(time.time()))
predict_path = "predict"
predict_vis_file = current_time[:8] + ".csv"
predict_file_path =  os.path.join(predict_path, predict_vis_file)
print("predict__file__name : ", predict_vis_file)

if os.path.isdir(f'{predict_path}') is False:
    os.makedirs(predict_path, exist_ok=True)
    df_predict = pd.DataFrame(columns=['date', 'predict_value'])
    df_predict.to_csv(predict_file_path, mode='w', index=False)
    print("create predict path")
else:
    df_predict = pd.read_csv(predict_file_path)
print(df_predict.head())
df_predict = pd.concat([df_predict, pd.DataFrame([[current_time, str(15000)]],columns=['date', 'predict_value'])], join='outer')
print(df_predict.head())
df_predict.to_csv(predict_file_path, mode='w', index=False)
print("create predict file")