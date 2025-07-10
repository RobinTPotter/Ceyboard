from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
import array, math

WAVETABLE_SIZE = 64
SAMPLE_RATE = 22000
PHASE_BITS = 16

FREQS = [440, 550, 660, 880]  # A major chord
PINS = [0, 1]  # Left, Right

# Wave table: 16-bit sine wave
wavetable = array.array("H", [
    int(32767 + 32767 * math.sin(2 * math.pi * i / WAVETABLE_SIZE))
    for i in range(WAVETABLE_SIZE)
])

# PIO 16-bit PWM (same as before)
@asm_pio(out_init=(PIO.OUT_LOW,), out_shiftdir=PIO.SHIFT_RIGHT, autopull=True, pull_thresh=16)
def pwm_out():
    pull()
    mov(x, osr)
    mov(y, invert(x))
    set(pins, 1)
    label("high")
    jmp(x_dec, "high")
    set(pins, 0)
    label("low")
    jmp(y_dec, "low")

# Setup left/right PWM state machines
sm_left = StateMachine(0, pwm_out, freq=SAMPLE_RATE * 2, out_base=Pin(PINS[0]))
sm_right = StateMachine(1, pwm_out, freq=SAMPLE_RATE * 2, out_base=Pin(PINS[1]))

sm_left.active(1)
sm_right.active(1)

# Oscillator phases and steps
phases = [0] * 4
steps = [
    int(f * WAVETABLE_SIZE * (1 << PHASE_BITS) / SAMPLE_RATE)
    for f in FREQS
]

# Main synth loop
while True:
    # Get samples
    samples = []
    for i in range(4):
        idx = (phases[i] >> PHASE_BITS) % WAVETABLE_SIZE
        sample = wavetable[idx]
        phases[i] += steps[i]
        samples.append(sample)

    # Mix left = voice 0 + 1, right = voice 2 + 3
    left = (samples[0] + samples[1]) >> 1
    right = (samples[2] + samples[3]) >> 1

    sm_left.put(left)
    sm_right.put(right)

