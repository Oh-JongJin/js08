#!/usr/bin/env python3
#
# Copyright 2021-2023 Sijung Co., Ltd.
#
# Authors:
#     cotjdals5450@gmail.com (Seong Min Chae)
#     5jx2oh@gmail.com (Jongjin Oh)


from PySide6.QtWidgets import QDialog, QFileDialog, QLineEdit, QMessageBox
from PySide6.QtGui import QIcon

from model import JS08Settings
from resources.user_menu import Ui_Dialog
from save_log import log

import warnings

warnings.filterwarnings('ignore')


class JS08UserSettingWidget(QDialog, Ui_Dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon('JS08_Logo.ico'))

        self.id_lineEdit.setText(JS08Settings.get('current_id'))
        self.current_pw.setEchoMode(QLineEdit.Password)
        self.new_pw.setEchoMode(QLineEdit.Password)
        self.new_pw_check.setEchoMode(QLineEdit.Password)

        self.buttonBox.accepted.connect(self.accept_click)
        self.buttonBox.rejected.connect(self.reject_click)

    def accept_click(self):
        current_id = JS08Settings.get('current_id')

        user = JS08Settings.get_user('user')
        # user_id = list(JS08Settings.get_user('user').keys())
        # user_pw = list(JS08Settings.get_user('user').values())

        input_current_pw = self.current_pw.text()
        input_new_pw = self.new_pw.text()
        input_new_pw_check = self.new_pw_check.text()

        if input_current_pw == JS08Settings.get('current_pw') and \
                input_new_pw == input_new_pw_check:
            user[current_id] = input_new_pw

            JS08Settings.set('user', user)
            JS08Settings.set('current_pw', input_new_pw)

            if input_current_pw != input_new_pw:
                log(JS08Settings.get('current_id'), f'Change Password ({input_current_pw}) -> ({input_new_pw})')

            self.close()

        else:
            QMessageBox.warning(self, 'Warning', 'Password Error')

    def reject_click(self):
        self.close()


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    ui = JS08UserSettingWidget()
    ui.show()
    sys.exit(app.exec())
