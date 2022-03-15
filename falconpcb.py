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

class Interface:

    def __init__(self):

        # Tx Data

        self.ledIdleVal_front       = 0
        self.ledIdleVal_rearAndSide = 0

        self.ledIdleMode_front = LEDIdleMode.SOLID
        self.ledIdleMode_rear  = LEDIdleMode.SOLID
        self.ledIdleMode_side  = LEDIdleMode.SOLID

        self.alertZone = AlertZone.NONE

        # Rx Data

        self.batterySOC = BatterySOC.ERROR
        self.status_charging = False
        self.status_error    = False

        # Thread flags

        self.commsThreadRunning = False
        self.txDataNew = False

    def _commsThread(self):
        self.commsThreadRunning = True

        self.spi = spidev.SpiDev()
        self.spi.open(0,0)

        while self.commsThreadRunning:
            startTime = time.time()
            while((time.time() < (startTime + 1.0)) and self.txDataNew == False):
                pass

            ledIdleModeByte = self.ledIdleMode_front | (self.ledIdleMode_rear << 2) | (self.ledIdleMode_side << 4)
            txData = [self.ledIdleVal_front, self.ledIdleVal_rearAndSide, ledIdleModeByte, self.alertZone.value, 0, 0]

            if self.txDataNew:
                print("\nSent data:")
                print(txData)

            rxData = self.spi.xfer2(txData, 100000)

            if self.txDataNew:
                print("\nRecieved data:")
                print(rxData)
                print("")

            self.txDataNew = False

        self.spi.close()

    def startComms(self):
        Thread(target=self._commsThread).start()

    def stopComms(self):
        self.ledIdleVal_front       = 0
        self.ledIdleVal_rearAndSide = 0
        self.ledIdleMode_front      = LEDIdleMode.SOLID
        self.ledIdleMode_rear       = LEDIdleMode.SOLID
        self.ledIdleMode_side       = LEDIdleMode.SOLID
        self.alertZone              = AlertZone.NONE

        self.txDataNew = True
        time.sleep(0.5)

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

        time.sleep(0.2)

        self.alertZone = AlertZone.NONE
        self.txDataNew = True

    def getBatterySOC(self):
        pass

    def getCharging(self):
        pass

    def getError(self):
        pass
