import micropython
# ----------- Connect to a router ----------- #
global IP


@micropython.native
def STA(ssid: str, passw: str):
    import network

    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(ssid, passw)

    while not sta.isconnected():
        pass

    print('Connection successful')
    print(sta.ifconfig())
    return sta


# ---------- Connect to a router with a static IP ---------- #
@micropython.native
def SSSTA(ssid: str, passw: str, static: str, routerip: str):
    import network

    sssta = network.WLAN(network.STA_IF)
    sssta.ifconfig((static, "255.255.255.0", routerip, routerip))
    sssta.active(True)
    sssta.connect(ssid, passw)

    while not sssta.isconnected():
        pass

    print('Connection successful')
    print(str(sssta.ifconfig()))
    return sssta


# --------- Create a Hotspot ---------- #
@micropython.native
def AP(ssid: str, pswd: str):
    import network

    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password=pswd, authmode=network.AUTH_WPA_WPA2_PSK, txpower=3)

    print('AP Active \n')

    varif = ap.ifconfig()
    print(varif[0])

    global IP
    IP = str(varif[0])
    return ap


def Wkill(cmd: bool):
    import network

    network.WLAN(0).active(cmd)
    network.WLAN(1).active(cmd)
