import re 
import time
from machine import Pin, PWM
from random import random

class PWMPLayer():
    def __init__(self, pin_num=0, freq_offset=0, freq_mult=1.0, transpose=0, freq_random_mult=0, duty_mult=1.0, duty_offset=0):
        self.pwm = PWM(Pin(pin_num, Pin.OUT))
        self.freq_offset = freq_offset
        self.freq_mult = freq_mult
        self.transpose = transpose
        self.freq_random_mult = freq_random_mult
        self.duty_mult = duty_mult
        self.duty_offset = duty_offset
    def duty_u16(self, duty):
        self.pwm.duty_u16(int(duty * self.duty_mult + self.duty_offset))
    def freq(self, freq):
        self.pwm.freq(int(
            (freq * 2**(1/12) * self.transpose ) * self.freq_mult
            + self.freq_offset
            + random()*self.freq_random_mult
        ))


vol = 100.0
pwm = PWMPlayer()
pwm.freq(440.0)
pwm.duty_u16(int(32000.0 * vol / 100))