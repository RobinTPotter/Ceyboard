import array, math

def rounded_square_wave(samples=64, round_frac=0.1, dip_frac=0.0):
    """Generate a square-like waveform with rounded edges and optional dip.
    
    samples: length of table (e.g. 64, 128)
    round_frac: fraction of samples used for each edge (0.0–0.5)
    dip_frac: fraction of dip applied on the flat (0.0 = none, 0.5 = half dip)
    """
    wave = []
    half = samples // 2
    edge_len = max(1, int(round_frac * half))

    for i in range(samples):
        pos = i % samples
        if pos < half:
            # "high" half
            if pos < edge_len:
                # rising edge (rounded)
                t = pos / edge_len
                val = int(32767 * math.sin(t * math.pi / 2))  # 0→+32767
            elif pos >= half - edge_len:
                # falling edge (rounded)
                t = (pos - (half - edge_len)) / edge_len
                val = int(32767 * math.cos(t * math.pi / 2))  # +32767→0
            else:
                # flat high with optional dip
                center_offset = (dip_frac * 32767) * math.sin(
                    (pos - edge_len) / (half - 2 * edge_len) * math.pi
                )
                val = int(32767 - center_offset)
        else:
            # "low" half (mirror inverted)
            val = -rounded_square_wave(samples, round_frac, dip_frac)[pos - half]
        wave.append(val)

    return array.array("h", wave)

# Example usage
waveform = rounded_square_wave(samples=64, round_frac=0.15, dip_frac=0.25)

