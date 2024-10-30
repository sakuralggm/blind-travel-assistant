from gpiozero import LED, PWMLED
from time import sleep

class RGBLED(object):
    __instance = None
    __init_flag = False
    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = object.__new__(cls)
            return cls.__instance
        else:
            return cls.__instance
 
    def __init__(self):
        if self.__init_flag == False:
            self.red = PWMLED(17)
            self.green = PWMLED(22)
            self.blue = PWMLED(27)
            self.__init_flag = True
        else:
            pass

    def red_pulse(self):
        self.red.pulse()
        return
    
    def blue_pulse(self):
        self.blue.pulse()
        return
    
    def green_pulse(self):
        self.green.pulse()
        return
    
    def red_on(self):
        self.red.on()
        return
    
    def green_on(self):
        self.green.on()
        return
    
    def blue_on(self):
        self.blue.on()
        return
    
    def red_off(self):
        self.red.off()
        return
    
    def green_off(self):
        self.green.off()
        return
    
    def blue_off(self):
        self.blue.off()
        return
    


    
