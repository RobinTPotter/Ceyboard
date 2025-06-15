import time
import utime
from machine import Pin, PWM
from random import random
import math

WAVE_TABLE_SIZE = 512
SAMPLE_RATE = 1800 # can 5 with current code

keys = [ 
    { "midi": 64, "note": "C4",  "freq": 261, "on": False, "col":0, "row":0, "changed": False},
    { "midi": 65, "note": "Cs4", "freq": 277, "on": False, "col":0, "row":1, "changed": False},
    { "midi": 66, "note": "D4",  "freq": 293, "on": False, "col":0, "row":2, "changed": False},
    { "midi": 67, "note": "Ds4", "freq": 311, "on": False, "col":0, "row":3, "changed": False},
    { "midi": 68, "note": "E4",  "freq": 329, "on": False, "col":1, "row":0, "changed": False},
    { "midi": 69, "note": "F4",  "freq": 349, "on": False, "col":1, "row":1, "changed": False},
    { "midi": 70, "note": "Fs4", "freq": 369, "on": False, "col":1, "row":2, "changed": False},
    { "midi": 71, "note": "G4",  "freq": 392, "on": False, "col":1, "row":3, "changed": False},
    { "midi": 72, "note": "Gs4", "freq": 415, "on": False, "col":2, "row":0, "changed": False},
    { "midi": 73, "note": "A4",  "freq": 440, "on": False, "col":2, "row":1, "changed": False},
    { "midi": 74, "note": "As4", "freq": 466, "on": False, "col":2, "row":2, "changed": False},
    { "midi": 75, "note": "B4",  "freq": 493, "on": False, "col":2, "row":3, "changed": False},
    { "midi": 76, "note": "C5",  "freq": 523, "on": False, "col":3, "row":0, "changed": False},
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
        self.matrix = { }
        self.keys = keys
        for rr in range(len(row_pins)):
            self.matrix[rr] = { }
            for cc in range(len(col_pins)):
                #print(self.matrix)
                poss = [k for k in keys if k["row"]==rr and k["col"]==cc]
                if len(poss)==1: self.matrix[rr][cc] = poss[0]
    def scan(self):
        output = []
        for row_index in self.matrix:
            for r in self.row_pins: r.value(1)
            self.row_pins[row_index].value(0)
            #print(f"setting row off")
            for col_index in self.matrix[row_index]:
                #print(f"scanning col { "midi": 64, col_index}")
                check = self.matrix[row_index][col_index]["on"]
                self.matrix[row_index][col_index]["on"] = self.col_pins[col_index].value() == 0
                if self.matrix[row_index][col_index]["on"] != check: self.matrix[row_index][col_index]["changed"] = True
                else: self.matrix[row_index][col_index]["changed"] = False
                if self.matrix[row_index][col_index]["changed"]:
                    output.append(self.matrix[row_index][col_index])
        return output


row_pins = [11,13,14,15,]
col_pins = [16,17,18,19,]
matrix = Matrix(row_pins, col_pins, keys)


while True:
    keys = matrix.scan()
    if len(keys)>0: print(keys)
    time.sleep(0.1)
