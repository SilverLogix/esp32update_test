import oled
from time import sleep_ms
import vga16
import network
import ugit

oled.fill(oled.BLACK)
oled.set_backlight_intensity(1023)
oled.micrologo()
sleep_ms(2000)
oled.fill(oled.BLACK)
oled.set_backlight_intensity(64)



oled.circle(32, 32, 32, oled.RED)
oled.set_backlight_intensity(1023)
oled.fill(oled.BLACK)
oled.fillroundrect(16, 16, 90, 90, 16, oled.BLUE)
oled.fillroundrect(128, 16, 90, 90, 16, oled.YELLOW)
oled.tft.text(vga16, " MICROPYTHON ", int(oled.tft.width() / 2 - 105), int(oled.tft.height() - 18), oled.WHITE, 0)
