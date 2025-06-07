import time
import utime
from machine import Pin, PWM
from random import random
import math

WAVE_TABLE_SIZE = 512
SAMPLE_RATE = 1800 # can 5 with current code

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
                check = self.matrix[row_index][col_index]["on"]
                self.matrix[row_index][col_index]["on"] = self.col_pins[col_index].value() == 0
                if self.matrix[row_index][col_index]["on"] != check: self.matrix[row_index][col_index]["changed"] = True
                else: self.matrix[row_index][col_index]["changed"] = False
        return self.keys


class PWMPlayer:
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin, Pin.OUT))
        self.pwm.freq(62500)
        self.pwm.duty_u16(0)
        self.on = True
        self.amp = 0.05
        self.index = 0
        self.tick = 0
        self.step = 0
        self._freq = 440.0
    def set_freq(self, freq):
        self._freq = freq
        self.step = self._freq * WAVE_TABLE_SIZE / SAMPLE_RATE


# setup

row_pins = [11,13,14,15,]
col_pins = [16,17,18,19,]
matrix = Matrix(row_pins, col_pins, keys)

pwm_pins = [0,1,2,3]#,1,2]  #,9,10,11,12,13]
channels = [PWMPlayer(pin) for pin in pwm_pins]  #6 channels
print (channels)
utime.sleep_us(100000)

tick=0

# generate wave table
wave = [
    int( 65535 * (1 + math.sin(2 * math.pi * i/WAVE_TABLE_SIZE) ) / 2 ) for i in range(WAVE_TABLE_SIZE)
]

interval_ms = 1000000 / SAMPLE_RATE

#for _ in range(3 * SAMPLE_RATE):
while True:



    start_time = utime.ticks_us()
    
    tick +=1

    tick = tick % 100

    # get the keys
    if tick == 0: 
        keys = matrix.scan() #[:]
        #print(keys)
        # get the keys which are on
        keys =[ k for k in keys if k["on"] ] # keys which are on
        #print(keys)
        for ch in channels:
            # give channel the frequency needed from key
            if len(keys)>0:
                test = keys.pop()
                ch.set_freq(test["freq"])
                if test["changed"]:
                    ch.index = 0
                    ch.tick = 0
                ch.on = True
            else:
                ch.on = False
            
    # cycle through the channels
    for ch in channels:
        if ch.on:
            index = ch.index
            value = int(ch.amp * wave[int(index) % WAVE_TABLE_SIZE])
            ch.pwm.duty_u16(value)
            ch.index = ( index + ch.step ) % WAVE_TABLE_SIZE
            ch.tick = ch.tick + 1
        else:
            ch.pwm.duty_u16(0)

    elapsed = utime.ticks_diff(utime.ticks_us(), start_time)
    delay = int(interval_ms - elapsed)
    if delay > 0:
        utime.sleep_us(delay)
    else:
        if tick==1: print(str(delay) + "!")


