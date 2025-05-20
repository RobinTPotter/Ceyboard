import time
import utime
from machine import Pin, PWM
from random import random
import math

keys = {
    0: {'note': 'C4', 'freq': 261, "on": False},
    1: {'note': 'Cs4', 'freq': 277, "on": False},
    2: {'note': 'D4', 'freq': 293, "on": False},
    3: {'note': 'Ds4', 'freq': 311, "on": False},
    4: {'note': 'E4', 'freq': 329, "on": False},
    5: {'note': 'F4', 'freq': 349, "on": False},
    6: {'note': 'Fs4', 'freq': 369, "on": False},
    7: {'note': 'G4', 'freq': 392, "on": False},
    8: {'note': 'Gs4', 'freq': 415, "on": False},
    9: {'note': 'A4', 'freq': 440, "on": False},
    10: {'note': 'As4', 'freq': 466, "on": False},
    11: {'note': 'B4', 'freq': 493, "on": False},
    12: {'note': 'C5', 'freq': 523, "on": False}
}

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
                index = cc+rr*4
                self.matrix[rr][cc] = keys[index]
    def scan(self):
        for row_index in self.matrix:
            for r in self.row_pins: r.value(1)
            self.row_pins[row_index].value(0)
            print(f"setting row off")
            for col_index in self.matrix[row_index]:
                print(f"scanning col {col_index}")
                if self.col_pins[col_index] == 0:
                    self.matrix[row_index][col_index][on] = True
                    print(f"setting ON {row_index} {col_index} {self.matrix[row_index][col_index]}")


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


# setup

row_pins = [0,1,2,3]
col_pins = [4,5,6,7]
matrix = Matrix(row_pins, col_pins, keys)

pwm_pins = [8,9,10,11,12,13]
channels = [PWMPlayer(pin) for pin in pwm_pins]  #6 channels



#ff = 440.0
#for i,ch in enumerate(channels):
#    ch.freq(440 * (5+i)/5)

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


