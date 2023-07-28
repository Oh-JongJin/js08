#!/usr/bin/env python3
#
# Copyright 2021-2023 Sijung Co., Ltd.
#
# Authors:
#     cotjdals5450@gmail.com (Seong Min Chae)
#     5jx2oh@gmail.com (Jongjin Oh)


import os
import time
from cryptography.fernet import Fernet
from model import JS08Settings


def log(ID: str, log_msg: str):
    os.makedirs(f'{JS08Settings.get("log_path")}/SET', exist_ok=True)
    ym = time.strftime('%Y%m%d', time.localtime(time.time()))[2:]

    log_path = JS08Settings.get('log_path')
    if os.path.isfile(f'{log_path}/Log_{ym}.txt'):
        key = JS08Settings.get_user('log_key')
    else:
        key = Fernet.generate_key()
        JS08Settings.set('log_key', key)
        with open(f'{log_path}/SET/SET_{ym}.txt', 'a') as f:
            f.write(str(key.decode('utf-8')))
    fernet = Fernet(key)

    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    with open(f'{log_path}/Log_{ym}.txt', 'a') as f:
        data = f'[{current_time}] {ID} >> {log_msg}'
        encrypt_data = fernet.encrypt(bytes(data, 'utf-8'))
        f.write(f'{str(encrypt_data)}\n')
        # f.write(f'{data}\n')


def decrypt_log(file):
    filename = file.split('.')[0][-6:]
    os.makedirs(f'{JS08Settings.get("log_path")}/SET', exist_ok=True)
    ym = time.strftime('%Y%m%d', time.localtime(time.time()))[2:]

    log_path = JS08Settings.get('log_path')
    if os.path.isfile(f'{log_path}/SET/SET_{filename}.txt'):
        # key = JS08Settings.get_user('log_key')
        with open(f'{log_path}/SET/SET_{filename}.txt', 'r') as f:
            key = f.readlines()[0]
    else:
        key = Fernet.generate_key()
        JS08Settings.set('log_key', key)
        with open(f'{log_path}/SET/SET_{ym}.txt', 'a') as f:
            f.write(str(key.decode('utf-8')))
    fernet = Fernet(key)

    result = []
    with open(file, 'r') as f:
        data = f.readlines()
        for i in data:
            if not i[:3] == 'key':
                output = eval(i)
                result.append(fernet.decrypt(output).decode('utf-8'))
    return result


if __name__ == '__main__':
    # JS08Settings.restore_value('log_key')
    # for i in range(0, 10):
    #     log('TEST', 'TEST Function')
    file = 'D://JS08/log/Log_230531.txt'
    a = decrypt_log(file)
    print(a)
