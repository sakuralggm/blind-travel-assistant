from adxl345 import ADXL345
from led import RGBLED
from time import sleep  # 导入sleep函数，用于暂停代码执行
from mqtt import MQTT

class Accelerator(object):
    def __init__(self):
        self.adxl345 = ADXL345()
        self.rgb = RGBLED()
        self.dev_id = "" # 设备ID，填自己的
        self.dev_name = "" # 设备名称
        self.dev_key = "" # 设备密钥
        self.mqtt = MQTT(self.dev_id, self.dev_name, self.dev_key)
        self.count = 0
        
    def check_adxl345(self):
        axes = self.adxl345.get_axes(True)
        self.publish(axes['x'], axes['y'], axes['z'])
        if (len([i for i in (abs(axes['x']), abs(axes['y']), abs(axes['z'])) if i > 2]) >= 2):
            print ("Fall detected!!\n")
            print ("   x = %.3fG" % ( axes['x'] ))
            print ("   y = %.3fG" % ( axes['y'] ))
            print ("   z = %.3fG" % ( axes['z'] ))
            self.alarm()
    
    def alarm(self):
        self.rgb.blue_pulse()
        sleep(4)
        self.rgb.blue_off()
    
    def publish(self, x_acc, y_acc, z_acc):
        value = {
            'x': x_acc,
            'y': y_acc,
            'z': z_acc
        }
        self.mqtt.client.publish(topic=self.mqtt.topic_publish, 
                                 payload=self.mqtt.data(self.count, value, "acceleration"), qos=1)
        self.count += 1