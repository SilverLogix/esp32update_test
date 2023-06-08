import micropython
import machine
import oled
import gc
#import ftptiny
#import webtiny

# noinspection PyArgumentList
machine.freq(240000000)
micropython.alloc_emergency_exception_buf(100)


#ftp = ftptiny.FtpTiny()  # create one
#ftp.start()  # start an ftp thread

#web = webtiny.WebServer()
#web.start()

print(str('Booting...'))
oled.boot()
gc.collect()

