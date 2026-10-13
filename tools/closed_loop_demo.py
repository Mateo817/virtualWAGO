#!/usr/bin/env python3
"""Preset PWM stimulus -> pulse integrator -> raw AI/DI in the next input scan.

Not a PLC: this demo supplies preset stimulus and models the plant response.
Model assumptions: 0.01 mm/pulse, 1250 mm sensor span, start position 200 mm.
No inertia, backlash, missed steps, PWM edge phase or electrical effects.
"""
from fractions import Fraction
import json
from pathlib import Path
import sys
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prototype.vio import Rail, encode_ai466_standard, decode_pwm677_frq
ROOT = Path(__file__).resolve().parents[1]

def run():
    rail = Rail(json.loads((ROOT/"config/research-layout.json").read_text()))
    rail.run(True)
    position = Fraction(200)
    rows = []
    for cycle in range(40):
        frequency = 1000 if cycle < 25 else 0
        raw_pwm = bytes([1]) + frequency.to_bytes(2, "little") + bytes(9)
        # Caller supplies a pre-programmed test stimulus, NOT a controller.
        command = bytes(4) + raw_pwm
        sample = rail.cycle(command.hex())
        effective_pwm = bytes.fromhex(sample["effective_hex"])[4:16]
        actual_frequency = decode_pwm677_frq(effective_pwm)[0]
        position += Fraction(actual_frequency * 20_000_000, 1_000_000_000) * Fraction(1,100)
        rail.advance(20_000_000)
        current = 4000 + int(position * 16000 / 1250)
        raw_ai = encode_ai466_standard(current)
        # Explicit RESEARCH ordering: status0,word0LE,status1,word1LE.
        rail.set_input("analog", bytes([0]).hex()+raw_ai.to_bytes(2,"little").hex()+"000000")
        # Only this model's two limit bits, not a claim about real wiring order.
        limits = int(position <= 0) | (int(position >= 700) << 1)
        rail.set_input("limit_inputs", limits.to_bytes(2,"little").hex())
        rows.append({"sample": sample, "position_mm": str(position),
                     "new_sensor_word": raw_ai,
                     "evidence_scope": "preset-stimulus-and-plant-only-NOT-PLC-execution"})
    return rows

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
