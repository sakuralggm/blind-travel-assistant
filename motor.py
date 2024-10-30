from gpiozero import Motor
from time import sleep


class MOTOR(object):
    def __init__(self):
        self.motor = Motor(13, 19)


    def motor_alarm(self):
        self.motor.forward(1)
        sleep(2)
        self.motor.stop()
        return
    


    
