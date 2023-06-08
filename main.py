import oled
import time
import random
import board
import vga8
import globals as g
from sys import modules

if __name__ == "__main__":
    oled.fill(oled.BLACK)
    oled.set_backlight_intensity(1023)
    oled.micrologo()
    time.sleep_ms(2000)
    oled.fill(oled.BLACK)
    oled.set_backlight_intensity(64)

    oled.gwifi()
    board.STA('NETGEAR90', 'curlyearth685')
    time.sleep_ms(1000)
    gn = board.get_npt()
    g.ntp = gn
    print(g.ntp)

    board.Wkill(True)

    board.AP('ttgo', 'password')

    rand = [oled.RED, oled.GREEN, oled.YELLOW, oled.MAGENTA]
    oled.circle(32, 32, 32, oled.RED)
    oled.set_backlight_intensity(1023)
    oled.fill(oled.BLACK)
    oled.fillroundrect(16, 16, 90, 90, 16, oled.BLUE)
    oled.fillroundrect(128, 16, 90, 90, 16, random.choice(rand))
    oled.tft.text(vga8, f"{g.ntp[1]}/{g.ntp[2]}/{g.ntp[0]}", 86, 114, oled.WHITE, 0)

    print("\n", modules.keys(), "\n")


