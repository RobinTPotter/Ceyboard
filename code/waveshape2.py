import array, math

def rounded_square_wave(samples=64, round_frac=0.1, dip_frac=0.0):
    """Generate a square-like waveform with rounded edges and optional dip.
    
    samples: length of table (e.g. 64, 128)
    round_frac: fraction of half-cycle used for rounding (0.0–0.5)
    dip_frac: depth of dip in the plateau (0.0 = none, 0.5 = half dip)
    """
    wave = []
    half = samples // 2
    edge_len = max(1, int(round_frac * half))

    # First half (positive)
    for pos in range(half):
        if pos < edge_len:
            # rising edge (smooth curve 0 → +32767)
            t = pos / edge_len
            val = int(32767 * math.sin(t * math.pi / 2))
        elif pos >= half - edge_len:
            # falling edge (+32767 → 0)
            t = (pos - (half - edge_len)) / edge_len
            val = int(32767 * math.cos(t * math.pi / 2))
        else:
            # plateau, apply dip (sinusoidal dip across the flat region)
            flat_pos = pos - edge_len
            flat_len = half - 2 * edge_len
            dip = dip_frac * 32767 * math.sin(math.pi * flat_pos / flat_len)
            val = int(32767 - dip)
        wave.append(val)

    # Second half (negative mirror)
    for pos in range(half):
        wave.append(-wave[pos])

    return array.array("h", wave)

# Example waveforms
wave1 = rounded_square_wave(64, round_frac=0.1, dip_frac=0.0)  # soft square
wave2 = rounded_square_wave(64, round_frac=0.2, dip_frac=0.25) # hollow square
wave3 = rounded_square_wave(128, round_frac=0.05, dip_frac=0.5) # deep dip


