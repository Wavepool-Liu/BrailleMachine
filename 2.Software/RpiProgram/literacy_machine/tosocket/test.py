#! /usr/bin/env python
# -*- coding:utf-8 -*-
# version : Python 2.7.13

import os, sys, time
import socket


def doConnect(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        client.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 0)
        return client
    except:
        return None


def main():
    host, port = '10.20.173.51', 10086
    print(host, port)
    sockLocal = doConnect(host, port)

    while True:
        try:
            msg = str(time.time())
            # sockLocal.send(msg)
            print("send msg ok : ", msg)
            print("recv data :", sockLocal.recv(1024))
        except socket.error:
            print("\r\nsocket error,do reconnect ")
            time.sleep(3)
            sockLocal = doConnect(host, port)
        except:
            print('\r\nother error occur ')
            time.sleep(3)
        time.sleep(1)


if __name__ == "__main__":
    main()