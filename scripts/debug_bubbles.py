"""Debug bubble detection - saves annotated grid for tuning."""
import os
import sys

import cv2
import numpy as np

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, SRC)

from image_utils import crop_relative, load_image
from bubble_reader import _bubble_fill_score, DEFAULT_COL_BOUNDS, DEFAULT_HEADER_RATIO

SAMPLE = os.path.join(os.path.dirname(__file__), "..", "samples", "Ayan-sample.png")
OUT = os.path.join(os.path.dirname(__file__), "..", "demo", "bubble_debug.png")


def main():
    img = load_image(SAMPLE)
    img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    g = crop_relative(img, 0.025, 0.172, 0.485, 0.358)
    vis = g.copy()
    h, w = g.shape[:2]
    top = int(h * DEFAULT_HEADER_RATIO)
    body_h = h - top
    row_h = body_h / 8
    for i in range(8):
        y1 = top + int(i * row_h)
        y2 = top + int((i + 1) * row_h)
        cv2.line(vis, (0, y1), (w, y1), (0, 255, 0), 1)
        for j in range(4):
            x1 = int(DEFAULT_COL_BOUNDS[j] * w)
            x2 = int(DEFAULT_COL_BOUNDS[j + 1] * w)
            cv2.rectangle(vis, (x1, y1), (x2, y2), (255, 0, 0), 1)
            score = _bubble_fill_score(g[y1:y2, x1:x2])
            cv2.putText(
                vis,
                f"{score:.0f}",
                (x1 + 2, y1 + 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (0, 0, 255),
                1,
            )
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cv2.imwrite(OUT, vis)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
