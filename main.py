import espnow  # noqa
import board
import gc
import ubinascii
import uWeb

print("Load main.py\n")

gc.enable()

board.Wkill(False)
board.AP('ttgo', 'password')

server = uWeb.WebServer()
server.start()

e = espnow.ESPNow()
e.active(True)

for mac, msg in e:
    mmm = ubinascii.hexlify(mac, ':').decode()
    print(mmm, msg)
    if msg == b"test":
        print("DO THINGS\n")
    if mac is None:   # mac, msg will equal (None, None) on timeout
        break

