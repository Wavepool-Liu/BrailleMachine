import socket  # 客户端 发送一个数据，再接收一个数据
import time
import threading
import json


def clientrec():
    global client
    while True:
        data = client.recv(1024)
        data = json.loads(data.decode())
        if data['mach_id'] == 2:
            tran = data['tran']
            word = data['word']
            print("汉字：" + tran)
            print("盲文：" + word)


def clientsend():
    global client
    while True:
        hello = "你好\n"
        client.send(hello.encode('utf-8'))  # 发送一条信息 python3 只接收btye流
        time.sleep(3)


if __name__ == '__main__':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 声明socket类型，同时生成链接对象
    client.connect(('192.168.31.229', 10086))  # 建立一个链接，连接到本地的6969端口
    client.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 0)
    t1 = threading.Thread(target=clientrec).start()
    t2 = threading.Thread(target=clientsend).start()
    while True:
        pass

