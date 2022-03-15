# coding=utf-8
import toaudio.AudioCrotrol
import togpio.gpioset
import toserial.serialset
from todatatrans.datatrans import *
from tobraille.toBraille import *
import socket  # 客户端 发送一个数据，再接收一个数据
import time
import threading
import json
from datetime import datetime
import os
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import json
import requests

FreWords = ['乐','州','涌','耸','与','陆','各','浓','奋','赏']
FreWordsShow = ['123-26-23','34-12356-1','12345-24-1','234-256-3','346-2','123-1256-23','1245-26-23','1345-256-2','124-356-23','156-236-3']
ColWords = ['学','雨','粒','巧','探','刘','庆','烤','材','伴']


# MQTT: 当收到关于客户订阅的主题的消息时调用。
def on_message(client, userdata, msg):
    global Serttl, SerUsb, AppEna, aud
    data = str(msg.payload, encoding='utf-8')
    if data == "lwp already dissconnected":
        print(data)
    else:
        if AppEna == True:
            try:
                data = json.loads(data)
                if data['mach_id'] == 1:
                    tran = data['tran']
                    word = json.loads(data['word'])[tran]
                    print("汉字：" + tran)
                    print("盲文：" + word)
                    SerUsb.write(StrToScreen("char", tran))
                    SerUsb.write(StrToScreen("state", word))
                    toserial.serialset.APPSendTo32(Serttl, word)
                    aud.says_api(tran)
                else:
                    print("二号机")
                    tran = data['tran']
                    word = data['word']
                    print("汉字：" + tran)
                    print("盲文：" + word)
            except:
                pass
        else:
            pass

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
    HOST = "119.23.254.108"  # 设置Ip
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



def iostate():
    global IoState,Mods,SayRecord,SerUsb,aud
    temp = 1
    while True:
        IoState = IO.ioflash()
        time.sleep(0.2)
        if IO.Bottom_state_Add_Mods(IoState["B4"], Mods) is True:
            Mods = IO.Mods
        else:
            pass
        if IoState['B1'] + IoState['B2'] != 2 and SayRecord == True:
            os.system('sudo pkill mpg123')
            SerUsb.write(StrToScreen("state", "结束播放"))
            SayRecord = False
        else:
            pass
        # if IO.Bottom_state_First(IoState["B5"]) is True:
        #     aud.stop_says()
        #     aud.SayLocalMp3("GetWordsInCols.mp3")
            # Mods = IO.Mods



def RpiRecord():
    global SayRecord, RecEna, IoState,SerUsb
    fval = 1
    while True:
        if RecEna is True:
            if IoState['B3'] == 0 and fval == 1:
                aud.stop_says()  # 杀死线程
                aud.stop_record()
                print("开始录音")
                SerUsb.write(StrToScreen("state", "开始录音"))
                aud.start_record()
                fval = 0
            elif IoState['B3'] == 0 and fval == 0:
                SerUsb.write(StrToScreen("state", "正在录音"))
                print("正在录音")
            elif IoState['B3'] == 1 and fval == 0:
                print("录音结束")
                SerUsb.write(StrToScreen("state", "录音结束"))
                aud.stop_record()
                threading.Thread(target=SayRecordThreading).start()
                fval = 1
            else:
                pass
            time.sleep(0.3)


def SayRecordThreading():
    global SayRecord,token, aud, LocalData,LocalDataEna
    print("正在转换")
    try:
        SayRecord = True
        SerUsb.write(StrToScreen("state", "正在转换"))
        result = aud.voicetotext(token,"record.wav")
        aud.says_api(result[0])
        braille_str = toBraille(result[0])[1]  # 取开头第一句话做识别
        SerUsb.write(StrToScreen("char",result[0]))
        SerUsb.write(StrToScreen("state",braille_str))
        toserial.serialset.SendCharTo32(Serttl, result)
        r = requests.get("http://119.23.254.108:10086/postlwp", data=result[0].encode("utf-8").decode("latin1"))
        print(r.text)
        aud.says_api(r.text)
        # a = datetime.now()  # 获得当前时间
        # summary = aud.get_summary(result)
        # aud.SayLocalMp3("GetWordsInCols.mp3")
        # aud.says_api(summary[:15])
        # b = datetime.now()
        # print(summary)
        # durn = (b - a).seconds  # 两个时间差，并以秒显示出来
        # print(durn)
        SayRecord = False
    except:
        SerUsb.write(StrToScreen("state", "网络错误"))
        aud.SayLocalMp3("NetError.mp3")


def SaylocalThreading():
    global mp3filename,SaylocalEna,aud
    while True:
        try:
            if SaylocalEna is True:
                aud.stop_says()
                aud.SayLocalMp3(mp3filename)
                SaylocalEna = False
            else:
                pass
        except:
            pass


def Mod3_FreWords():
    global FreCharIndex, IoState, CharIndexMax, aud, mp3filename, SaylocalEna, IO, LocalData, FreWordsEna,LocalDataEna
    while True:
        # 向前索引
        if FreWordsEna is True:
            if IO.Bottom_state_Add_Index(IoState['B2'], IoState['B1'], FreCharIndex) is True:
                FreCharIndex = FreCharIndex+IO.Index
                print(FreCharIndex)
                try:
                    SaylocalEna = False
                    aud.stop_says()
                    time.sleep(0.5)
                    SerUsb.write(StrToScreen("char", FreWords[FreCharIndex]))
                    mp3filename = "FreWords" + str(FreCharIndex) + ".mp3"
                    SerUsb.write(StrToScreen("state", "第" + str(FreCharIndex) + "个字"))
                    toserial.serialset.APPSendTo32(Serttl, FreWordsShow[FreCharIndex])
                    # aud.says_api(FreWords[FreCharIndex])
                    # r = requests.get("http://119.23.254.108:10086/postlwp",
                    #                  data=FreWordsShow[FreCharIndex].encode("utf-8").decode("latin1"))
                    # print(r.text)
                    # aud.says_api(r.text)
                    SaylocalEna = True
                except:
                    SerUsb.write(StrToScreen("state", "网络错误"))
                    aud.SayLocalMp3("NetError.mp3")
            else:
                pass
        else:
            pass
        time.sleep(0.2)


def Mod4_ColWords():
    global ColsCharIndex, IoState, CharIndexMax, aud, mp3filename, SaylocalEna, IO, LocalData, ColWordsEna,LocalDataEna
    while True:
        # 向前索引
        if ColWordsEna is True:
            if IO.Bottom_state_Add_Index(IoState['B2'], IoState['B1'], ColsCharIndex) is True:
                ColsCharIndex = ColsCharIndex+IO.Index
                print(ColsCharIndex)
                try:
                    SaylocalEna = False
                    aud.stop_says()
                    time.sleep(0.5)
                    SerUsb.write(StrToScreen("char", ColWords[ColsCharIndex]))

                    mp3filename = "ColWords" + str(ColsCharIndex) + ".mp3"
                    SerUsb.write(StrToScreen("state", "第" + str(ColsCharIndex) + "个字"))
                    toserial.serialset.SendCharTo32(Serttl, ColWords[ColsCharIndex])
                    # aud.says_api(ColWords[ColsCharIndex])
                    # r = requests.get("http://119.23.254.108:10086/postlwp",
                    #                  data=ColWords[ColsCharIndex].encode("utf-8").decode("latin1"))
                    # print(r.text)
                    # aud.says_api(r.text)
                    SaylocalEna = True
                except:
                    SerUsb.write(StrToScreen("state", "网络错误"))
                    aud.SayLocalMp3("NetError.mp3")
            else:
                pass
        else:
            pass
        time.sleep(0.2)

def NumsMatchHex(MachID,String1,HexEnd):
    HexStr =MachID
    for i in range(1,7):
        if String1.find(str(i)) != -1:
            HexStr = HexStr + "01"
        else:
            HexStr = HexStr + "00"
    HexStr = HexStr + HexEnd
    return HexStr

if __name__ == '__main__':
    mp3filename =""
    LocalData =""
    SaylocalEna = True
    SayRecord = False
    Mods = 0  # 刚开始模式0
    RecEna = AppEna = FreWordsEna = ColWordsEna = LocalDataEna = False
    aud = toaudio.AudioCrotrol
    token = aud.fetch_token()
    IO = togpio.gpioset.BGpio()
    IO.Gpio_Init()
    IoState = IO.ioflash()
    SerUsb = toserial.serialset.get_serial.get_usb_port(9600)
    Serttl = toserial.serialset.get_serial.get_ttl_port(115200)
    client_main()
    t1 = threading.Thread(target=iostate).start()
    t2 = threading.Thread(target=RpiRecord).start()
    t3 = threading.Thread(target=Mod3_FreWords).start()
    t4 = threading.Thread(target=Mod4_ColWords).start()
    t5 = threading.Thread(target=SaylocalThreading).start()
    SerUsb.write(RefreshToScreen("page 0"))
    Serttl.write(bytes.fromhex(NumsMatchHex("f1", "0", "ee")))
    Serttl.write(bytes.fromhex(NumsMatchHex("f2", "0", "ee")))
    Serttl.write(bytes.fromhex(NumsMatchHex("f3", "0", "ee")))
    # Serttl.write("f1 00 00 00 00 00 00 ee")
    # Serttl.write("f2 00 00 00 00 00 00 ee")
    # Serttl.write("f3 00 00 00 00 00 00 ee")
    aud.SayLocalMp3("welcome.mp3")
    SaylocalEna = True
    # t9 = threading.Thread(target=TTL32_SendData_GetColWords).start()
    while True:
        try:
            if ModJudge.ModJudgeFirst(Mods) is True:
                RecEna = AppEna = FreWordsEna = ColWordsEna = SaylocalEna = False
                if Mods == 1 :  # 模式1：自主学习
                    aud.stop_says()
                    print("自主学习模式")
                    SerUsb.write(RefreshToScreen("page 1"))
                    SerUsb.write(StrToScreen("mod", "自主学习模式"))
                    SerUsb.write(StrToScreen("char", ""))
                    SerUsb.write(StrToScreen("state", ""))
                    aud.SayLocalMp3("Mod1.mp3")
                    RecEna = True

                elif Mods == 2 :  # 模式2：教学模式
                    AppEna = True
                    print("APP教学模式")
                    SerUsb.write(StrToScreen("mod", "APP教学模式"))
                    SerUsb.write(StrToScreen("char", ""))
                    SerUsb.write(StrToScreen("state", ""))
                    aud.stop_says()
                    aud.SayLocalMp3("Mod2.mp3")
                elif Mods == 3 :  # 模式3：高频词模式
                    AppEna = False
                    SerUsb.write(StrToScreen("mod", "高频词学习模式"))
                    SerUsb.write(StrToScreen("char", ""))
                    SerUsb.write(StrToScreen("state", ""))
                    SerUsb.write(StrToScreen("char", "联网中"))
                    aud.stop_says()
                    aud.SayLocalMp3("Mod3.mp3")
                    time.sleep(1)
                    SerUsb.write(StrToScreen("char", "更新成功"))
                    FreCharIndex = 0
                    FreWordsEna = True
                    print("高频词模式")
                elif Mods == 4 :  # 模式2：收藏词模式
                    SerUsb.write(StrToScreen("mod", "收藏词学习模式"))
                    SerUsb.write(StrToScreen("char", ""))
                    SerUsb.write(StrToScreen("state", ""))
                    aud.stop_says()
                    aud.SayLocalMp3("Mod4.mp3")
                    ColsCharIndex = 0
                    ColWordsEna = True
                    print("收藏词模式")
                else:
                    if Mods >4:
                        Mods = 1
                    pass
                print(Mods)
        except KeyboardInterrupt:
            GPIO.cleanup()