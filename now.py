import espnow  # noqa
import _thread
import network
import ubinascii
from time import sleep_ms

e = espnow.ESPNow()  # Enable ESP-NOW
e.active(True)
is_rx_thread_running = False


def auth():
    # A WLAN interface must be active to send()/recv()
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.disconnect()                # Disconnect from last connected WiFi SSID


def get_mac():
    mac = ubinascii.hexlify(network.WLAN(1).config('mac'), ':').decode()
    print(f"MAC: {mac}")
    wlan_mac = network.WLAN(1).config('mac')
    print(ubinascii.hexlify(wlan_mac).decode())


def tx(mac, data):
    global e
    e.add_peer(mac)  # Add the receiver's MAC address
    e.send(mac, data, True)  # Send data to the receiver
    print(f"Sent data to : {mac}")
    sleep_ms(1000)


def rx():
    global is_rx_thread_running, e

    while is_rx_thread_running:
        # Add MAIN peers mac
        peer = b'\x84\xcc\xa8\x61\x0a\x21'  # MAC address of peer's wifi interface
        e.add_peer(peer)  # Sender's MAC registration

        while True:
            host, msg = e.recv()
            if msg:  # wait for message
                if msg == b'test':  # decode message and translate
                    print("OMG Got message!\n")
                elif msg == b'back':
                    pass
                elif msg == b'stop':
                    pass


def start_rx_thread():
    global is_rx_thread_running

    if not is_rx_thread_running:
        is_rx_thread_running = True
        _thread.stack_size(128)
        _thread.start_new_thread(rx, ())
        print("NOW Stack:", _thread.stack_size())
        print("Rx thread started.")
    else:
        print("Rx thread is already running.")


def stop_rx_thread():
    global is_rx_thread_running
    if is_rx_thread_running:
        is_rx_thread_running = False
        print("Rx thread stopped.")
    else:
        print("Rx thread is not running.")


# Usage:
# Start the thread
# start_rx_thread()

# Send data via ESP-NOW
# mac_address = b'\xe8\x68\xe7\x4e\xbb\x19'  # MAC address of the receiver
# data = b'walk'  # Data to be sent
# tx(mac_address, data)

# Stop the thread
# stop_rx_thread()
