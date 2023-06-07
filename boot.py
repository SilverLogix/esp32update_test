import micropython
import machine
import ugit
import board
import ftptiny

# noinspection PyArgumentList
machine.freq(240000000)
micropython.alloc_emergency_exception_buf(100)

print(str('Booting...'))

try:
    board.STA('iPhone', 'macos111')
except OSError as error:
    print(error)

ugit.pull_all()


#ap = network.WLAN(network.AP_IF)
#ap.config(essid="esp32")
#ap.active(True)

#print('Connection successful')
#print(ap.ifconfig())

#ftp = ftptiny.FtpTiny()  # create one
#ftp.start()  # start an ftp thread

