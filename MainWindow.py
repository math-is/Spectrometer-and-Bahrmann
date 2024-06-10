# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(875, 917)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 10, 831, 781))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.plotWidget = QtWidgets.QWidget(self.gridLayoutWidget)
        self.plotWidget.setObjectName("plotWidget")
        self.gridLayout.addWidget(self.plotWidget, 22, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 15, 0, 1, 1)
        self.SpecUpperBound = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.SpecUpperBound.setMaximum(10000)
        self.SpecUpperBound.setProperty("value", 1100)
        self.SpecUpperBound.setObjectName("SpecUpperBound")
        self.gridLayout.addWidget(self.SpecUpperBound, 4, 4, 1, 1)
        self.driveBtn = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.driveBtn.setStyleSheet("background-color: rgb(105, 205, 235);\n"
"color: rgb(0, 0, 0);")
        self.driveBtn.setObjectName("driveBtn")
        self.gridLayout.addWidget(self.driveBtn, 18, 2, 1, 1)
        self.numSteps = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.numSteps.setMinimum(-40000)
        self.numSteps.setMaximum(40000)
        self.numSteps.setObjectName("numSteps")
        self.gridLayout.addWidget(self.numSteps, 18, 4, 1, 1)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 4, 2, 1, 1)
        self.nAverage = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.nAverage.setMinimum(1)
        self.nAverage.setMaximum(1000)
        self.nAverage.setProperty("value", 10)
        self.nAverage.setObjectName("nAverage")
        self.gridLayout.addWidget(self.nAverage, 3, 4, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 6, 2, 1, 1)
        self.btnSaveSpec = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btnSaveSpec.setStyleSheet("background-color: rgb(45, 230, 15);\n"
"color: rgb(0, 0, 0);")
        self.btnSaveSpec.setObjectName("btnSaveSpec")
        self.gridLayout.addWidget(self.btnSaveSpec, 13, 2, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.IntTime = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.IntTime.setMinimum(1000)
        self.IntTime.setMaximum(1000000)
        self.IntTime.setProperty("value", 1000)
        self.IntTime.setObjectName("IntTime")
        self.gridLayout.addWidget(self.IntTime, 7, 4, 1, 1)
        self.listSpec = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.listSpec.setStyleSheet("background-color: rgb(220, 220, 220);\n"
"color: rgb(0, 0, 0);")
        self.listSpec.setObjectName("listSpec")
        self.gridLayout.addWidget(self.listSpec, 1, 2, 1, 1)
        self.checkSub = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkSub.setObjectName("checkSub")
        self.gridLayout.addWidget(self.checkSub, 8, 4, 1, 1)
        self.checkContSave = QtWidgets.QRadioButton(self.gridLayoutWidget)
        self.checkContSave.setObjectName("checkContSave")
        self.gridLayout.addWidget(self.checkContSave, 16, 2, 1, 1)
        self.TriggerMode = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.TriggerMode.setEditable(False)
        self.TriggerMode.setObjectName("TriggerMode")
        self.TriggerMode.addItem("")
        self.TriggerMode.addItem("")
        self.TriggerMode.addItem("")
        self.TriggerMode.addItem("")
        self.gridLayout.addWidget(self.TriggerMode, 2, 4, 1, 1)
        self.lineEdit_file = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_file.setObjectName("lineEdit_file")
        self.gridLayout.addWidget(self.lineEdit_file, 14, 2, 1, 1)
        self.SpecLowerBound = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.SpecLowerBound.setMaximum(10000)
        self.SpecLowerBound.setProperty("value", 900)
        self.SpecLowerBound.setObjectName("SpecLowerBound")
        self.gridLayout.addWidget(self.SpecLowerBound, 6, 4, 1, 1)
        self.browseButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.browseButton.setStyleSheet("background-color: rgb(207, 190, 150);\n"
"color: rgb(0, 0, 0);")
        self.browseButton.setObjectName("browseButton")
        self.gridLayout.addWidget(self.browseButton, 14, 4, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 7, 2, 1, 1)
        self.btnBackground = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btnBackground.setStyleSheet("background-color: rgb(245, 245, 125);\n"
"color: rgb(0, 0, 0);")
        self.btnBackground.setObjectName("btnBackground")
        self.gridLayout.addWidget(self.btnBackground, 8, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 14, 0, 1, 1)
        self.checkAverage = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkAverage.setObjectName("checkAverage")
        self.gridLayout.addWidget(self.checkAverage, 3, 2, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 17, 0, 1, 1)
        self.listMotor = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.listMotor.setCurrentText("")
        self.listMotor.setObjectName("listMotor")
        self.gridLayout.addWidget(self.listMotor, 17, 2, 1, 1)
        self.positionDisplay = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.positionDisplay.setObjectName("positionDisplay")
        self.gridLayout.addWidget(self.positionDisplay, 19, 2, 1, 1)
        self.checkAutoDrive = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkAutoDrive.setObjectName("checkAutoDrive")
        self.gridLayout.addWidget(self.checkAutoDrive, 18, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 19, 0, 1, 1)
        self.motor_pos_btn = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.motor_pos_btn.setObjectName("motor_pos_btn")
        self.gridLayout.addWidget(self.motor_pos_btn, 17, 4, 1, 1)
        self.lineEdit_path = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_path.setObjectName("lineEdit_path")
        self.gridLayout.addWidget(self.lineEdit_path, 15, 2, 1, 1)
        self.StopBtn = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.StopBtn.setStyleSheet("background-color: rgb(245, 55, 25);\n"
"color: rgb(0, 0, 0);")
        self.StopBtn.setObjectName("StopBtn")
        self.gridLayout.addWidget(self.StopBtn, 20, 2, 1, 1)
        self.btnExit = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btnExit.setStyleSheet("background-color: rgb(190, 120, 255);\n"
"color: rgb(0, 0, 0);")
        self.btnExit.setObjectName("btnExit")
        self.gridLayout.addWidget(self.btnExit, 20, 4, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 875, 21))
        self.menubar.setObjectName("menubar")
        self.menuSpecra_Viewer = QtWidgets.QMenu(self.menubar)
        self.menuSpecra_Viewer.setStyleSheet("background-color: rgb(71, 70, 72);")
        self.menuSpecra_Viewer.setObjectName("menuSpecra_Viewer")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuSpecra_Viewer.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_5.setText(_translate("MainWindow", "save path"))
        self.driveBtn.setText(_translate("MainWindow", "Drive Steps"))
        self.label.setText(_translate("MainWindow", "Spectrum Upperbound"))
        self.label_2.setText(_translate("MainWindow", "Spectrum Lowerbound"))
        self.btnSaveSpec.setText(_translate("MainWindow", "Save current Spectra"))
        self.label_6.setText(_translate("MainWindow", "Spectrometer"))
        self.checkSub.setText(_translate("MainWindow", "Substract Background"))
        self.checkContSave.setText(_translate("MainWindow", "Continous Save"))
        self.TriggerMode.setItemText(0, _translate("MainWindow", "trigger1"))
        self.TriggerMode.setItemText(1, _translate("MainWindow", "trigger2"))
        self.TriggerMode.setItemText(2, _translate("MainWindow", "trigger3"))
        self.TriggerMode.setItemText(3, _translate("MainWindow", "trigger4"))
        self.browseButton.setText(_translate("MainWindow", "Browse"))
        self.label_3.setText(_translate("MainWindow", "Integration time"))
        self.btnBackground.setText(_translate("MainWindow", "Save Background"))
        self.label_4.setText(_translate("MainWindow", "Fileprefix:"))
        self.checkAverage.setText(_translate("MainWindow", "Average over:"))
        self.label_7.setText(_translate("MainWindow", "Motor"))
        self.checkAutoDrive.setText(_translate("MainWindow", "Auto Drive"))
        self.label_8.setText(_translate("MainWindow", "position"))
        self.motor_pos_btn.setText(_translate("MainWindow", "motor pos"))
        self.StopBtn.setText(_translate("MainWindow", "STOP"))
        self.btnExit.setText(_translate("MainWindow", "EXIT"))
        self.menuSpecra_Viewer.setTitle(_translate("MainWindow", "Specra-Viewer"))

