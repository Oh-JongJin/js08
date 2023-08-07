# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'user_menu.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QTextBrowser, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(271, 259)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridWidget = QWidget(Dialog)
        self.gridWidget.setObjectName(u"gridWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.gridWidget.sizePolicy().hasHeightForWidth())
        self.gridWidget.setSizePolicy(sizePolicy1)
        self.gridWidget.setStyleSheet(u"background-color:rgb(22,32,42);")
        self.gridLayout_2 = QGridLayout(self.gridWidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.etc_verticalLayout = QVBoxLayout()
        self.etc_verticalLayout.setObjectName(u"etc_verticalLayout")
        self.setting_label = QLabel(self.gridWidget)
        self.setting_label.setObjectName(u"setting_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.setting_label.sizePolicy().hasHeightForWidth())
        self.setting_label.setSizePolicy(sizePolicy2)
        font = QFont()
        font.setFamilies([u"Noto Sans"])
        font.setPointSize(23)
        self.setting_label.setFont(font)
        self.setting_label.setStyleSheet(u"background-color:rgb(27,49,70);\n"
"color: #ffffff;")

        self.etc_verticalLayout.addWidget(self.setting_label)

        self.id_horizontalLayout = QHBoxLayout()
        self.id_horizontalLayout.setSpacing(6)
        self.id_horizontalLayout.setObjectName(u"id_horizontalLayout")
        self.id_label = QLabel(self.gridWidget)
        self.id_label.setObjectName(u"id_label")
        sizePolicy1.setHeightForWidth(self.id_label.sizePolicy().hasHeightForWidth())
        self.id_label.setSizePolicy(sizePolicy1)
        self.id_label.setMinimumSize(QSize(0, 34))
        font1 = QFont()
        font1.setFamilies([u"Noto Sans"])
        font1.setPointSize(10)
        self.id_label.setFont(font1)
        self.id_label.setStyleSheet(u"background-color:rgb(27,49,70);\n"
"color: #ffffff;")

        self.id_horizontalLayout.addWidget(self.id_label)

        self.id_lineEdit = QTextBrowser(self.gridWidget)
        self.id_lineEdit.setObjectName(u"id_lineEdit")
        sizePolicy1.setHeightForWidth(self.id_lineEdit.sizePolicy().hasHeightForWidth())
        self.id_lineEdit.setSizePolicy(sizePolicy1)
        self.id_lineEdit.setMinimumSize(QSize(0, 34))
        self.id_lineEdit.setMaximumSize(QSize(196, 34))
        font2 = QFont()
        font2.setPointSize(12)
        self.id_lineEdit.setFont(font2)
        self.id_lineEdit.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.id_horizontalLayout.addWidget(self.id_lineEdit)


        self.etc_verticalLayout.addLayout(self.id_horizontalLayout)

        self.pw_horizontalLayout_3 = QHBoxLayout()
        self.pw_horizontalLayout_3.setSpacing(6)
        self.pw_horizontalLayout_3.setObjectName(u"pw_horizontalLayout_3")
        self.pw_label_3 = QLabel(self.gridWidget)
        self.pw_label_3.setObjectName(u"pw_label_3")
        sizePolicy1.setHeightForWidth(self.pw_label_3.sizePolicy().hasHeightForWidth())
        self.pw_label_3.setSizePolicy(sizePolicy1)
        self.pw_label_3.setMinimumSize(QSize(0, 34))
        font3 = QFont()
        font3.setFamilies([u"Noto Sans KR Medium"])
        font3.setPointSize(10)
        self.pw_label_3.setFont(font3)
        self.pw_label_3.setStyleSheet(u"background-color:rgb(27,49,70);\n"
"color: #ffffff;")

        self.pw_horizontalLayout_3.addWidget(self.pw_label_3)

        self.current_pw = QLineEdit(self.gridWidget)
        self.current_pw.setObjectName(u"current_pw")
        sizePolicy1.setHeightForWidth(self.current_pw.sizePolicy().hasHeightForWidth())
        self.current_pw.setSizePolicy(sizePolicy1)
        self.current_pw.setMinimumSize(QSize(0, 34))
        self.current_pw.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.pw_horizontalLayout_3.addWidget(self.current_pw)


        self.etc_verticalLayout.addLayout(self.pw_horizontalLayout_3)

        self.pw_horizontalLayout = QHBoxLayout()
        self.pw_horizontalLayout.setSpacing(6)
        self.pw_horizontalLayout.setObjectName(u"pw_horizontalLayout")
        self.pw_label = QLabel(self.gridWidget)
        self.pw_label.setObjectName(u"pw_label")
        sizePolicy1.setHeightForWidth(self.pw_label.sizePolicy().hasHeightForWidth())
        self.pw_label.setSizePolicy(sizePolicy1)
        self.pw_label.setMinimumSize(QSize(0, 34))
        self.pw_label.setFont(font3)
        self.pw_label.setStyleSheet(u"background-color:rgb(27,49,70);\n"
"color: #ffffff;")

        self.pw_horizontalLayout.addWidget(self.pw_label)

        self.new_pw = QLineEdit(self.gridWidget)
        self.new_pw.setObjectName(u"new_pw")
        sizePolicy1.setHeightForWidth(self.new_pw.sizePolicy().hasHeightForWidth())
        self.new_pw.setSizePolicy(sizePolicy1)
        self.new_pw.setMinimumSize(QSize(0, 34))
        self.new_pw.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.pw_horizontalLayout.addWidget(self.new_pw)


        self.etc_verticalLayout.addLayout(self.pw_horizontalLayout)

        self.pw_horizontalLayout_4 = QHBoxLayout()
        self.pw_horizontalLayout_4.setSpacing(6)
        self.pw_horizontalLayout_4.setObjectName(u"pw_horizontalLayout_4")
        self.pw_label_4 = QLabel(self.gridWidget)
        self.pw_label_4.setObjectName(u"pw_label_4")
        sizePolicy1.setHeightForWidth(self.pw_label_4.sizePolicy().hasHeightForWidth())
        self.pw_label_4.setSizePolicy(sizePolicy1)
        self.pw_label_4.setMinimumSize(QSize(0, 34))
        self.pw_label_4.setFont(font3)
        self.pw_label_4.setStyleSheet(u"background-color:rgb(27,49,70);\n"
"color: #ffffff;")

        self.pw_horizontalLayout_4.addWidget(self.pw_label_4)

        self.new_pw_check = QLineEdit(self.gridWidget)
        self.new_pw_check.setObjectName(u"new_pw_check")
        sizePolicy1.setHeightForWidth(self.new_pw_check.sizePolicy().hasHeightForWidth())
        self.new_pw_check.setSizePolicy(sizePolicy1)
        self.new_pw_check.setMinimumSize(QSize(0, 34))
        self.new_pw_check.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.pw_horizontalLayout_4.addWidget(self.new_pw_check)


        self.etc_verticalLayout.addLayout(self.pw_horizontalLayout_4)

        self.buttonBox = QDialogButtonBox(self.gridWidget)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy1.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy1)
        font4 = QFont()
        font4.setFamilies([u"Noto Sans KR Medium"])
        font4.setPointSize(9)
        self.buttonBox.setFont(font4)
        self.buttonBox.setStyleSheet(u"background-color:rgb(27,49,70);\n"
"color: #ffffff;")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)

        self.etc_verticalLayout.addWidget(self.buttonBox)


        self.gridLayout_2.addLayout(self.etc_verticalLayout, 0, 0, 1, 1)


        self.gridLayout.addWidget(self.gridWidget, 0, 0, 1, 1)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Setting", None))
        self.setting_label.setText(QCoreApplication.translate("Dialog", u"   Settings", None))
        self.id_label.setText(QCoreApplication.translate("Dialog", u" ID", None))
        self.pw_label_3.setText(QCoreApplication.translate("Dialog", u" \ud604\uc7ac \ube44\ubc00\ubc88\ud638", None))
        self.pw_label.setText(QCoreApplication.translate("Dialog", u" \uc0c8 \ube44\ubc00\ubc88\ud638", None))
        self.pw_label_4.setText(QCoreApplication.translate("Dialog", u" \uc0c8 \ube44\ubc00\ubc88\ud638 \ud655\uc778", None))
    # retranslateUi

