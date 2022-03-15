import binascii

# 往串口屏组件发送数据
def StrToScreen(id, contant):
    id_hex = binascii.hexlify((id + ".txt" + "=\"").encode('gb2312')).decode('gb2312')
    contant_hex = binascii.hexlify((contant + "\"").encode('gb2312')).decode('gb2312')
    return bytes.fromhex(id_hex + contant_hex + "ff ff ff")

def RefreshToScreen(order):
    order_hex = binascii.hexlify(order.encode('gb2312')).decode('gb2312')
    return bytes.fromhex(order_hex + "ff ff ff")

class ModJudge:
    FMod = 0


    @staticmethod
    def ModJudgeFirst(Mod):
        if Mod != ModJudge.FMod:
            print("ModJudge.FMod: ",str(ModJudge.FMod))
            ModJudge.FMod = Mod
            return True
        else:
            return False

        # return True
if __name__ == '__main__':
    mods = 1