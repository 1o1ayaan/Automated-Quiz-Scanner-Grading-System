import os
import sys
import cv2
import numpy as np

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from bubble_reader import _find_bubble_region, _detect_horizontal_lines, _row_boundaries, _upscale
from image_utils import load_image

def inspect(filepath):
    print("=" * 60)
    print(f"INSPECTING LINES FOR: {os.path.basename(filepath)}")
    print("=" * 60)
    img = load_image(filepath)
    img = _upscale(img)
    part1_grid, part2_grid = _find_bubble_region(img)
    
    lines1 = _detect_horizontal_lines(part1_grid)
    lines2 = _detect_horizontal_lines(part2_grid)
    
    print("Part 1 detected lines:", lines1)
    print("Part 1 rows derived:", _row_boundaries(part1_grid))
    
    print("\nPart 2 detected lines:", lines2)
    print("Part 2 rows derived:", _row_boundaries(part2_grid))

if __name__ == "__main__":
    inspect("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Abdurrehman.png")
