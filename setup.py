#!/usr/bin/env python3
#
# Copyright 2020-2021 Sijung Co., Ltd.
# 
# Authors: 
#     ruddyscent@gmail.com (Kyungwon Chun)
#     5jx2oh@gmail.com (Jongjin Oh)

from setuptools import find_packages, setup

setup(
    name='js08',
    version='0.1',
    author='Sijung Co., Ltd.',
    author_email='steve17@sijung.com',
    description='AI-powered & image-based visibility meter',
    license='Copyright (C)',
    long_description=open('README.md', 'r').read(),
    long_description_content_type="text/markdown",
    keywords=['visibility', 'weather station'],
    url='http://sijung.com/ko/bbs/page.php?hid=m02_01',
    project_urls={
        'Source Code': 'https://github.com/sijung21/js08'
    },
    packages=find_packages(),
    install_requires=['PyQt5', 'PyQtChart', 'pymongo', 'numpy', 'opencv-python', 'onnxruntime'],
    package_data={'js08.resources': ['*.ui', '*.json', '*.onnx']},
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Environment :: X11 Applications :: Qt',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX :: Linux'
        ],
    entry_points={
        'gui_scripts': ['js08=js08.__main__:main']
    },
    data_files=[
        ('share/applications/', ['js08.desktop'])
        ],
    python_requres='>=3.6'
)
