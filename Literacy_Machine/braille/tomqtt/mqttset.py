# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import json
import time, datetime
import threading
import os



# MQTT: 当收到关于客户订阅的主题的消息时调用。    (handle_speed=Func(Maxspeed), C_Clock, gear)
def on_message(client, userdata, msg):
    MSG = str(msg.payload, encoding='utf-8')
    try:
        print(MSG)
    except:
        pass


# MQTT: 当代理响应连接请求时调用。
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("mne", qos=0) # 订阅主题
    # client.publish("AgvICU", "Agv1 Connected")


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
    client.will_set(topic="mne", payload="lwp already dissconnected", qos=0, retain=True)
    client.connect(HOST, PORT, 5)  # 链接
    # client.loop_forever()            # 以forever方式阻塞运行
    client.loop_start()  # 若主线程死循环，则采用这种方式


# Main
if __name__ == "__main__":
    # 启动Mqtt Client端
    try:
        client_main()
    except:
        pass
    while True:
        pass