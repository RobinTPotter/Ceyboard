import time
import utime
from machine import Pin, PWM
from random import random
import math


WAVE_TABLE_SIZE = 100
SAMPLE_RATE = 4000

class PWMPlayer:
    def __init__(self, pin):
        self.pwm = Pin(pin, Pin.OUT)
        self.pwm.freq(62500)
        self.pwm.duty_u16(0)
        self.on = True
        self.amp = 1.0
        self.index = 0
        self.step = 0
    def freq(self, freq):
        self.step = freq * WAVE_TABLE_SIZE / SAMPLE_RATE

channels = [PWMPlayer(pin) for pin in [0,1,2,3,4,5]]  #6 channels

ff = 440.0
for i,ch in enumerate(channels):
    ch.freq(440 * (5+i)/5)

# generate wave table
wave = [
    int( 65535 * (1 + math.sin(2 * math.pi * i/WAVE_TABLE_SIZE) ) / 2 ) for i in range(WAVE_TABLE_SIZE)
]

interval_ms = 1000000 / SAMPLE_RATE

for _ in range(3 * SAMPLE_RATE):
    start_time = utime.ticks_us()
    for ch in channels:
        if ch.on:
            index = ch.index
            value = int(ch.amp * wave[int(index) % WAVE_TABLE_SIZE])
            ch.pwm.duty_u16(value)
            ch.index = ( index + ch.step ) % WAVE_TABLE_SIZE
        else:
            ch.pwm.duty_u16(0)
    
    elapsed = utime.ticks_diff(utime.ticks_us(), start)
    utime.sleep_us(elapsed)


