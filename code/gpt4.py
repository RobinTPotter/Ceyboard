import board
import digitalio
import audiopwmio
import synthio
import time

# ----------------------------
# Keyboard matrix setup
# ----------------------------
ROW_PINS = [board.GP6, board.GP7, board.GP8, board.GP9]
COL_PINS = [board.GP10, board.GP11, board.GP12, board.GP13, board.GP14]

KEY_FREQS = [
    [261.63, 293.66, 329.63, 349.23, 392.00],
    [440.00, 493.88, 523.25, 587.33, 659.25],
    [698.46, 783.99, 880.00, 987.77, 1046.5],
    [1174.7, 1318.5, 1396.9, 1568.0, 1760.0],
]

row_pins = []
for p in ROW_PINS:
    pin = digitalio.DigitalInOut(p)
    pin.switch_to_output(value=True)
    row_pins.append(pin)

col_pins = []
for p in COL_PINS:
    pin = digitalio.DigitalInOut(p)
    pin.switch_to_input(pull=digitalio.Pull.UP)
    col_pins.append(pin)

# ----------------------------
# SynthIO setup
# ----------------------------
audio = audiopwmio.PWMAudioOut(board.GP0)
synth = synthio.Synthesizer(sample_rate=8000)
synth.level = 0.8
audio.play(synth)

default_env = synthio.Envelope(
    attack_time=0.05,
    decay_time=0.1,
    release_time=0.3,
    sustain_level=0.7,
)

# Keep track of active notes
active_notes = {}

# ----------------------------
# Configurable polyphony limit
# ----------------------------
MAX_POLYPHONY = 4   # change this number to set the limit

# ----------------------------
# Matrix scanning
# ----------------------------
def scan_matrix():
    pressed = []
    for r_index, r_pin in enumerate(row_pins):
        for rp in row_pins:
            rp.value = True
        r_pin.value = False
        for c_index, c_pin in enumerate(col_pins):
            if not c_pin.value:
                pressed.append((r_index, c_index))
    return pressed

# ----------------------------
# Main loop
# ----------------------------
while True:
    pressed_keys = scan_matrix()

    # Enforce polyphony limit: only use first N keys
    limited_keys = pressed_keys[:MAX_POLYPHONY]

    # Handle newly pressed notes
    for r, c in limited_keys:
        freq = KEY_FREQS[r][c]
        if freq not in active_notes:
            note = synthio.Note(frequency=freq, envelope=default_env)
            synth.press(note)
            active_notes[freq] = note

    # Handle released notes
    for freq in list(active_notes.keys()):
        still_pressed = any(KEY_FREQS[r][c] == freq for r, c in limited_keys)
        if not still_pressed:
            synth.release(active_notes[freq])
            del active_notes[freq]

    time.sleep(0.01)


