from micropython import const
import st7789
import vga8 as font
import machine

SCK = const(0x12)
MOS = const(0x13)
RST = const(0x17)
SCS = const(0x05)
SDC = const(0x10)
BCK = const(0x04)

pwm = machine.PWM(const(machine.Pin(BCK)))  # Create PWM object for backlight control

BLACK = const(0x0000)
BLUE = const(0x001F)
RED = const(0xF800)
GREEN = const(0x07E0)
CYAN = const(0x07FF)
MAGENTA = const(0xF81F)
YELLOW = const(0xFFE0)
WHITE = const(0xFFFF)

# Initialize the display and configure backlight pin
spi = machine.SPI(1, baudrate=30000000, sck=machine.Pin(SCK), mosi=machine.Pin(MOS))
tft = st7789.ST7789(
    spi,
    135,
    240,
    reset=machine.Pin(RST, machine.Pin.OUT),
    cs=machine.Pin(SCS, machine.Pin.OUT),
    dc=machine.Pin(SDC, machine.Pin.OUT),
    rotation=3)
tft.init()


def set_backlight_intensity(intensity: int):
    # Set the duty cycle of the PWM signal
    pwm.duty(intensity)  # noqa


def fast_hline(x: int, y: int, width: int, color):
    tft.fill_rect(x, y, width, 1, color)


def fast_vline(x, y, height, color):
    tft.fill_rect(x, y, 1, height, color)


def circle(x0, y0, radius, *args, **kwargs):
    """Circle drawing function.  Will draw a single pixel wide circle with
    center at x0, y0 and the specified radius."""
    f = 1 - radius
    ddf_x = 1
    ddf_y = -2 * radius
    x = 0
    y = radius
    tft.pixel(x0, y0 + radius, *args, **kwargs)  # bottom
    tft.pixel(x0, y0 - radius, *args, **kwargs)  # top
    tft.pixel(x0 + radius, y0, *args, **kwargs)  # right
    tft.pixel(x0 - radius, y0, *args, **kwargs)  # left
    while x < y:
        if f >= 0:
            y -= 1
            ddf_y += 2
            f += ddf_y
        x += 1
        ddf_x += 2
        f += ddf_x
        # angle notations are based on the unit circle and in diection of being drawn
        tft.pixel(x0 + x, y0 + y, *args, **kwargs)  # 270 to 315
        tft.pixel(x0 - x, y0 + y, *args, **kwargs)  # 270 to 255
        tft.pixel(x0 + x, y0 - y, *args, **kwargs)  # 90 to 45
        tft.pixel(x0 - x, y0 - y, *args, **kwargs)  # 90 to 135
        tft.pixel(x0 + y, y0 + x, *args, **kwargs)  # 0 to 315
        tft.pixel(x0 - y, y0 + x, *args, **kwargs)  # 180 to 225
        tft.pixel(x0 + y, y0 - x, *args, **kwargs)  # 0 to 45
        tft.pixel(x0 - y, y0 - x, *args, **kwargs)  # 180 to 135


def fillcircle(x0, y0, r, color):
    fast_vline(x0, y0 - r, 2 * r + 1, color)
    fillCircleHelper(x0, y0, r, 3, 0, color)


def fillCircleHelper(x0, y0, r, corners, delta, color):
    f = 1 - r
    ddF_x = 1
    ddF_y = -2 * r
    x = 0
    y = r
    px = x
    py = y

    delta += 1  # Avoid some +1's in the loop

    while x < y:
        if f >= 0:
            y -= 1
            ddF_y += 2
            f += ddF_y
        x += 1
        ddF_x += 2
        f += ddF_x

        if x < (y + 1):
            if corners & 1:
                fast_vline(x0 + x, y0 - y, 2 * y + delta, color)
            if corners & 2:
                fast_vline(x0 - x, y0 - y, 2 * y + delta, color)

        if y != py:
            if corners & 1:
                fast_vline(x0 + py, y0 - px, 2 * px + delta, color)
            if corners & 2:
                fast_vline(x0 - py, y0 - px, 2 * px + delta, color)
            py = y
        px = x


def fillRect(x, y, w, h, color):
    for i in range(x, x + w):
        fast_vline(i, y, h, color)


def drawcirclehelper(x0, y0, r, cornername, color):
    f = 1 - r
    ddf_x = 1
    ddf_y = -2 * r
    x = 0
    y = r

    while x < y:
        if f >= 0:
            y -= 1
            ddf_y += 2
            f += ddf_y
        x += 1
        ddf_x += 2
        f += ddf_x

        if cornername & 0x4:
            tft.pixel(x0 + x, y0 + y, color)
            tft.pixel(x0 + y, y0 + x, color)
        if cornername & 0x2:
            tft.pixel(x0 + x, y0 - y, color)
            tft.pixel(x0 + y, y0 - x, color)
        if cornername & 0x8:
            tft.pixel(x0 - y, y0 + x, color)
            tft.pixel(x0 - x, y0 + y, color)
        if cornername & 0x1:
            tft.pixel(x0 - y, y0 - x, color)
            tft.pixel(x0 - x, y0 - y, color)


def roundrect(x, y, w, h, r, color):
    max_radius = min(w, h) // 2  # 1/2 minor axis
    if r > max_radius:
        r = max_radius

    fast_hline(x + r, y, w - 2 * r, color)  # Top
    fast_hline(x + r, y + h - 1, w - 2 * r, color)  # Bottom
    fast_vline(x, y + r, h - 2 * r, color)  # Left
    fast_vline(x + w - 1, y + r, h - 2 * r, color)  # Right

    drawcirclehelper(x + r, y + r, r, 1, color)
    drawcirclehelper(x + w - r - 1, y + r, r, 2, color)
    drawcirclehelper(x + w - r - 1, y + h - r - 1, r, 4, color)
    drawcirclehelper(x + r, y + h - r - 1, r, 8, color)


def fillroundrect(x, y, w, h, r, color):
    max_radius = min(w, h) // 2  # 1/2 minor axis
    if r > max_radius:
        r = max_radius

    fillRect(x + r, y, w - 2 * r, h, color)

    fillCircleHelper(x + w - r - 1, y + r, r, 1, h - 2 * r - 1, color)
    fillCircleHelper(x + r, y + r, r, 2, h - 2 * r - 1, color)


def fill(col):
    tft.fill(col)


def text(string: str, x: int, y: int, fg=WHITE, bg=BLACK):
    tft.text(font, string, x, y, fg, bg)


def pixel(x, y, col):
    tft.pixel(x, y, col)


def scroll(dx, dy):
    tft.scroll(dx, dy)


def text_long(otitle, oline1, oline2, oline3, oline4, oline5, oline6, oline7, fg=WHITE, bg=BLACK):
    tft.text(font, otitle, 0, 0, YELLOW, bg)

    tft.text(font, oline1, 0, 18, fg, bg)
    tft.text(font, oline2, 0, 34, fg, bg)
    tft.text(font, oline3, 0, 50, fg, bg)
    tft.text(font, oline4, 0, 66, fg, bg)
    tft.text(font, oline5, 0, 82, fg, bg)
    tft.text(font, oline6, 0, 98, fg, bg)
    tft.text(font, oline7, 0, 114, fg, bg)


# -------------- Screen Splashes ---------------#
def boot(col=BLACK):
    tft.fill(col)
    tft.text(font, "Boot", 0, tft.height() - 16, WHITE, 0)  # Boot text on screen


def gwifi(col=BLACK):
    tft.fill(col)
    tft.text(font, "WIFI", 0, tft.height() - 16, WHITE, 0)


def g_update(col=BLACK):
    tft.fill(col)
    tft.text(font, "UPDATE", 0, tft.height() - 16, WHITE, 0)


def micrologo(col=BLACK):
    tft.fill(col)
    tft.jpg('m_logo.jpg', 0, -8, 1)
    tft.text(font, " MICROPYTHON ", int(tft.width() / 2 - 50), int(tft.height() - 18), WHITE, 0)
