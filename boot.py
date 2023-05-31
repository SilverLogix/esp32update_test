import micropython
import machine
# noinspection PyUnresolvedReferences
from machine import Pin
import ftptiny

# noinspection PyArgumentList
machine.freq(240000000)
micropython.alloc_emergency_exception_buf(100)

print(str('Booting...'))

import network

ap = network.WLAN(network.AP_IF)
ap.config(essid="esp32")
ap.active(True)

print('Connection successful')
print(ap.ifconfig())

ftp = ftptiny.FtpTiny()  # create one
ftp.start()  # start an ftp thread

