import serial
import pygame.midi
pygame.midi.init()
import json

player = pygame.midi.Output(0)
player.set_instrument(0)


pico = serial.Serial("COM6", 115200, timeout=1)

while pico.readable():
    a = pico.readline()
    print(a)
    if len(a)>0:
        #print(a)
        data = f'{{ "data": {a.decode("utf-8").replace("'",'"').replace('\r\n','').replace("False","false").replace("True","true")}}}'
        #print(data)
        data = json.loads(data)["data"]
        print(data)
        for d in data:
            if d["on"]: player.note_on(d["midi"],127)
            elif not d["on"]: player.note_off(d["midi"],127)
