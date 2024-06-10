# -*- coding: utf-8 -*-
"""
SMS-Library for using SMS-CONTROLLER(UNI-JENA) over Network

Included only VC-1 Commands and Parameters !!!!

Created on Wed Jul 14 11:34:19 2021

Fixed Errors on 20.08.2021 -> Version 1.0
created on 17.04.2023 -> Finally Version 1.1
new in this version:
use status_class ->counter and status_flags
added new command: GET_FR_RAMP_STEPTYPE ( renamed: GET_MOVEMENT), GET_CURRENT, GET_NAME, GO_ZERO, GET_STATUS_SHORT

@authors: schulze & bahrmann & Alexander Kessler (alexander.kessler@uni-jena.de or a.kessler@hi-jena.gsi.de)
"""

import socket

# Hardware-Rückmeldungen(Software-Handshake)
handshake_list = [b'\xff', b'\xe1', b'\xe2', b'\xe3', b'\xe4', b'\xe5', b'\xe6', b'\xe7',
                  b'\xe8', b'\xe9', b'\xea', b'\xeb', b'\xec', b'\xed', b'\xee', b'\xef']

BUFSIZE = 1024

# Befehlscodes
RUN_STEPS = 0x02
STOP = 0x03
RESET = 0x04
GO_END_L = 0x05
GO_END_R = 0x06
GET_STATUS = 0x07
GO_ZERO = 0x08
GET_CURRENT = 0x09
GET_STATUS_SHORT = 0x0A
GET_NAME = 0x0B
GET_FR_RAMP_STEPTYPE = 0x12  # Früher GET_MOVEMENT

# Schrittartcodes
STEPTYPE_1_1 = 0x00
STEPTYPE_1_2 = 0x02
STEPTYPE_1_4 = 0x04
STEPTYPE_1_8 = 0x06

# Schrittartzuordnung
stepTypeStr ={STEPTYPE_1_1: "1/1", STEPTYPE_1_2: "1/2", STEPTYPE_1_4: "1/4", STEPTYPE_1_8: "1/8"}
freq_dict = {
            #Frequenz dict automatisch erzeugt in der Form F100Hz: 0x01 .... F4000Hz: 0x26 (...=d40)
            f"F{i}00Hz": 0x00 + i
            for i in range(1, 0x27)  # Von 1 bis 40 für F100Hz bis F4000Hz
        } 
def freqToStr(freq: int):
    for f, v in freq_dict.items():
        if freq == v: return f
    raise AttributeError(f"FreqStr {freq} is not defined")

def microStepStr2STEPTYPE( microStepStr: str ):
    for steptype, v in stepTypeStr.items():
        if v == microStepStr: return steptype
    raise ValueError(f"MicroStepWidth {microStepStr} is not implemented")

ERR_SMS_NOT_PC =        0xE1
ERR_CMDBUFFER_OVFL =    0xE2
ERR_NO_DATA =           0xE3
ERR_MOT_RUN =           0xE4
ERR_DATA_FORMAT =       0xE5
ALARM_EC =              0xE6
ERR_WRONG_CMD =         0xE7
ERR_NO_MOTOR =          0xE8
ERR_REM_MANCTL =        0xE9
ERR_DATA_TRANSFER =     0xEA # "Fehler bei der Datenuebertragung",
ERR_MOT_SHORT_C =       0xEF # "Kurzschluss Motor",
ERR_NO_CONNECTION =     0xF1 # "Verbindung zur Steuerung unterbrochen",
ERR_NO_CLIENT =         0xF2 # "Client konnte nicht gefunden werden",
ERR_NO_SMS =            0xF3 # "keine Steuerung gefunden",
ERR_NR_OF_STEPS =       0xF4 # "Anzahl Schritte falsch",
NO_ERROR =              0xFF # "kein Fehler"
NOERROR =               0x00

errors_dict = {
            ERR_SMS_NOT_PC:         "die Steuerung ist nicht im PC-Modus",
            ERR_CMDBUFFER_OVFL:     "Befehlsspeicher voll",
            ERR_NO_DATA:            "keine Daten vorhanden",
            ERR_MOT_RUN:            "der Motor noch aktiv",
            ERR_DATA_FORMAT:        "falsches Datenformat",
            ALARM_EC:               "Enkontakte ausgeloest",
            ERR_WRONG_CMD:          "falscher Befehl",
            ERR_NO_MOTOR:           "Modul/Motor nicht vorhanden",
            ERR_REM_MANCTL:         "Fernbedienung defekt",
            ERR_DATA_TRANSFER:      "Fehler bei der Datenuebertragung",
            ERR_MOT_SHORT_C:        "Kurzschluss Motor",
            ERR_NO_CONNECTION:      "Verbindung zur Steuerung unterbrochen",
            ERR_NO_CLIENT:          "Client konnte nicht gefunden werden",
            ERR_NO_SMS:             "keine Steuerung gefunden",
            ERR_NR_OF_STEPS:        "Anzahl Schritte ist falsch",
            NO_ERROR:               "kein Fehler"
        }

class axis:
    '''
    Klasse axis, bildet einen Motor der BahrmannSMS ab.
    '''
    def __init__(self):
        self.motor = 0  # Bahrmannscher MotorCode
        #Status
        self.cardispresent = False # True wenn die Karte eingesteckt ist
        self.configured = False    # wird auf True gesetzt, wenn die Axis in SW konfiguriert wurde.
        self.errorcode = 0x00       
        #Config 
        self.microstep_on = 0
        self.steptype = STEPTYPE_1_1 # Schrittweite
        self.softend_on = 0
        self.frequency = freq_dict["F100Hz"]  # Bahrmann Hexcode für Frequenz
        self.ramp = 0
        self.current = 180         # Strom in Steuerung nicht einstellbar(VC1), nur zum Lesen verwenden!
        self.name = ""
        #Logische Konfiguration
        self.physunit = ""
        self.step_in_init = 1.0
        self.offset = 0.0
        # Motorwerte
        self.counterstr = "0"  # Schrittzähler als string
        self.counterfloat = 0.0  # Schrittzähler als float. Das ist hier auch die DialPosition (Zifferblattanzeige)
        self._userposition = self.counterfloat / self.step_in_init + self.offset
        self.endleft = 0
        self.endright = 0
        self.motor_on = 0

    @property
    def position(self):
        return self._userposition
    
    @position.setter
    def position(self, pos : float):
        raise NotImplementedError("Setting of userposition not impelented so far")
        
class FSUBahrmannSMSExc(Exception):
    def __init__(self, msg = "Exception in FSUBahrmannSMS"):
        self.msg = "Exception in FSUBahrmannSMS: " + msg
        super().__init__(self.msg)
    
class FSUBahrmannSMS:
    def __init__(self, ip: str, port: int ) -> None:
        self.socket = socket.socket()
        self.s_timeout = 1.0
        self.socket.settimeout(self.s_timeout)
        self.ip = ip
        self.port= port
        self.axes=[]
        self.serial=""
        self.state = NO_ERROR #Hier wird Controllerfehler, wie z.B. nicht in PC-Modus gespeichert.

        # Motorcodes
        self.motorcodes={ f"MOTOR{i+1}": 0x10+i for i in range(0, 10)}   # MOTOR1 : 0x10, ... , MOTOR16 : 0x20    
        
        # Rampencodes
        self.rampencodes={ f"RAMPE{i}": 0x00+i for i in range(0, 10)}
        
        #try:
        self.connect() 
        self.initMotors()
       # except FSUBahrmannSMSExc as e:
          #  pass            

    def initMotors(self):
        for k, v in self.motorcodes.items():
            a = axis()
            a.motor=v
            a.errorcode = self._getState(a) 
            if a.errorcode == ERR_NO_SMS:
                raise FSUBahrmannSMSExc(errors_dict[a.errorcode])
            elif a.errorcode == ERR_NO_MOTOR:   # Motor ist nicht vorhanden
                a.cardispresent = False
                self.axes.append(a)
                # raise FSUBahrmannSMSExc(errors_dict[a.errorcode])
            elif a.errorcode == 0:
                a.cardispresent = True
                a.errorcode = self.getName(a)
                a.errorcode = self._getFrqRampSteptype(a)
                a.errorcode = self._getCurrent(a)
                self.axes.append(a)
            else: 
                raise FSUBahrmannSMSExc(errors_dict[a.errorcode]) 
            
    
    def checkAxisAvailable(self, axisNr):
        return True if self.axes[axisNr-1] else False #Checken, was passiert, wenn die Motorkarte nicht da ist?
    
    def setAxisConfigured(self, axisNr, bCnfg=True): 
        if self.checkAxisAvailable(axisNr):
            self.axes[axisNr-1].configured = bCnfg
        else:
            raise FSUBahrmannSMSExc(f"Motor{axisNr} is not available")

    def connect(self):
        try:
            self.socket.connect((self.ip, self.port))    
            # Seriennummer abfragen -> Test ob Verbindung ok
            answer = self._send_data(bytes('N', 'utf8'))
            if (len(answer) != 9) or (answer[8] != NO_ERROR):
                raise FSUBahrmannSMSExc(errors_dict[ERR_NO_SMS])
            else:
                self.serial = answer.strip(b'\xff').decode()         
        except socket.timeout:
            raise FSUBahrmannSMSExc("socket timout")
        return self.serial
        
    def disconnect(self):
        self.socket.close()

    def __del__(self):
        self.disconnect()
    
    def _send_data(self, msg):
        fehler = 0
        # Nachricht senden
        self.socket.send(msg)
        try:
            data = self.socket.recv(BUFSIZE)
        # Fehlerauswertung falls Verbindung unterbrochen wird oder Client nicht antwortet
        except socket.timeout:
            self.socket.close()
            return b'\xf1'
        
        found = -1
        while found == -1:
            # Softhandshake auswerten
            for i in handshake_list:
                found = data.find(i)
                if found != -1:
                    if i != b'\xff':
                        fehler = i
                    break
            if found == -1:
                # weiter auf Daten vom Server warten, wenn kein Handshake gefunden
                try:
                    data += self.socket.recv(BUFSIZE)
                # Fehlerauswertung falls Verbindung unterbrochen wird \ kein Handshake gefunden wird
                except socket.timeout:
                    fehler = b'\xf1'
                    self.socket.close()
                    return fehler
        # Daten anzeigen
        if fehler == 0:
            return data
        # Fehler anzeigen
        else:
            return fehler
    
    """Parametersting erstellen und senden"""
    def _sendParameters(self, motor, steps):
        strHex = "%0.5X" % abs(steps)
        stepsHex = "0" + strHex[4] + "0" + strHex[3] + "0" + strHex[2] + "0" + strHex[1] + "0" + strHex[0]
        stepsBytes = bytes.fromhex(stepsHex)
        sendBytes = [motor.motor + 0x10]  # Motordatensteuerwort
        sendBytes.extend(list(stepsBytes))  # Anzahl Schritte
        if steps < 0:
            sendBytes.append(motor.steptype)  # negativer Wert + Schrittart
        else:
            sendBytes.append(motor.steptype + 0x01)  # positiver Wert + Schrittart
        sendBytes.append(motor.ramp)  # Rampe
        sendBytes.append(motor.frequency)  # Frequenz
        return self._send_data(bytes(sendBytes))
        
    """Motornamen abfragen"""
    def getName(self, motor):
        error = 0  # Standardwerte einstellen
        mot = motor.motor
        answer = self._send_data(bytes([mot, GET_NAME]))  # Motorkommandosteuerwort + Kommando
        if len(answer) == 17:
            if answer[16] != 0xff:
                print("Motor error: " + self.errorMessage(0xE5))  # falsches Datenformat
                error = 1
            if error == 0:
                motor.name = answer[0:16].decode()
        else:
            print("Motor error: " + errors_dict[answer[0]])
            error = 1
        return error

    """Motorparameter(RFS) abfragen"""
    def _getFrqRampSteptype(self, motor):
        error = 0  # Standardwerte einstellen
        value = 0
        mot = motor.motor
        answer = self._send_data(bytes([mot, GET_FR_RAMP_STEPTYPE]))  # Motorkommandosteuerwort + Kommando
        if len(answer) == 4:
            if answer[3] != 0xff:
                print("Motor error: " + self.errorMessage(0xE5))  # falsches Datenformat
                error = 1
            if error == 0:
                if answer[0] & 0x80 & answer[1] & 0x80:  # VC-2 Format ->Transportbit  bei Frequenz löschen
                    motor.frequency = answer[2] & 0x7F
                else:  # all others VC
                    motor.frequency = answer[2]
                    motor.ramp = answer[1]
                    motor.steptype = (answer[0] & 0x06)     # nur bis 1/8 Schritt!!! ->1/16, 1/32 erst ab VC-2
                    #                   VC-0/VC-1
        else:
            print("Motor error: " + errors_dict[answer[0]])
            error = 1
        return error


    """Motorstrom abfragen"""
    def _getCurrent(self, motor):
        error = 0  # Standardwerte einstellen
        value = 0
        mot = motor.motor
        answer = self._send_data(bytes([mot, GET_CURRENT]))  # Motorkommandosteuerwort + Kommando
        if len(answer) == 4:
            if answer[3] != 0xff:
                print("Motor error: " + self.errorMessage(0xE5))  # falsches Datenformat
                error = 1
            if error == 0:
                value = answer[0:2].decode()
                motor.current = int(value) * 25
        else:
            print("Motor error: " + errors_dict[answer[0]])
            error = 1
        return error

    def getStateOne(self, axis):
        error = self._getState(self.axes[axis-1])
        return self.axes[axis-1], error
    


    """nur Status-Bytes abfragen"""
    def _getState_short(self, status):
        error = 0  # Standardwerte einstellen
        mot = status.motor
        answer = self._send_data(bytes([mot, GET_STATUS_SHORT]))  # Motorkommandosteuerwort + Kommando
        if len(answer) == 2:
            if answer[1] != 0xff:
                print("Motor error: " + self.errorMessage(0xE5))  # falsches Datenformat
                error = 1
            if error == 0:
                if answer[0] & 0x01:  # Endkontakt rechts
                    status.endright = 1
                if answer[0] & 0x02:  # Endkontakt links
                    status.endleft = 1
                if answer[0] & 0x08:  # Motorstatus -> 1= nicht bereit
                    status.motor_on = 1
                else:
                    status.motor_on = 0
                if answer[0] & 0x10:  # Microschitte aktiviert
                    status.microstep_on = 1
                else:
                    status.microstep_on = 0
                if answer[0] & 0x20:  # Softendkontakte aktiviert
                    status.softend_on = 1
                else:
                    status.softend_on = 0
        else:
            print("Motor error: " + errors_dict[answer[0]])
            error = 1
        return error

    """Zählerstand und Status-Bytes abfragen"""
    def _getState(self, status):
        error = 0  # Standardwerte einstellen
        pos = 0
        mot = status.motor
        answer = self._send_data(bytes([mot, GET_STATUS]))  # Motorkommandosteuerwort + Kommando
        if len(answer) == 10:
            if answer[9] != 0xff:
                print("Motor error: " + self.errorMessage(0xE5))  # falsches Datenformat
                error = 1
            if error == 0:
                pos = answer[0:6].decode()[::-1]    #Zahl von 0-6 + drehen
                status.endright = 1 if answer[7] & 0x01 else 0  # Endkontakt rechts
                status.endleft = 1 if answer[7] & 0x02 else 0  # Endkontakt links  
                pos = '-' + pos if answer[7] & 0x04 else '+' + pos # Vorzeichen
                status.motor_on = 1 if answer[7] & 0x08 else 0  # Motorstatus -> 1= nicht bereit
                status.microstep_on = 1 if answer[7] & 0x10 else 0  # Microschitte aktiviert
                status.softend_on = 1 if answer[7] & 0x20 else 0  # Softendkontakte aktiviert
                micro = answer[8]
                if micro >= 128:  # neue Variante Microschritte(32)
                    micro = (micro - 128) / 32
                else:  # alte Variante Microschritte(8)
                    micro = (micro - 48) / 4
                status.counterstr = pos + str(micro)[1:]  # Vorkommastelle löschen
        else:
            error = answer[0]
        return error

    """
    GetPosition: liefert die Anzahl der Schritte zurück.
    axis: Nummer des Motors 1...N
    """
    def getPosition(self, axisNr):
        return float(self.axes[axisNr-1].counterstr)

    
    def StopOne(self, axisNr):
        self._stopMotor(self.axes[axisNr-1])   

    """Motor anhalten"""
    def _stopMotor(self, motor):
        error = 0
        mot = motor.motor
        answer = self._send_data(bytes([mot, STOP]))
        if answer != b'\xff':
            print("Motor error: " + errors_dict[answer[0]])
            error = 1
        return error

    def StartOne(self, axisNr, position):
        try:
            m = self.axes[axisNr-1]
            print("aktuelle Motorposition: " + m.counterstr + " gewünschte Motorposition: " + str(position))
            steps = int(position - float(m.counterstr))
            self._runMotor(m, steps)
        except IndexError as e:
            raise e(f"IndexError: Motor{axisNr} is not present")


    """Anzahl Schritte fahren"""
    def _runMotor(self, motor, steps):
        if steps > 1048575 or steps < -1048575: # or steps == 0:
            raise FSUBahrmannSMSExc(errors_dict[ERR_NR_OF_STEPS])

        answer = self._sendParameters(motor, steps)
        if answer != b'\xff':
            raise FSUBahrmannSMSExc("Error on Send Parameters: " + errors_dict[answer[0]])
        else:
            answer = self._send_data(bytes([motor.motor, RUN_STEPS]))
            if answer != b'\xff':
                raise FSUBahrmannSMSExc("Error on Send Data: " + errors_dict[answer[0]])

    """zum linken Endkontakt(-) fahren"""
    def gotoEndL(self, motor):
        error = 0
        steps = -1048575  # maximale Anzahl(0xFFFFF) Schritte in negative Richtung
        answer = self.sendParameters(motor, steps)
        if answer != b'\xff':
            print("Motor error: " + errors_dict[answer[0]])
            error = 1
            return error
        else:
            answer = self._send_data(bytes([motor.motor, GO_END_L]))
            if answer != b'\xff':
                print("Motor error: " + errors_dict[answer[0]])
                error = 1
        return error

    """zur Nullposition(Zähler) fahren"""
    def gotoZero(self, motor):
        error = 0
        steps = -1048575  # maximale Anzahl(0xFFFFF) Schritte in negative Richtung
        answer = self.sendParameters(motor, steps)
        if answer != b'\xff':
            print("Motor error: " + errors_dict[answer[0]])
            error = 1
            return error
        else:
            answer = self._send_data(bytes([motor.motor, GO_ZERO]))
            if answer != b'\xff':
                print("Motor error: " + errors_dict[answer[0]])
                error = 1
        return error

    """zum rechten Endkontakt(+) fahren"""
    def gotoEndR(self, motor):
        error = 0
        steps = 1048575  # maximale Anzahl(0xFFFFF) Schritte in positve Richtung
        answer = self.sendParameters(motor, steps)
        if answer != b'\xff':
            print("Motor error: " + errors_dict[answer[0]])
            error = 1
            return error
        else:
            answer = self._send_data(bytes([motor.motor, GO_END_R]))
            if answer != b'\xff':
                print("Motor error: " + errors_dict[answer[0]])
                error = 1
        return error


    """Zählerstand auf Null setzen"""
    def _resetPosition(self, motor):
        error = 0
        mot = motor.motor
        answer = self._send_data(bytes([mot, RESET]))
        if answer != b'\xff':
            print("Motor error: " + errors_dict[answer[0]])
            error = 1
        return error
    
    #----------------------------------------
    # Interface zu Sardana Motor Controller
    #
    def resetPosition(self, axisNr):
        return self._resetPosition(self.axes[axisNr-1])            

    def getStepTypeStr(self, axisNr):
        return stepTypeStr[self.axes[axisNr-1].steptype]
    
    def setStepTypeStr(self, axisNr, stepType: str):
        self.axes[axisNr-1].steptype = microStepStr2STEPTYPE( stepType )

    def setPhysUnit(self, axisNr, physUnit: str):
        self.axes[axisNr-1].physunit = physUnit

    def getPhysUnit(self, axisNr, physUnit: str):
        return self.axes[axisNr-1].physunit
    
    def setFreqFromStr(self, axisNr, freqstr: str):
        self.axes[axisNr-1].frequency = freq_dict[freqstr]

    def getFreqAsStr(self, axisNr, offset):
        return freqToStr(freq_dict[self.axes[axisNr-1].frequency])

    def setOffset(self, axisNr, offset):
        self.axes[axisNr-1].offset = offset

    def getOffset(self, axisNr):
        return self.axes[axisNr-1].offset

    def getPhysUnit(self, axisNr, physUnit: str):
        return self.axes[axisNr-1].physunit       