# coding=utf-8
import toaudio.AudioCrotrol
import togpio.gpioset
import toserial.serialset
from todatatrans.datatrans import *
import socket  # 客户端 发送一个数据，再接收一个数据
import time
import threading
import json
# from tobraille import *

FreWords = ['','州','春','耸','与','陆','各','浓','奋','赏']
ColWords = ['','春','粒','巧','探','刘','庆','烤','材','伴']


def clientrec():
    global client,SerUsb,AppEna,LocalData,LocalDataEna
    while True:
        try:
            data = client.recv(1024)
            data = json.loads(data.decode())
            if data['mach_id'] == 1 and AppEna is True:
                SerUsb.write(StrToScreen("state", "已连接"))
                tran = data['tran']
                word = data['word']
                SerUsb.write(StrToScreen("char", tran))
                LocalData = tran
                LocalDataEna = True
                aud.says_api(tran)
                print("汉字：" + tran)
                print("盲文：" + word)
            else:
                SerUsb.write(StrToScreen("state", "未连接"))
        except:
            pass


def B4mods():
    global IO, IoState,Mods,mp3filename,SaylocalEna
    while True:
        if IO.Bottom_state_Add_Mods(IoState["B1"], Mods) is True:
            Mods = IO.Mods
        if IO.Bottom_state_First(IoState['B5']) is True:
            mp3filename = "GetWordsInCols.mp3"
            SaylocalEna = True
        else:
            pass


def iostate():
    global IoState
    while True:
        IoState = IO.ioflash()
        time.sleep(0.2)



def RpiRecord():
    global RecEna, IoState, SaysEna,SerUsb
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
                SaysEna = True
                fval = 1
            else:
                pass

            if IoState['B1'] + IoState['B2'] != 2:
                SerUsb.write(StrToScreen("state", "结束播放"))
                aud.stop_says()
                SaysEna = False
            time.sleep(0.3)


def SayRecordThreading():
    global SaysEna, token, aud, LocalData,LocalDataEna
    while True:
        if SaysEna is True:
            print("正在转换")
            try:
                SerUsb.write(StrToScreen("state", "正在转换"))
                result = aud.voicetotext(token,"record.wav")
                SerUsb.write(StrToScreen("char",result))
                LocalData = result
                LocalDataEna = True
                print(result)
                summary = aud.get_summary(result)
                aud.says_api(summary)
                SaysEna = False
            except:
                SerUsb.write(StrToScreen("state", "网络错误"))
                aud.SayLocalMp3("NetError.mp3")
        else:
            pass


def SaylocalThreading():
    global mp3filename,SaylocalEna,aud
    while True:
        try:
            if SaylocalEna  is True:
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
                if FreCharIndex == 0:
                    SerUsb.write(StrToScreen("state", "已回到第一组"))
                    SerUsb.write(StrToScreen("char", ""))
                    mp3filename = "BackcharIndex.mp3"
                    IO.Index = FreCharIndex = 2
                    aud.stop_says()
                    SaylocalEna = True
                elif FreCharIndex > 10:
                    print("len(FreWords)")
                    SerUsb.write(StrToScreen("state", "已学习完所有词库"))
                    SerUsb.write(StrToScreen("char", ""))
                    mp3filename = "OvercharIndex.mp3"
                    IO.Index = FreCharIndex = len(FreWords)
                    aud.stop_says()
                    SaylocalEna = True
                else:
                    SaylocalEna = False
                    aud.stop_says()
                    time.sleep(0.5)
                    SerUsb.write(StrToScreen("char", FreWords[FreCharIndex]))
                    LocalData = FreWords[FreCharIndex]
                    LocalDataEna = True
                    mp3filename = "FreWords" + str(FreCharIndex) + ".mp3"
                    SerUsb.write(StrToScreen("state", "第" + str(FreCharIndex) + "个字"))
                    SaylocalEna = True
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
            if IO.Bottom_state_Add_Index(IoState['B1'], IoState['B2'], ColsCharIndex) is True:
                ColsCharIndex = IO.Index
                print(ColsCharIndex)
                if ColsCharIndex == 0:
                    SerUsb.write(StrToScreen("state", "已回到第一组"))
                    SerUsb.write(StrToScreen("char", ""))
                    mp3filename = "BackcharIndex.mp3"
                    IO.Index = ColsCharIndex = 5
                    aud.stop_says()
                    SaylocalEna = True
                elif ColsCharIndex > 10:
                    SerUsb.write(StrToScreen("state", "已学习完所有词库"))
                    SerUsb.write(StrToScreen("char", ""))
                    mp3filename = "OvercharIndex.mp3"
                    IO.Index = ColsCharIndex = len(ColWords)
                    aud.stop_says()
                    SaylocalEna = True
                else:
                    SaylocalEna = False
                    aud.stop_says()
                    time.sleep(0.5)
                    SerUsb.write(StrToScreen("char", ColWords[ColsCharIndex]))
                    LocalData =  ColWords[ColsCharIndex]
                    LocalDataEna = True
                    mp3filename = "ColWords" + str(ColsCharIndex) + ".mp3"
                    SerUsb.write(StrToScreen("state", "第" + str(ColsCharIndex) + "个字"))
                    SaylocalEna = True
            else:
                pass
        else:
            pass
        time.sleep(0.2)

# def TTL32_SendData_GetColWords():
#     global LocalData,LocalDataEna
#     while True:
#         if LocalDataEna is True:
#             toserial.serialset.SendCharTo32(Serttl, LocalData)
#             LocalDataEna = False
#         else:
#             pass


if __name__ == '__main__':
    mp3filename =""
    LocalData =""
    SaylocalEna = True
    Mods = 0  # 刚开始模式0
    RecEna=SaysEna=AppEna= FreWordsEna= ColWordsEna  = LocalDataEna = False
    aud = toaudio.AudioCrotrol
    token = aud.fetch_token()
    IO = togpio.gpioset.BGpio()
    IO.Gpio_Init()
    IoState = IO.ioflash()
    SerUsb = toserial.serialset.get_serial.get_usb_port(9600)
    # Serttl = toserial.serialset.get_serial.get_ttl_port(115200)

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 声明socket类型，同时生成链接对象
        client.connect(('192.168.43.127', 10086))  # 建立一个链接，连接到本地的6969端口
        client.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 0)
        t1 = threading.Thread(target=clientrec).start()
    except:
        client = "None"
        pass
    t2 = threading.Thread(target=B4mods).start()
    t3 = threading.Thread(target=iostate).start()
    t4 = threading.Thread(target=RpiRecord).start()

    t5 = threading.Thread(target=SayRecordThreading).start()
    t6 = threading.Thread(target=SaylocalThreading).start()

    t7 = threading.Thread(target=Mod3_FreWords).start()
    t8 = threading.Thread(target=Mod4_ColWords).start()
    SaylocalEna = True
    SerUsb.write(RefreshToScreen("page 0"))
    aud.SayLocalMp3("welcome.mp3")
    print(2121)
    # t9 = threading.Thread(target=TTL32_SendData_GetColWords).start()
    while True:
        if ModJudge.ModJudgeFirst(Mods) is True:
            RecEna = SaysEna = AppEna = FreWordsEna = ColWordsEna = SaylocalEna = False
            if Mods == 1 :  # 模式1：自主学习
                aud.stop_says()
                print("自主学习模式")
                SerUsb.write(RefreshToScreen("page 1"))
                SerUsb.write(StrToScreen("mod", "自主学习模式"))
                SerUsb.write(StrToScreen("char", ""))
                SerUsb.write(StrToScreen("state", ""))
                aud.SayLocalMp3("Mod1.mp3")
                RecEna = True
                SaysEna = False
            elif Mods == 2 :  # 模式2：教学模式
                print("APP教学模式")
                SerUsb.write(StrToScreen("mod", "APP教学模式"))
                SerUsb.write(StrToScreen("char", ""))
                aud.stop_says()
                aud.SayLocalMp3("Mod2.mp3")
                if client == "None":
                    SaylocalEna = True
                    mp3filename = "AppError.mp3"
                    SerUsb.write(StrToScreen("state", "未连接"))
                else:
                    AppEna = True
                    SerUsb.write(StrToScreen("state", "已连接"))
            elif Mods == 3 :  # 模式3：高频词模式
                SerUsb.write(StrToScreen("mod", "高频词学习模式"))
                SerUsb.write(StrToScreen("char", ""))
                SerUsb.write(StrToScreen("state", ""))
                SerUsb.write(StrToScreen("char", "联网中"))
                aud.stop_says()
                aud.SayLocalMp3("Mod3.mp3")
                time.sleep(2)
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
                ColsCharIndex = 5
                ColWordsEna = True
                print("收藏词模式")
            else:
                if Mods >4:
                    Mods = 1
                pass
            print(Mods)
