from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
import array, math

# ---------------------------
# Audio constants
# ---------------------------
WAVETABLE_SIZE = 64
SAMPLE_RATE = 8000
PHASE_BITS = 16
PINS = [0, 1]   # left / right PWM pins

# ---------------------------
# Keyboard matrix setup
# ---------------------------
ROW_PINS = [6, 7, 8, 9]         # example row pins
COL_PINS = [10, 11, 12, 13, 14] # example col pins

# Frequencies for each key position (matrix[r][c])
KEY_FREQS = [
    [261.63, 293.66, 329.63, 349.23, 392.00],  # Row 0
    [440.00, 493.88, 523.25, 587.33, 659.25],  # Row 1
    [698.46, 783.99, 880.00, 987.77, 1046.5],  # Row 2
    [1174.7, 1318.5, 1396.9, 1568.0, 1760.0],  # Row 3
]

row_pins = [Pin(p, Pin.OUT) for p in ROW_PINS]
col_pins = [Pin(p, Pin.IN, Pin.PULL_UP) for p in COL_PINS]

# ---------------------------
# Build sine wavetable
# ---------------------------
wavetable = array.array(
    "H",
    [int(32767 + 32767 * math.sin(2 * math.pi * i / WAVETABLE_SIZE))
     for i in range(WAVETABLE_SIZE)]
)

# ---------------------------
# PIO for 16-bit PWM
# ---------------------------
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

sm_left  = StateMachine(0, pwm_out, freq=SAMPLE_RATE * 2, out_base=Pin(PINS[0]))
sm_right = StateMachine(1, pwm_out, freq=SAMPLE_RATE * 2, out_base=Pin(PINS[1]))
sm_left.active(1)
sm_right.active(1)

# ---------------------------
# Synth state
# ---------------------------
phases = [0] * 4
steps  = [0] * 4  # phase increments

# ---------------------------
# Matrix scan
# ---------------------------
def scan_matrix():
    """Scan the keyboard matrix, return list of (freq) for pressed keys."""
    pressed = []
    for r_index, r_pin in enumerate(row_pins):
        # Set all rows high, then pull current row low
        for rp in row_pins:
            rp.value(1)
        r_pin.value(0)

        # Read each column
        for c_index, c_pin in enumerate(col_pins):
            if c_pin.value() == 0:  # active low
                pressed.append(KEY_FREQS[r_index][c_index])
    return pressed

def update_steps_from_pressed(pressed):
    """Update steps[] from list of pressed freqs (up to first 4)."""
    global steps
    for i in range(4):
        if i < len(pressed):
            f = pressed[i]
            steps[i] = int(f * WAVETABLE_SIZE * (1 << PHASE_BITS) / SAMPLE_RATE)
        else:
            steps[i] = 0  # silence

# ---------------------------
# Main loop
# ---------------------------
scan_interval = 8          # scan every 8 samples (~1ms)
scan_counter = 0

while True:
    # --- Periodic matrix scan ---
    if scan_counter == 0:
        pressed_freqs = scan_matrix()
        update_steps_from_pressed(pressed_freqs)
    scan_counter = (scan_counter + 1) % scan_interval

    # --- Generate 4 voices ---
    s = [0, 0, 0, 0]
    for i in range(4):
        if steps[i] != 0:
            idx = (phases[i] >> PHASE_BITS) & (WAVETABLE_SIZE - 1)
            s[i] = wavetable[idx]
            phases[i] += steps[i]
        else:
            s[i] = 32767  # midpoint (silence)

    # Mix: left = voices 0+1, right = voices 2+3
    left  = (s[0] + s[1]) >> 1
    right = (s[2] + s[3]) >> 1

    sm_left.put(left)
    sm_right.put(right)


