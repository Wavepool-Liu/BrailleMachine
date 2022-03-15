#-- coding:utf8 --
import togpio.gpioset
import RPi.GPIO as GPIO
import os
import time


if __name__ == "__main__":
    # IO口测试
    IO = togpio.gpioset.BGpio()
    IO.Gpio_Init()
    Index =  1
    Mod = 1
    fval = 0
    while True:
        val = GPIO.input(IO.B6)
        try:
            if fval == 0 and val == 1:
                os.system("sudo reboot")
            elif fval == 1 and val == 0:
                os.system("sudo pkill -f main.py")
            else:
                pass
            time.sleep(2)

            # var = IO.ioflash()
            # # print(var)
            # if IO.Bottom_state_Add_Index(var["B1"],var["B2"],Index) is True:
            #     Index = IO.Index
            #     print(Index)
            # if IO.Bottom_state_First(var["B1"]) is True:
            #     print("heihei")
            # elif IO.Bottom_state_Add_Mods(var["B4"],Mod) is True:
            #     Mod = IO.Mods
            #     print(Mod)
            # else:
            #     pass
        except KeyboardInterrupt:
            GPIO.cleanup()