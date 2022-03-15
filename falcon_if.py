#!/usr/bin/env python
from enum import IntEnum
from threading import Thread
import time
import spidev

class LEDIdleMode(IntEnum):
    SOLID    = 0
    FLASHING = 1

class AlertZone(IntEnum):
    NONE  = 0
    FRONT = 1
    REAR  = 2
    LHS   = 3
    RHS   = 4

class BatterySOC(IntEnum):
    ERROR  = 0
    LOW    = 1
    MEDIUM = 2
    HIGH   = 3

class FalconInterface:

    # Tx Data

    ledIdleMode_front = LEDIdleMode.SOLID
    ledIdleMode_rear  = LEDIdleMode.SOLID
    ledIdleMode_side  = LEDIdleMode.SOLID

    alertZone = AlertZone.NONE

    # Rx Data

    batterySOC = BatterySOC.ERROR
    status_charging = False
    status_error    = False

    # Thread flags

    commsThreadRunning = False
    txDataNew = False

    def __init__(self):
        self.ledIdleVal_front       = 0
        self.ledIdleVal_rearAndSide = 0

    def _commsThread(self):
        self.commsThreadRunning = True

        self.spi = spidev.SpiDev()
        self.spi.open(0,0)

        while self.commsThreadRunning:
            startTime = time.time()
            while((time.time() < (startTime + 10.0)) and self.txDataNew == False):
                pass

            ledIdleModeByte = self.ledIdleMode_front | (self.ledIdleMode_rear << 2) | (self.ledIdleMode_side << 4)
            txData = [self.ledIdleVal_front, self.ledIdleVal_rearAndSide, ledIdleModeByte, self.alertZone.val, 0, 0]

            print("\nSent data: ")
            print(txData)

            rxData = self.spi.xfer2(txData, 100000)

            print("\nRecieved data: ")
            print(rxData)

            self.txDataNew = False

        self.spi.close()

    def startComms(self):
        Thread(target=self._commsThread).start()

    def stopComms(self):
        self.commsThreadRunning = False

    def setLEDIdleVal(self, front, rearAndSide):
        self.ledIdleVal_front       = front
        self.ledIdleVal_rearAndSide = rearAndSide
        self.txDataNew = True

    def setLEDIdleMode(self, front, rear, side):
        self.ledIdleMode_front = front
        self.ledIdleMode_rear  = rear
        self.ledIdleMode_side  = side
        self.txDataNew = True

    def setAlertZone(self, zone):
        self.alertZone = zone
        self.txDataNew = True

    def getBatterySOC(self):
        pass

    def getCharging(self):
        pass

    def getError(self):
        pass
