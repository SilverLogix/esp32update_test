import _thread
import board
import gc
import ubinascii
import espnow
import uWeb
import uFtp

print("Load main.py\n")

gc.enable()

board.Wkill(False)
board.AP('ttgo', 'password')


def start_web_server():
    server = uWeb.WebServer()
    server.start()


def start_ftp_server():
    serverftp = uFtp.FTPServer()
    serverftp.start()


_thread.start_new_thread(start_web_server, ())
_thread.start_new_thread(start_ftp_server, ())

e = espnow.ESPNow()
e.active(True)
print("espnow")

while True:
    for mac, msg in e:
        mmm = ubinascii.hexlify(mac, ':').decode()
        print(mmm, msg)
        if msg == b"test":
            print("DO THINGS\n")
        if mac is None:  # mac, msg will equal (None, None) on timeout
            break

    _thread.poll()
