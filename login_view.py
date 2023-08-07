#!/usr/bin/env python3
#
# Copyright 2021-2023 Sijung Co., Ltd.
#
# Authors:
#     cotjdals5450@gmail.com (Seong Min Chae)
#     5jx2oh@gmail.com (Jongjin Oh)


import sys
import random
import string
import time
from datetime import datetime

from PySide6.QtWidgets import QDialog, QLineEdit, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from model import JS08Settings
from resources.login_window import Ui_Dialog
from save_log import log


class LoginWindow(QDialog, Ui_Dialog):

    def __init__(self):
        super(LoginWindow, self).__init__()

        self.setupUi(self)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.show()

        self.sijunglogo.setIcon(QIcon('resources/asset/f_logo.png'))
        self.login_button.clicked.connect(self.login_click)
        self.login_button.setShortcut('Return')

        self.admin_id = JS08Settings.get('admin_id')
        self.admin_pw = JS08Settings.get('admin_pw')
        self.user_id = list(JS08Settings.get_user('user').keys())
        self.user_pw = list(JS08Settings.get_user('user').values())
        self.id = [self.admin_id]
        self.id.extend(self.user_id)
        self.pw = [self.admin_pw]
        self.pw.extend(self.user_pw)
        self.account = {}
        for i in range(len(self.id)):
            self.account[self.id[i]] = self.pw[i]
        self.id = list(self.account.keys())
        self.pw = list(self.account.values())

        self.pw_lineEdit.setEchoMode(QLineEdit.Password)

        self.flag = 0

    def login_click(self):
        input_id = self.id_lineEdit.text()
        input_pw = self.pw_lineEdit.text()
        if input_id in self.account.keys() and input_pw == self.account[f'{input_id}']:
            if input_id == JS08Settings.get('admin_id'):
                now = datetime.now()
                if JS08Settings.get('login_time') != '':
                    agga = datetime.strptime(JS08Settings.get('login_time'), '%Y-%m-%d %H:%M:%S')
                    diff = now - agga
                    if diff.seconds >= 60:
                        JS08Settings.set('right', 'administrator')
                        JS08Settings.set('login_flag', 0)
                    else:
                        QMessageBox.warning(None, '계정 일시 차단', '잠시 후에 다시 로그인을 시도해 주세요.')
                        self.close()
                        sys.exit()
            else:
                JS08Settings.set('right', 'user')
            log(input_id, 'Login')
            JS08Settings.set('current_id', input_id)
            JS08Settings.set('current_pw', input_pw)
            self.close()

        elif not input_id in self.account.keys():
            self.alert_label.setText('없는 아이디 입니다.')

        else:
            self.flag = self.flag + 1

            self.alert_label.setText(f'비밀번호가 올바르지 않습니다. ({self.flag} / 5)')

            if self.flag > 5 and input_id != JS08Settings.get('admin_id'):
                log(input_id, f'Account Blocking, Password initialized')
                # log(input_id, f'User ({input_id}) Account Blocking')
                QMessageBox.warning(None, '비밀번호 초기화', '비밀번호 5회 오류로 인해 비밀번호가 교체됩니다. '
                                                      '관리자에게 문의하세요.')

                rand_str = ''
                for i in range(10):
                    rand_str += str(random.choice(string.ascii_uppercase + string.digits))
                user = JS08Settings.get_user('user')
                user[input_id] = rand_str
                JS08Settings.set('user', user)
                self.close()
                sys.exit()

            elif self.flag > 5 and input_id == JS08Settings.get('admin_id'):
                if JS08Settings.get('login_flag') >= 3:
                    JS08Settings.restore_value('admin_pw')
                    QMessageBox.information(None, '비밀번호 초기화', '비밀번호가 초기화 됩니다.')
                    log(input_id, 'Administrator password initialized')
                    self.close()
                    sys.exit()
                else:
                    log(input_id, 'Administrator login failed')
                    QMessageBox.warning(None, '비밀번호 5회 오류', '잠시 후에 다시 로그인을 시도해 주세요.')
                    JS08Settings.set('login_time', time.strftime('%Y-%m-%d %H:%M:00', time.localtime()))
                    JS08Settings.set('login_flag', JS08Settings.get('login_flag') + 1)
                    self.close()
                    sys.exit()

            else:
                pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            sys.exit()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = LoginWindow()
    sys.exit(app.exec())
