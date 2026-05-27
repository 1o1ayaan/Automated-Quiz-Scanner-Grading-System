import os
import sys

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from qr_decoder import decode_answer_key
from image_utils import load_image

def check():
    samples_dir = "c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples"
    for fname in sorted(os.listdir(samples_dir)):
        if not fname.lower().endswith(".png"):
            continue
        path = os.path.join(samples_dir, fname)
        try:
            # Let's see what rotation decode_answer_key finds.
            # We can print the raw payload which contains "[decoded at ...]"
            key = decode_answer_key(path)
            print(f"{fname}: {key.quiz_identifier} | Set: {key.set_identifier} | Raw: {key.raw_payload}")
        except Exception as e:
            print(f"{fname}: Failed to decode QR: {e}")

if __name__ == "__main__":
    check()
