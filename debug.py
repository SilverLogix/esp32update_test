import utime
import gc
import micropython
import machine
import esp32 # noqa
import os
import network
import ubinascii
from os import statvfs


class Debugging:
    def __init__(self):
        pass

    def pro_and_mem(self, f, *args, **kwargs):
        gc.collect()
        im = gc.mem_free()
        funcname = str(f).split(' ')[1]

        def funcmem(*args, **kwargs):
            t = utime.ticks_us()
            result = f(*args, **kwargs)
            delta = utime.ticks_diff(utime.ticks_us(), t)
            ou = gc.mem_free()
            print(f"Function ({funcname}) took = {delta / 1000:6.3f}ms and used {im - ou} of memory\n")
            return result
        return funcmem

    def profile(self, f, *args, **kwargs):
        myname = str(f).split(' ')[1]

        def new_fun(*args, **kwargs):
            t = utime.ticks_us()
            result = f(*args, **kwargs)
            delta = utime.ticks_diff(utime.ticks_us(), t)
            print(f"Function ({myname}) time = {delta/1000:6.3f}ms\n")
            return result
        return new_fun

    def profile_total(self, f, *args, **kwargs):
        ncalls = 0
        ttime = 0.0

        def new_func(*args, **kwargs):
            nonlocal ncalls, ttime
            t = utime.ticks_us()
            result = f(*args, **kwargs)
            delta = utime.ticks_diff(utime.ticks_us(), t)
            ncalls += 1
            ttime += delta
            print(f"Function: ({f.__name__}) Call count = {ncalls} | Total time = {ttime/1000:6.3f}ms\n")
            return result

        return new_func

    def used_mem(self, f, *args, **kwargs):
        gc.collect()
        im = gc.mem_free()
        name = str(f).split(' ')[1]

        def new_mem(*args, **kwargs):
            result = f(*args, **kwargs)
            ou = gc.mem_free()
            to = (im - ou)
            print(f"Function ({name}) used memory = {to}\n")
            return result
        return new_mem

    def serial_mem(self, mp: bool):
        if mp:
            micropython.mem_info(True)
        else:
            micropython.mem_info()

    def files(self):
        dirr = str(os.listdir())
        print(f"Files: {dirr}")

    def space_free(self):  # Display remaining free space
        bits = statvfs('/flash')
        # print(str(bits))
        blksize = bits[0]  # 4096
        blkfree = bits[3]  # 12
        freesize = blksize * blkfree  # 49152
        mbcalc = 1024 * 1024  # 1048576
        mbfree = freesize / mbcalc  # 0.046875
        print(f"Flash: {mbfree}MB")

    def m_freq(self):
        gfr = str(machine.freq())
        print(f"Mhz: {gfr}")

    def raw_temp(self):
        raw = str(esp32.raw_temperature())
        print(f"CPU Temp: {raw}F")

    def show_voltage(self):
        adc = machine.ADC(machine.Pin(32))
        vref = int(1100)
        utime.sleep_ms(100)
        v = adc.read()
        utime.sleep_ms(100)
        battery_voltage = (float(v) / 4095.0) * 2.0 * 3.3 * (vref / 1000.0)
        print(f"Voltage: {battery_voltage:0.2f}v")

    def get_mac(self):
        mac = ubinascii.hexlify(network.WLAN(1).config('mac'), ':').decode()
        print(f"MAC: {mac}")

    def parts(self):
        getpart = esp32.Partition.info(0)
        print(f"MAC: {getpart}")

    def b_print(self):
        print("\n------------------------")
        self.get_mac()
        self.space_free()
        self.m_freq()
        self.raw_temp()
        self.show_voltage()
        print("\n")
        self.files()
        print("\n")
        print("-------------------------\n")

        gc.collect()

# Example usage:
# deb = Debugging()
# deb.b_print()
