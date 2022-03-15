#!/usr/bin/env python
#coding=utf-8
import serial
from serial.tools import list_ports
import re
import time
import binascii
from tobraille.toBraille import *
# 往串口屏组件发送数据
def StrToScreen(id, contant):
    id_hex = binascii.hexlify((id + ".txt" + "=\"").encode('gb2312')).decode('gb2312')
    contant_hex = binascii.hexlify((contant + "\"").encode('gb2312')).decode('gb2312')
    return bytes.fromhex(id_hex + contant_hex + "ff ff ff")

def NumsMatchHex(MachID,String1,HexEnd):
    HexStr =MachID
    for i in range(1,7):
        if String1.find(str(i)) != -1:
            HexStr = HexStr + "01"
        else:
            HexStr = HexStr + "00"
    HexStr = HexStr + HexEnd
    return HexStr

def SendCharTo32(serttl,Data):
    braille_str = toBraille(Data[0])[1] # 取开头第一句话做识别
    print(braille_str)
    delay = 6
    if braille_str.count("-") == 2:
        F1Points,F2Points,F3Points = braille_str.split("-",2)
        serttl.write(bytes.fromhex(NumsMatchHex("f1",F1Points,"ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f2", F2Points, "ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f3", F3Points, "ee")))
    elif braille_str.count("-") == 1:
        F1Points,F2Points = braille_str.split("-",1)
        F3Points = "0"
        serttl.write(bytes.fromhex(NumsMatchHex("f1", F1Points, "ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f2", F2Points, "ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f3", F3Points, "ee")))
    elif braille_str.count("-") == 0:
        F1Points = braille_str.split("-",1)
        F2Points = "0"
        F3Points = "0"
        serttl.write(bytes.fromhex(NumsMatchHex("f1", F1Points, "ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f2", F2Points, "ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f3", F3Points, "ee")))
    else:
        pass

class get_serial:
    @staticmethod
    def get_usb_port(BRate):  #获取串口
        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) == 0:
            print('no port')
            return None
        else:
            for i in range(0, len(port_list)):
                pattern = re.compile(r'\d+')        #正则表达式
                r = pattern.match(str(port_list[0]), 11, 13)
                usb = r.group(0)
                usb_port = '/dev/ttyUSB' + usb
                try:
                    ser = serial.Serial(usb_port, BRate, timeout=0.5)
                    ser.close()
                    ser.open()
                    ser.flushInput()
                    return ser
                except:
                    return None

    @staticmethod
    def get_ttl_port(BRate):  # 获取串口
        ttl_port = '/dev/ttyAMA0'
        try:
            ser = serial.Serial(ttl_port, BRate, timeout=0.5)
            ser.close()
            ser.open()
            ser.flushInput()
            return ser
        except:
            return None

def SetMachRise_Down(serttl,MacId,delaytime):
    serttl.write(bytes.fromhex(MacId+" 11 01 ee"))
    time.sleep(delaytime)
    serttl.write(bytes.fromhex(MacId+" 11 02 ee"))
    time.sleep(delaytime)
    serttl.write(bytes.fromhex(MacId+" 11 03 ee"))
    time.sleep(delaytime)
    serttl.write(bytes.fromhex(MacId+" 11 04 ee"))
    time.sleep(delaytime)
    serttl.write(bytes.fromhex(MacId+" 11 05 ee"))
    time.sleep(delaytime)
    serttl.write(bytes.fromhex(MacId+" 11 06 ee"))
    time.sleep(delaytime)
    serttl.write(bytes.fromhex(MacId+" 22 01 ee"))
    time.sleep(delaytime)
    serttl.write(bytes.fromhex(MacId+" 22 02 ee"))
    time.sleep(delaytime)
    serttl.write(bytes.fromhex(MacId+" 22 03 ee"))
    time.sleep(delaytime)
    serttl.write(bytes.fromhex(MacId+" 22 04 ee"))
    time.sleep(delaytime)
    serttl.write(bytes.fromhex(MacId+" 22 05 ee"))
    time.sleep(delaytime)
    serttl.write(bytes.fromhex(MacId+" 22 06 ee"))

def SetMachRise(serttl,Machid,IO,delaytime):
    serttl.write(bytes.fromhex(Machid + " 11 "+IO+" ee"))
    time.sleep(delaytime)

def SetMachDown(serttl,Machid,IO,delaytime):
    serttl.write(bytes.fromhex(Machid + " 22 "+IO+" ee"))
    time.sleep(delaytime)

# def SetRiseIO(serttl,MachId,IO,delaytime):


if __name__ == "__main__":
    serusb = get_serial.get_usb_port(9600)
    serttl = get_serial.get_ttl_port(115200)
    serttl.write(bytes.fromhex("f1  00 00 00 00 00 00 ee"))
    time.sleep(5)
    serttl.write(bytes.fromhex("f2  00 00 00 00 00 00 ee"))
    # serttl.write(bytes.fromhex("f1  00 00 01 01 00 01 ee"))
    # time.sleep(5)
    # serttl.write(bytes.fromhex("f2  00 00 01 00 00 00 ee"))
    # serttl.write(bytes.fromhex("f2 11 02 ee"))
    # time.sleep(3)
    # serttl.write(bytes.fromhex("f2 11 02 ee"))
    # time.sleep(3)
    # # time.sleep(3)
    # serttl.write(bytes.fromhex("f3 11 03 ee"))
    # time.sleep(3)
    # serttl.write(bytes.fromhex("f3 11 04 ee"))
    # time.sleep(3)
    # serttl.write(bytes.fromhex("f3 11 06 ee"))
    # time.sleep(3)
    # serttl.write(bytes.fromhex("f2 11 03 ee"))
    # time.sleep(3)

    # serttl.write(bytes.fromhex("f2 11 05 ee"))
    # time.sleep(3)
    # serttl.write(bytes.fromhex("f2 11 06 ee"))
    # time.sleep(3)

    # serttl.write(bytes.fromhex("f3 22 02 ee"))
    # time.sleep(3)
    # serttl.write(bytes.fromhex("f3 22 04 ee"))
    # time.sleep(3)
    # serttl.write(bytes.fromhex("f3 22 05 ee"))
    # time.sleep(3)
    # serttl.write(bytes.fromhex("f2 22 02 ee"))
    # time.sleep(3)
    # serttl.write(bytes.fromhex("f2 22 05 ee"))
    # time.sleep(3)
    # serttl.write(bytes.fromhex("f2 22 06 ee"))
    # time.sleep(3)