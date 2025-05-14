import time
from machine import Pin, PWM
from random import random

class PWMPlayer():
    def __init__(self, pin_num=0, freq=440.0, freq_offset=0, freq_mult=1.0, transpose=0, freq_random_mult=0, duty_mult=1.0, duty_offset=0):
        self.pwm = PWM(Pin(pin_num, Pin.OUT))
        self.freq_offset = freq_offset
        self.freq_mult = freq_mult
        self.transpose = transpose
        self.freq_random_mult = freq_random_mult
        self.duty_mult = duty_mult
        self.duty_offset = duty_offset
        self.freq(freq)
    def duty_u16(self, duty):
        self.duty = int(duty * self.duty_mult + self.duty_offset)
    def on(self):
        self.pwm.duty_u16(self.duty)
    def off(self):
        self.pwm.duty_u16(0)
    def freq(self, freq):
        self._freq = freq
        self.set_freq()
    def set_transpose(self, semitone):
        self.transpose = self.transpose + semitone 
        self.set_freq()
    def set_freq(self):
        print(self._freq)
        fr = (self._freq + self._freq * 2**(1/12) * self.transpose ) * self.freq_mult #\
        #    + self.freq_offset \
        #    + random()*self.freq_random_mult
        print(fr)
        print(self)
        self.pwm.freq(int(fr))
    def __repr__(self):
        return [getattr(self,p) for p in dir(self)]



vol = 100.0


pwm1 = PWMPlayer(2)
pwm1.freq(220.0)
pwm1.duty_u16(int(32000.0 * vol / 100))
#pwm1.on()
time.sleep(0.5)
pwm1.off()
time.sleep(0.5)

left = [2,6,12]
right = [16, 20, 28]

left = [PWMPlayer(l) for l in left]
right = [PWMPlayer(r) for r in right]
all = left + right
for a,t in zip(all,[0,7,8,12,16,21]):
    a.freq(110)
    a.duty_u16(int(32000.0 * vol / 100))
    a.set_transpose(t)
    a.on()
    time.sleep(0.2)

time.sleep(0.5)

for a in all: a.off()




