#!/usr/bin/env python3
#
# Copyright 2021-2022 Sijung Co., Ltd.
#
# Authors:
#     cotjdals5450@gmail.com (Seong Min Chae)
#     5jx2oh@gmail.com (Jongjin Oh)


import time


def log(classify: str, log_msg: str, ID: str):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    with open('Log.txt', 'a') as f:
        f.write(f'[{current_time}][{classify}|{ID}] >> {log_msg}\n')
