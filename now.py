# ESP-NOW tests


import espnow  # noqa
import time


e = espnow.ESPNow()     # Enable ESP-NOW
e.active(True)

peer1 = b'\xe8\x68\xe7\x4e\xbb\x19'   # MAC address of peer1's wifi interface
e.add_peer(peer1)                     # add peer1 (receiver1)

peer2 = b'\x60\x01\x94\x5a\x9c\xf0'   # MAC address of peer2's wifi interface

print("Starting...")            # Send to all peers

e.send(peer1, "walk", True)     # send commands to pear 1
e.send(peer2, "walk", True)     # send commands to pear 2
time.sleep_ms(2000)
e.send(peer1, "walk", True)
e.send(peer2, "back", True)
time.sleep_ms(2000)
