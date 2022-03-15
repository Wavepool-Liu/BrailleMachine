#!/usr/bin/env python
#coding=utf-8
import serial
from serial.tools import list_ports
import re
import time
import binascii
from tobraille.toBraille import *
import RPi.GPIO as GPIO
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import json
import time,datetime
import threading
import os



# MQTT: 当收到关于客户订阅的主题的消息时调用。
def on_message(client, userdata, msg):
    data = str(msg.payload, encoding='utf-8')
    if data == "lwp already dissconnected":
        print(data)
    else:
        data = json.loads(data)
        if data['mach_id'] == 1:
            tran = data['tran']
            word = json.loads(data['word'])[tran]
            print("汉字：" + tran)
            print("盲文：" + word)
            APPSendTo32(serttl, word)
        else:
            tran = data['tran']
            word = data['word']
            print("汉字：" + tran)
            print("盲文：" + word)


# MQTT: 当代理响应连接请求时调用。
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("mne", qos=0) # 订阅主题


# MQTT: 当与代理断开连接时调用
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")


# MQTT: 初始化客户端函数
def client_main():
    HOST = "47.107.148.165"  # 设置Ip
    PORT = 1883  # 设置端口号
    client_id = "lwp"
    client = mqtt.Client(client_id)
    client.on_connect = on_connect  # 启动订阅模式
    client.on_disconnect = on_disconnect  # 启动订阅模式
    client.on_message = on_message  # 接收消息
    # 设置要发送给代理的遗嘱。 如果客户端断开而没有调用disconnect（），代理将代表它发布消息。
    # client.will_set(topic="mne", payload="lwpwp already dissconnected", qos=0, retain=True)
    client.connect(HOST, PORT, 5)  # 链接
    client.loop_start()  # 若主线程死循环，则采用这种方式

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
    delay = 5
    if braille_str.count("-") == 2:
        F3Points,F2Points,F1Points = braille_str.split("-",2)
        serttl.write(bytes.fromhex(NumsMatchHex("f3",F3Points,"ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f2", F2Points, "ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f1", F1Points, "ee")))
    elif braille_str.count("-") == 1:
        print("进来啦")
        F3Points,F2Points = braille_str.split("-",1)
        F1Points = "0"
        serttl.write(bytes.fromhex(NumsMatchHex("f3", F3Points, "ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f2", F2Points, "ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f1", F1Points, "ee")))
    elif braille_str.count("-") == 0:
        F1Points = "0"
        F2Points = "0"
        F3Points = braille_str.split("-",1)
        serttl.write(bytes.fromhex(NumsMatchHex("f3", F3Points, "ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f2", F2Points, "ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f1", F1Points, "ee")))
    else:
        pass

def APPSendTo32(serttl,BrailleData):
    delay = 5
    if BrailleData.count("-") == 2:
        F1Points,F2Points,F3Points = BrailleData.split("-",2)
        if F2Points == "null":
            F2Points = "0"

        serttl.write(bytes.fromhex(NumsMatchHex("f1", F1Points, "ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f2", F2Points, "ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f3", F3Points, "ee")))

    elif BrailleData.count("-") == 1:
        print("进来啦")
        F1Points,F2Points = BrailleData.split("-",1)
        if F2Points == "null":
            F2Points = "0"
        F3Points = "0"
        serttl.write(bytes.fromhex(NumsMatchHex("f1", F1Points, "ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f2", F2Points, "ee")))
        time.sleep(delay)
        serttl.write(bytes.fromhex(NumsMatchHex("f3", F3Points, "ee")))

    elif BrailleData.count("-") == 0:
        F1Points = "0"
        F2Points = "0"
        F3Points = BrailleData.split("-",1)
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
    client_main()
    serttl = get_serial.get_ttl_port(115200)
    while True:
        pass
    # try:
    #     # serusb = get_serial.get_usb_port(9600)
    #     serttl = get_serial.get_ttl_port(115200)
    #     APPSendTo32(serttl,"145-null-1")
    #     # SendCharTo32(serttl, "刘")
    #     # 145-256-1
    #     # time.sleep(5)
    #     # serttl.write(bytes.fromhex("f1  01 01 01 01 01 01 ee"))
    #     # time.sleep(5)
    #     # serttl.write(bytes.fromhex("f2  01 01 01 01 01 01 ee"))
    #     # time.sleep(5)
    #     # serttl.write(bytes.fromhex("f3  01 01 01 01 01 01 ee"))
    #     # time.sleep(5)
    # except KeyboardInterrupt:
    #     GPIO.cleanup()