#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

import platform
import sys

from setuptools import find_packages, setup

python_version = platform.python_version().rsplit('.', maxsplit=1)[0]

mac_v, _, _ = platform.mac_ver()
if mac_v != '':
    mac_v_split = mac_v.split('.')
    mac_major_version = mac_v_split[0]
    mac_minor_version = mac_v_split[1]
    mac_version = '.'.join([mac_major_version, mac_minor_version])
else:
    mac_major_version = None
    mac_version = None

# get the right python string for the version
if python_version == '3.6':
    tflite_python = 'cp36-cp36m'
elif python_version == '3.7':
    tflite_python = 'cp37-cp37m'
elif python_version == '3.8':
    tflite_python = 'cp38-cp38'
elif python_version == '3.9':
    tflite_python = 'cp39-cp39'

# get the right platform and machine strings for the tflite_runtime wheel URL
sys_platform = sys.platform.lower()
machine = platform.machine().lower()
if sys_platform == 'linux':
    tflite_platform = sys_platform
    tflite_machine = machine
elif sys_platform == 'win32':
    tflite_platform = 'win'
    tflite_machine = machine
elif sys_platform == 'darwin' and machine == 'x86_64':
    if mac_version == '10.15':
        tflite_platform = 'macosx_10_15'
    elif mac_major_version == '11':
        tflite_platform = 'macosx_11_0'
    tflite_machine = machine

# add it to the requirements, or print the location to find the version to install
if tflite_python and tflite_platform and tflite_machine:
    tflite_req = f"tflite_runtime @ https://github.com/google-coral/pycoral/releases/download/v2.0.0/tflite_runtime-2.5.0.post1-{tflite_python}-{tflite_platform}_{tflite_machine}.whl"
else:
    print(
        f"Couldn't find tflite_runtime for your platform {sys.platform}, machine {platform.machine()}, python version {python_version}, and mac version {mac_version}. If you are trying to use TensorFlow Lite, please see the install guide for the right version: https://www.tensorflow.org/lite/guide/python#install_just_the_tensorflow_lite_interpreter"
    )

setup(
    name='JS08',
    version='0.1',
    author='Sijung Co., Ltd.',
    author_email='steve17@sijung.com',
    description='AI-powered & image-based visibility meter',
    license='copyright (C)',
    long_description=open('README.md', 'r').read(),
    keywords=['visibility', 'weather station'],
    url='http://sijung.com/ko/bbs/page.php?hid=m02_01',
    project_urls={
        'Source Code': 'https://github.com/sijung21/js06'
    },
    packages=find_packages(),
    install_requires=['PyQt5', 'pymongo', 'numpy', tflite_req],
    package_data={'js06.resources': ['*.ui', '*.json', 'js02.tflite']},
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['js08 = js06.__main__:main']
    }
)
