import array
import math
from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
import utime

# Number of samples in sine wave lookup table
SAMPLES = 32

# Create a sine lookup table with values scaled to 0..31 (5-bit PWM resolution)
sine_wave = array.array("H", [int(15 + 15 * math.sin(2 * math.pi * i / SAMPLES)) for i in range(SAMPLES)])

# PIO assembly for 5-bit PWM output on a pin using sideset
@asm_pio(sideset_init=PIO.OUT_LOW, out_init=PIO.OUT_LOW, out_shiftdir=PIO.SHIFT_LEFT)
def pwm_5bit():
    # This state machine outputs a PWM cycle on sideset pins with duty cycle from 'out' register.
    # 'out' contains 5-bit PWM duty cycle (0-31)
    # We count 32 cycles, sideset pin high for duty cycles, low otherwise.

    # out is 5 bits, counts from 31 down to 0
    pull(block)          # get duty cycle from FIFO
    mov(x, osr)          # move duty cycle to x
    mov(y, invert(x))    # y = 31 - x (to know how many low cycles)

    label("pwm_high")
    jmp(x_dec, "set_high")  # loop x times (duty cycle)

    jmp("pwm_low")         # jump to pwm low if duty cycle is 0

    label("set_high")
    nop().side(1)         # pin high for 1 cycle
    jmp("pwm_high")

    label("pwm_low")
    jmp(y_dec, "set_low")  # loop y times (off duty cycle)

    jmp("done")

    label("set_low")
    nop().side(0)         # pin low for 1 cycle
    jmp("pwm_low")

    label("done")
    nop().side(0)         # ensure pin low at end
    wrap()

# Setup StateMachine on Pin 15 (change as you want)
PIN_NUM = 15

sm = StateMachine(0, pwm_5bit, freq=20000, sideset_base=Pin(PIN_NUM))

# Start the state machine
sm.active(1)

# Feed sine wave samples continuously into FIFO
while True:
    for sample in sine_wave:
        sm.put(sample)
        utime.sleep_us(30)  # Adjust speed to change output frequency


