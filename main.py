import time
import subprocess
import gc

import smbus
import pigpio

subprocess.call(["sudo pigpiod"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

gpio = pigpio.pi()


class BH1750:
    LOW_ADDR = 0b0100011
    HIGH_ADDR = 0b1011100

    def __init__(self, addr_pin: int,  addr: bool):
        self.addr_pin = addr_pin
        gpio.set_mode(self.addr_pin, pigpio.OUTPUT)
        gpio.write(addr_pin, addr)
        self._address = addr
        self.i2c_handle = gpio.i2c_open(1, self.address, 0)
        self.continuous_h_mode()
    
    def __del__(self):
        try:
            if self.i2c_handle:
                gpio.i2c_close(self.i2c_handle)
        except:
            pass

    @property
    def address(self):
        return self.HIGH_ADDR if self._address else self.LOW_ADDR

    @address.setter
    def address_set(self, addr: bool):
        gpio.write(self.addr_pin, addr)
        self._address = addr
        gpio.i2c_close(self.i2c_handle)
        self.i2c_handle = gpio.i2c_open(1, self.address, 0)

    def _send_command(self, data):
        gpio.i2c_write_byte(self.i2c_handle, data)

    def _read_data(self, count):
        if count == 1:
            return gpio.i2c_read_byte(self.i2c_handle)
        else:
            return gpio.i2c_read_device(self.i2c_handle, count)

    def power_off(self):
        self._send_command(0b00000000)

    def power_on(self):
        self._send_command(0b00000001)

    def reset(self):
        self.power_on()
        self._send_command(0b00000111)

    def continuous_h_mode(self):
        self._send_command(0b00010000)

    def continuous_h_mode2(self):
        self._send_command(0b00010001)

    def continuous_l_mode(self):
        self._send_command(0b00010011)

    def one_time_h_mode(self):
        self._send_command(0b00100000)

    def one_time_h_mode2(self):
        self._send_command(0b00100001)

    def one_time_l_mode(self):
        self._send_command(0b00100011)

    def convert_to_number(self, count, data):
        brightness = 0
        for i in data:
            brightness += i
            brightness <<= 8
        return (brightness >> 8) / 1.2

    def get_brightness(self):
        time.sleep(0.140)
        return self.convert_to_number(*self._read_data(2))


def main():
    brightness_sensor = BH1750(17, False)

    while True:
        brightness = brightness_sensor.get_brightness()
        
        if brightness <= 10:
            print("too dark")
        elif brightness <= 25:
            print("dark")
        elif brightness <= 45:
            print("medium")
        elif brightness <= 60:
            print("bright")
        else:
            print("too bright")

        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except:
        gc.collect()
        gpio.stop()

