import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from urllib.parse import quote
import time
import json
import random
import base64
import hmac

class MQTT(object):
    def __init__(self, dev_id, dev_name, dev_key):
        self.HOST = "mqtts.heclouds.com"         # 未加密地址
        self.PORT = "1883"                       # 未加密端口
        self.PRO_ID = ""                         # 产品ID, 填自己的
        self.DEV_ID = dev_id                     # 设备ID 
        self.DEV_NAME = dev_name                 # 设备名称
        self.DEV_KEY = dev_key                   # 设备Key
        self.ACCESS_KET = ""   # 产品AccessKey, 填自己的
        
        # 配置MQTT连接信息
        self.client_id = self.DEV_NAME
        self.username = self.PRO_ID
        self.password = self.token(self.PRO_ID, self.DEV_NAME, self.DEV_KEY)
        print('username:' + self.username)
        print('password:' + self.password)
        self.client = mqtt.Client(client_id=self.client_id, clean_session=True, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.on_disconnect = self.on_disconnect
        self.client.username_pw_set(username=self.username, password=self.password)
        # client.tls_set(ca_certs='MQTTS-certificate.pem')              # 加密方式需要使用鉴权证书
        # client.tls_insecure_set(True) #关验证
        self.client.connect(self.HOST, int(self.PORT), keepalive=1200)

        # 按照OneENT要求的格式，配置数据发布和订阅的主题
        self.topic_dp = '$sys/%s/%s/dp/post/json/+' % (self.username, self.DEV_NAME)   # 设备上报数据主题
        self.topic_cmd = '$sys/%s/%s/cmd/#' % (self.username, self.DEV_NAME)           # 设备接受命令主题
        self.topic_cmds = '$sys/%s/%s/cmd/request/' % (self.username, self.DEV_NAME)   # 设备接受命令主题
        self.topic_publish = '$sys/%s/%s/dp/post/json' %(self.username,self.DEV_NAME)
        self.client.loop_start()

    # 用于生成Token的函数
    def token(self, _pid, dname, access_key):
        version = '2018-10-31'
        # res = 'mqs/%s' % id           # 通过MQ_ID访问
        # res = 'products/%s' % id      # 通过产品ID访问产品API
        res = 'products/%s/devices/%s' % (_pid, dname)  # 通过MQTTS产品id和设备名称访问
        # 用户自定义token过期时间
        et = str(int(time.time()) + 3600000)
        # 签名方法，支持md5、sha1、sha256
        method = 'md5'
        # 对access_key进行decode
        key = base64.b64decode(access_key)
        # print(key)
        # 计算sign
        org = et + '\n' + method + '\n' + res + '\n' + version
        # print(org)
        sign_b = hmac.new(key=key, msg=org.encode(), digestmod=method)
        sign = base64.b64encode(sign_b.digest()).decode()
        # print(sign)
        # value 部分进行url编码，method/res/version值较为简单无需编码
        sign = quote(sign, safe='')
        res = quote(res, safe='')
        # token参数拼接
        token = 'version=%s&res=%s&et=%s&method=%s&sign=%s' % (version, res, et, method, sign)
        return token

    # 定义了带时间戳的输出格式
    def ts_print(self, *args):
        t = time.strftime("[%Y-%m-%d %H:%M:%S")
        ms = str(time.time()).split('.')[1][:3]
        t += ms + ']:'
        print(t, args)

    # 当MQTT代理响应客户端连接请求时触发
    def on_connect(self, client, userdata, flags, rc):
        self.ts_print("<<<<CONNACK")
        self.ts_print("connected with result code: " + mqtt.connack_string(rc), rc)
        client.subscribe(topic=self.topic_cmd, qos=1)        # 订阅由OneNET平台下发的命令
        client.subscribe(topic=self.topic_dp, qos=1)         # 订阅上传数据的响应结果

    # 当接收到MQTT代理发布的消息时触发
    def on_message(self, client, userdata, msg):
        self.ts_print('on_message')
        self.ts_print("Topic: " + str(msg.topic))
        self.ts_print("Payload: " + str(msg.payload))
        if self.topic_cmds in msg.topic:                     # 命令响应的主题
            responseTopic = str(msg.topic).replace("request","response",1)
            # print(responseTopic)
            client.publish(responseTopic,'OK',qos = 1)  # 发布命令响应

    # 当客户端调用publish()发布一条消息至MQTT代理后被调用
    def on_publish(self, client, userdata, mid):
        self.ts_print("Puback:mid: " + str(mid))
        self.ts_print("Puback:userdata: " + str(userdata))

    # 当MQTT代理响应订阅请求时被调用
    def on_subscribe(self, client, obj, mid, granted_qos):
        self.ts_print("Subscribed: message:" + str(obj))
        self.ts_print("Subscribed: mid: " + str(mid) + "  qos:" + str(granted_qos))

    # 当客户端与代理服务器断开连接时触发
    def on_disconnect(self, client):
        self.ts_print('DISCONNECTED')

    # 从树莓派发布到服务器的数据内容
    def data(self, ds_id, value, data_id):
        message = {
            "id": int(ds_id),
            "dp": {
                data_id: [{      # 传感器采集的数据
                    "v": value
                }],
            }
        }
        # print(message)
        message = json.dumps(message).encode('ascii')
        return message
