import tomqtt.mqttset
import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    data = str(msg.payload, encoding='utf-8')
    if data == "lwp already dissconnected":
        pass
        # print(data)
    else:
        data = json.loads(data)
        # if data['mach_id'] == 1:
        #     tran = data['tran']
        #     word = data['word']
        #     print("汉字：" + tran)
        #     print("盲文：" + word)
        # else:
        #     tran = data['tran']
        #     word = data['word']
        #     print("汉字：" + tran)
        #     print("盲文：" + word)
        # client.publish("mne", "get")

# MQTT: 当代理响应连接请求时调用。
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("mne", qos=0) # 订阅主题


# MQTT: 当与代理断开连接时调用
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

if __name__ == "__main__":
    # 启动Mqtt Client端
    try:
        client = tomqtt.mqttset.client_main()
    except:
        pass
    while True:
        pass