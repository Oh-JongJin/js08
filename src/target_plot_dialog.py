# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'target_plot_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TargetPlot(object):
    def setupUi(self, TargetPlot, x: int, y: int):
        TargetPlot.setObjectName("TargetPlot")
        TargetPlot.resize(x, y)

        self.retranslateUi(TargetPlot)
        QtCore.QMetaObject.connectSlotsByName(TargetPlot)

    def retranslateUi(self, TargetPlot):
        _translate = QtCore.QCoreApplication.translate
        TargetPlot.setWindowTitle(_translate("TargetPlot", "Target Plot"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    TargetPlot = QtWidgets.QDialog()
    ui = Ui_TargetPlot()
    ui.setupUi(TargetPlot)
    TargetPlot.show()
    sys.exit(app.exec_())
