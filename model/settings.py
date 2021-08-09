#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

from PyQt5.QtCore import QSettings # pylint: disable=no-name-in-module

class Js06Settings:
    settings = QSettings('sijung', 'js06')

    defaults = {
        'camera': 3,
        'normal_shutdown': False,
        'db_host': 'localhost',
        'db_port': 27017,
        'db_admin': 'sijung',
        'db_admin_password': 'sijung_pw',
        'db_user': 'js06',
        'db_user_password': 'js06_pw'
    }

    @classmethod
    def set(cls, key, value):
        cls.settings.setValue(key, value)
    # end of set

    @classmethod
    def get(cls, key):
        return cls.settings.value(
            key,
            cls.defaults[key],
            type(cls.defaults[key])
        )
    # end of get

    @classmethod
    def restore_defaults(cls):
        for key, value in cls.defaults.items():
            cls.set(key, value)
    # end of restore_defaults

# end of Js06Settings

if __name__ == '__main__':
    all_keys = Js06Settings.settings.allKeys()
    for key in all_keys:
        value = Js06Settings.get(key)
        print(f'{key}: {value}')

# end of settings.py
