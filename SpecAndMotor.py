
import sys
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject, QThread
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from MainWindow import Ui_MainWindow
from PyQt5.QtWidgets import QDialog, QFileDialog
import pandas as pd
from datetime import datetime

import seabreeze.spectrometers
from seabreeze.spectrometers import Spectrometer as sm

from FSUBahrmannSMS import FSUBahrmannSMS , FSUBahrmannSMSExc

# import qdarktheme

print(seabreeze.spectrometers.list_devices()[0].serial_number)


doAverage = False
numAverage = 10
integrationTime = 1000
subBackground = False
ContSave = False
running = True
host = "192.168.2.23"
port = 5000
motorNum = 10
doAutoDrive = False
average_wavelength = 1010
steps_to_drive = 0

#moving average without padding
def movingaverage(interval, window_size):
    window= np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')

# Worker class to handle fetching data from the spectrometer in the background
class Worker(QObject):
    data_fetched = pyqtSignal(np.ndarray, np.ndarray)
    def __init__(self, spectrometer):
        super().__init__()  
        self.spectromter = spectrometer
        self.running = True
        
    def run(self):
        global running
        # Simulate data fetching
        print("worker run started")
        while self.running:
            self.spectromter.integration_time_micros(integrationTime)
            time.sleep(0.85)  #if there is no sleep, it will crash if it is not triggered
            wavelengths_spec = self.spectromter.wavelengths()[30:] #cut the first 30 values because the spectrometer gives out a weird artifacat there
            intensities_spec = self.spectromter.intensities()[30:]
            self.data_fetched.emit(wavelengths_spec, intensities_spec)



# Matplotlib canvas class to create a plot
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        # self.ax.set_xlim(900, 1100)
        self.line, = self.ax.plot([], [])        
        self.wavelengths  = []
        self.intensities = []
        self.drift_dist = 0 # parameter to measure the drift
        self.host = host
        self.port = port
        self.motorNum = motorNum
        # self.motorPos = 0
        
        try:
            self.sms = FSUBahrmannSMS(host, port)
            self.sms.setStepTypeStr(1, "1/4")
            # self.motorPos = self.sms.getPosition(self.motorNum)
            # self.sms.setAcc
        except:
            print("no Motor found in canvas")

    def update_plot(self, wavelengths, intensities):
        self.ax.relim()
        self.ax.autoscale_view()
        if subBackground:
            intensities -= background
        if ContSave:
            df = pd.DataFrame()
            df.insert(0,"wavelength",wavelengths)
            df.insert(1,"intensity",intensities)
            df.insert(2,"motor_pos", self.sms.getStateOne(10)[0].counterstr[1:-2])
            df.to_csv(savePath+filePrefix + str(datetime.now()).replace(" ", "").replace(":", "-")+".dat", sep="\t")
        if doAverage:
            intensities = movingaverage(intensities, numAverage)
            
        if doAutoDrive:
            ints2 = intensities
            if not subBackground:
                ints2 -= background
            if not doAverage:
                ints2 = movingaverage(ints2, numAverage)
            wavelength_max = wavelengths[np.argmax(ints2)]
            print("max wavelength = ",wavelength_max)
            #quadratic scaling so that fluctuations near the average dont do much
            self.drift_dist += np.sign(wavelength_max - average_wavelength) * (wavelength_max - average_wavelength)**2
            print("drift dist = ", self.drift_dist)
            
            if self.drift_dist < -2000:
                print("hochfahren")
                self.drive_steps(1)
                self.drift_dist = 0
            if self.drift_dist > 2000:
                print("runterfahren")
                self.drive_steps(-1)
                self.drift_dist = 0
                
            # print("autodrive")
            
            #wenn wellenlänge zu groß wird, dann delay kleiner machen und umgekehrt
        
        self.wavelengths = wavelengths
        self.intensities = intensities
        self.line.set_data(wavelengths, intensities)
        self.draw()    
    
    #functions for motor movement
    def drive_steps(self, steps):
        # global steps_to_drive
        driveTo = steps + float(self.sms.getStateOne(10)[0].counterstr)
        self.sms.StartOne(self.motorNum, driveTo)
    
    # def update_positionDisplay(self):
    #     self.positionDisplay.setText(str(self.canvas.motorPos))
    
    def StopMotor(self):
        self.sms.StopOne(self.motorNum)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()
        self.worker = None
        self.threadRef = None
        self.appRef = None
        self.setWindowTitle("Spectrometer Data Test")
        
        # try:
        #     self.sms = FSUBahrmannSMS(host, port)
        #     self.sms.setStepTypeStr(1, "1/4")
        #     self.motorPos = self.sms.getPosition(self.motorNum)
        #     # self.sms.setAcc
        # except:
        #     print("no Motor found in main")
        
        # self.canvas = MplCanvas()
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.plotLayout = QVBoxLayout(self.plotWidget) 
        self.plotLayout.addWidget(self.canvas)
        
        
        self.spectrometers = list()
        self.initSpectrometerList()

    """
    HIER WERDEN DIE EINZELNEN SIGNALS MIT DEN SLOTS VERBUNDEN
    siehe QT5 Doc
    """
    def connectSignalsSlots(self):
       self.nAverage.valueChanged.connect(self.updateParams)
       self.IntTime.valueChanged.connect(self.updateParams)
       self.checkAverage.clicked.connect(self.updateParams)
       self.checkContSave.clicked.connect(self.updateParams)
       self.TriggerMode.currentIndexChanged.connect(self.updateParams)
       
       # self.SpecLowerBound.valueChanged.connect(self.updateParams)
       self.SpecLowerBound.valueChanged.connect(self.updateParams)
       self.SpecUpperBound.valueChanged.connect(self.updateParams)
       self.nAverage.valueChanged.connect(self.updateParams)

       self.lineEdit_file.textChanged.connect(self.updateParams)
       self.lineEdit_path.textChanged.connect(self.updateParams)
       self.browseButton.clicked.connect(self.browse)
       
       self.btnBackground.clicked.connect(self.save_background)
       self.btnSaveSpec.clicked.connect(self.save_current_spec)
       self.checkSub.clicked.connect(self.updateParams)

       self.btnExit.clicked.connect(self.close_application)
       self.listSpec.currentIndexChanged.connect(self.updateCurrentSpectrometer)
       
       self.numSteps.valueChanged.connect(self.updateParams)
       self.driveBtn.clicked.connect(self.drive_steps)
       self.checkAutoDrive.clicked.connect(self.updateParams)
       self.StopBtn.clicked.connect(self.StopMotor)
       self.motor_pos_btn.clicked.connect(self.update_positionDisplay)
       # self.positionDisplay.
       # self.update_positionDisplay()
    
    def update_plot(self, wavelengths, intensities):
        self.canvas.update_plot(wavelengths, intensities)
        
    def updateCurrentSpectrometer(self):
        if self.worker is not None:
            self.stopCurrentSpektrometer()
        serial = self.spectrometers[self.listSpec.currentIndex()]
        self.openSpectrometer(serial)
        self.startSpektrometer()
        
    # functions for opening and closing a new spectrometer, when a new one is selected
    def openSpectrometer(self, serialNumber):
        print("opening new spectrometer")
        spec = sm.from_serial_number(serialNumber)
        spec.trigger_mode(0)
        self.spec = spec
    def startSpektrometer(self):
        self.worker = Worker(self.spec)
        thread = QThread()
        self.worker.moveToThread(thread)
        thread.started.connect(self.worker.run)
        thread.start()
        self.worker.data_fetched.connect(self.update_plot)
        self.setThreadReference(thread)
    def stopCurrentSpektrometer(self):
        print("closing current spectrometer")
        self.worker.running = False
        self.threadRef.terminate()
        time.sleep(1.05)  #sleep so the worker is always terminated before the spectrometer is closed
        self.spec.close() #close connection to spectrometer
        
        
    def setThreadReference(self, thread):
        self.threadRef = thread
        
    def setAppReference(self, app):
        self.appRef = app
        
    
    def initSpectrometerList(self):
        print("")
        for index, spectrometer in enumerate(seabreeze.spectrometers.list_devices()):
            serialNum = spectrometer.serial_number
            self.spectrometers.append(serialNum)
            self.listSpec.addItem(serialNum)
        
    def save_background(self):
        global background
        background = self.canvas.intensities
        print(background)
        
    def save_current_spec(self):
        df = pd.DataFrame()
        df.insert(0,"wavelength",self.canvas.wavelengths)
        df.insert(0,"intensity",self.canvas.intensities)
        df.to_csv(savePath+filePrefix + str(datetime.now()).replace(" ", "").replace(":", "-")+".dat", sep="\t")
        
    def set_axis_limits(self, xlim):
        self.canvas.ax.set_xlim(xlim)
        self.canvas.draw()
    
    def close_application(self):    
        self.close()
        self.stopCurrentSpektrometer()
        try:
            self.canvas.sms.disconnect()
        except:
            print("no motor to close")
        print("FinishedClosing Bye")
        
        if self.appRef is not None:
            self.appRef.quit()
        
    def browse(self):
        savePath = QFileDialog.getExistingDirectory() +"/"
        self.lineEdit_path.setText(savePath) 
        
    """functions for controlling the step motor"""
    # def openMotor(self, motorNum):
    #     print("opening new motor")
    #     sms = FSUBahrmannSMS(self.host, self.port)
    #     sms.initMotors()
    #     self.sms = sms
    
    # def get_motor_position(self):
    #     print(self.sms.getPosition(self.motorNum))
    #     return self.sms.getPosition(self.motorNum)
    
    def drive_steps(self):
        self.update_positionDisplay()
        self.canvas.drive_steps(steps_to_drive)
    
    def update_positionDisplay(self):
        self.positionDisplay.setText(self.canvas.sms.getStateOne(10)[0].counterstr[:-2])
    
    def StopMotor(self):
        self.canvas.StopMotor()
        self.update_positionDisplay()
    
    """
    Falls die Parameter geändert werden soll das aktualisiert werden
    """
    def updateParams(self):
        global subBackground, lowerBounds, upperBounds, doAverage, numAverage, integrationTime
        global averageSum,averageCount,writeContinu, ContSave, TriggerIndex
        global filePrefix, savePath, FFTlower, FFTupper, writeAllAv, windowFunction, doOffset, linOffset, doFFTRemoveAv
        global steps_to_drive, doAutoDrive
        

        # doAlwaysWrite = self.checkWrite.isChecked()
        subBackground = self.checkSub.isChecked()
        
        lowerBounds = self.SpecLowerBound.value()
        upperBounds = self.SpecUpperBound.value()

        doAverage = self.checkAverage.isChecked()
        numAverage = self.nAverage.value()
        
        integrationTime = self.IntTime.value() #in micro seconds
        
        TriggerIndex = self.TriggerMode.currentIndex()
        self.spec.trigger_mode(TriggerIndex)
        ContSave = self.checkContSave.isChecked()
        filePrefix = self.lineEdit_file.text()
        savePath = self.lineEdit_path.text()
        
        self.set_axis_limits((lowerBounds, upperBounds))
        
        steps_to_drive = self.numSteps.value()
        doAutoDrive = self.checkAutoDrive.isChecked()
        
        self.update_positionDisplay()
        # print(steps_to_drive)

        
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main_window = MainWindow()
    main_window.setAppReference(app)

    main_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()








































