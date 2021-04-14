#-- coding:utf8 --
import RPi.GPIO as GPIO
import time


class BGpio:
    B1 = 5   # 向前切换
    B2 = 6   # 向后切换
    B3 = 13  # 录音按钮
    B4 = 19  # 模式切换
    B5 = 26  # 收藏词
    B6 = 12  # 程序启动
    state = 0
    Bfval = 1
    flag = 1

    Mods = 0
    MBfval = 1
    Mflag = 1

    Index = 0
    IBfval = "11"
    Iflag = 1
    def __init__(self):
        self.B1 = 5
        self.B2 = 6
        self.B3 = 13
        self.B4 = 19
        self.B5 = 26
        self.B6 = 12
        pass

    # 1. Gpio 初始化
    def Gpio_Init(self):
        GPIO.setwarnings(False)       # 关闭警告
        GPIO.setmode(GPIO.BCM)        # 选择GPIO编码格式 BCM

        # 设置输入检测引脚  上拉
        In_GPIOS = (BGpio.B1, BGpio.B2, BGpio.B3, BGpio.B4, BGpio.B5, BGpio.B6)
        GPIO.setup(In_GPIOS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # @staticmethod
    # def B1_Get():

    @staticmethod
    def ioflash():
        B1var = GPIO.input(BGpio.B1)
        B2var = GPIO.input(BGpio.B2)
        B3var = GPIO.input(BGpio.B3)
        B4var = GPIO.input(BGpio.B4)
        B5var = GPIO.input(BGpio.B5)
        B6var = GPIO.input(BGpio.B6)
        IOSTATE = {'B1':B1var, 'B2': B2var, 'B3':B3var, 'B4':B4var, 'B5':B5var, 'B6':B6var}
        return IOSTATE

    # 判断按键状态 按下后松开  变量+1
    @staticmethod
    def Bottom_state_Add_Mods(MBval, Mods):
        if MBval != BGpio.MBfval and BGpio.Mflag == 1:
            print("按下")
            BGpio.Mflag = 0
            BGpio.MBfval = MBval
            BGpio.Mods = Mods
            return False
        elif MBval == BGpio.MBfval and BGpio.Mflag == 0:
            # print("结束")
            return False
        elif MBval != BGpio.MBfval and BGpio.Mflag == 0:
            print("结束")
            BGpio.Mflag = 1
            BGpio.MBfval = MBval
            BGpio.Mods = BGpio.Mods + 1
            return True
        else:
            BGpio.Mflag = 1
            return False

    # 判断按键状态 按下后松开  变量+1
    @staticmethod
    def Bottom_state_Add_Index(IB1val,IB2val, Index):
        if (str(IB1val)+str(IB2val)) != BGpio.IBfval and BGpio.Iflag == 1:
            print("按下")
            BGpio.Iflag = 0
            BGpio.IBfval = str(IB1val)+str(IB2val)
            BGpio.Index = Index
            return False
        elif (str(IB1val)+str(IB2val)) == BGpio.IBfval and BGpio.Iflag == 0:
            # print("结束")
            return False
        elif (str(IB1val)+str(IB2val)) != BGpio.IBfval and BGpio.Iflag == 0:
            print("结束")
            BGpio.Iflag = 1
            if BGpio.IBfval == "01":
                BGpio.Index = -1
            elif BGpio.IBfval == "10":
                BGpio.Index = 1
                pass
            else:
                pass
            BGpio.IBfval = (str(IB1val)+str(IB2val))
            return True
        else:
            BGpio.Iflag = 1
            return False

# 判断按键状态 按下后松开  变量+1
    @staticmethod
    def Bottom_state_First(Bval):
        if Bval != BGpio.Bfval and BGpio.flag == 1:
            print("按下")
            BGpio.flag = 0
            BGpio.Bfval = Bval
            return False
        elif Bval == BGpio.Bfval and BGpio.flag == 0:
            return False
        elif Bval != BGpio.Bfval and BGpio.flag == 0:
            print("结束")
            BGpio.Mflag = 1
            BGpio.Bfval = Bval
            return True
        else:
            BGpio.Mflag = 1
            return False


if __name__ == "__main__":
    # IO口测试
    IO = BGpio()
    IO.Gpio_Init()
    Index =  1
    Mod = 1
    try:
        while True:
            var = IO.ioflash()
            print(var)
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
            time.sleep(0.2)
    except KeyboardInterrupt:
        GPIO.cleanup()