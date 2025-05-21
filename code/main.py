import time
import utime
from machine import Pin, PWM
from random import random
import math

WAVE_TABLE_SIZE = 100
SAMPLE_RATE = 4000

keys = [
    {'note': 'C4', 'freq': 261, "on": False, "col":0, "row":0, "changed": False},
    {'note': 'Cs4', 'freq': 277, "on": False, "col":0, "row":1, "changed": False},
    {'note': 'D4', 'freq': 293, "on": False, "col":0, "row":2, "changed": False},
    {'note': 'Ds4', 'freq': 311, "on": False, "col":0, "row":3, "changed": False},
    {'note': 'E4', 'freq': 329, "on": False, "col":1, "row":0, "changed": False},
    {'note': 'F4', 'freq': 349, "on": False, "col":1, "row":1, "changed": False},
    {'note': 'Fs4', 'freq': 369, "on": False, "col":1, "row":2, "changed": False},
    {'note': 'G4', 'freq': 392, "on": False, "col":1, "row":3, "changed": False},
    {'note': 'Gs4', 'freq': 415, "on": False, "col":2, "row":0, "changed": False},
    {'note': 'A4', 'freq': 440, "on": False, "col":2, "row":1, "changed": False},
    {'note': 'As4', 'freq': 466, "on": False, "col":2, "row":2, "changed": False},
    {'note': 'B4', 'freq': 493, "on": False, "col":2, "row":3, "changed": False},
    {'note': 'C5', 'freq': 523, "on": False, "col":3, "row":0, "changed": False},
]

# row 0 is note 0,1,2,3
# row 1 is note 4,5,6,7
# row 2 is note 8,9,10,11
# row 3 is note 12,13,14,15

# col 0 is 0,4,8,12
# col 1 is 1,5,9,13
# col 2 is 2,6,10,14
# col 3 is 3,7,11,15


class Matrix:
    def __init__(self,row_pins, col_pins, keys):
        self.row_pins = [Pin(r, Pin.OUT) for r in row_pins]
        self.col_pins = [Pin(c, Pin.IN, Pin.PULL_UP) for c in col_pins]
        self.matrix = {}
        self.keys = keys
        for rr in range(len(row_pins)):
            self.matrix[rr] = {}
            for cc in range(len(col_pins)):
                #print(self.matrix)
                poss = [k for k in keys if k["row"]==rr and k["col"]==cc]
                if len(poss)==1: self.matrix[rr][cc] = poss[0]
    def scan(self):
        for row_index in self.matrix:
            for r in self.row_pins: r.value(1)
            self.row_pins[row_index].value(0)
            #print(f"setting row off")
            for col_index in self.matrix[row_index]:
                #print(f"scanning col {col_index}")
                self.matrix[row_index][col_index]["on"] = self.col_pins[col_index].value() == 0
        return self.keys


class PWMPlayer:
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin, Pin.OUT))
        self.pwm.freq(62500)
        self.pwm.duty_u16(0)
        self.on = True
        self.amp = 1.0
        self.index = 0
        self.tick = 0
        self.step = 0
        self.freq = 440.0
    def freq(self, freq):
        self.freq = freq
        self.step = freq * WAVE_TABLE_SIZE / SAMPLE_RATE


# setup

row_pins = [11,13,14,15,]
col_pins = [16,17,18,19,]
matrix = Matrix(row_pins, col_pins, keys)

pwm_pins = [8]  #,9,10,11,12,13]
channels = [PWMPlayer(pin) for pin in pwm_pins]  #6 channels

tick=0

while True:
    keys = matrix.scan()
    keys = [ k for k in keys if k["on"] ]
    print(keys)
    time.sleep(0.5)
    print (tick)
    tick=tick+1


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
    
    # get the keys
    keys = matrix.scan()[:]
    
    # get the keys which are on
    keys = [ keys[k] for k in keys if keys[k]["on"] ] # keys which are on
    
    # cycle through the channels
    for ch in channels:
    
        # give channel the frequency needed from key
        if len(keys)>0:
            test = keys.pop()
            ch.freq(test["freq"])
            if test["changed"]:
                ch.index = 0
                ch.tick = 0
            ch.on = True
        else:
            ch.on = False
            
        if ch.on:
            index = ch.index
            value = int(ch.amp * wave[int(index) % WAVE_TABLE_SIZE])
            ch.pwm.duty_u16(value)
            ch.index = ( index + ch.step ) % WAVE_TABLE_SIZE
            ch.tick = ch.tick + 1
        else:
            ch.pwm.duty_u16(0)

    elapsed = utime.ticks_diff(utime.ticks_us(), start)
    utime.sleep_us(elapsed)


