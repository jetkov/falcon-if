#!/usr/bin/env python

import time
import sys
import spidev

spi = spidev.SpiDev()
spi.open(0,0)

def buildReadCommand(channel):
    startBit = 0x01
    singleEnded = 0x08

    return [startBit, (singleEnded|channel)<<4, 0]

def readAdc(channel):
    if ((channel > 7) or (channel < 0)):
        return -1
    r = spi.xfer2(buildReadCommand(channel))
    return processAdcValue(r)

if __name__ == '__main__':
    try:
        while True:
            txData = [25, 75, 0b00100111, 4, 0, 0]
            spi.xfer2(txData, 100000)
            print("Sent #1")
            time.sleep(1)
            txData = [42, 69, 0b00011101, 2, 0, 0]
            spi.xfer2(txData, 100000)
            print("Sent #2")
            time.sleep(1)

    except KeyboardInterrupt:
        spi.close()
        sys.exit(0)
