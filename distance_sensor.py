from gpiozero import DistanceSensor
from mqtt import MQTT
from motor import MOTOR

class CSB(object):
    def __init__(self):
        self.sensor = DistanceSensor(23, 24)
        self.dev_id = "" # 设备ID，填自己的
        self.dev_name = "" # 设备名称
        self.dev_key = "" # 设备密钥
        self.mqtt = MQTT(self.dev_id, self.dev_name, self.dev_key)
        self.count = 0
        self.motor = MOTOR()

    def check_distance_sensor(self):
        print(self.sensor.distance)
        self.publish(self.sensor.distance)
        if (self.sensor.distance < 0.2):
            print("Warning! Obstruction ahead!\n")
            self.motor.motor_alarm()
    
    def publish(self, distance):
        self.mqtt.client.publish(topic=self.mqtt.topic_publish, 
                                 payload=self.mqtt.data(self.count, round(distance, 4), "distance"), qos=1)
        self.count += 1