import os
import sys
import cv2
import numpy as np

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from bubble_reader import _find_bubble_region, _row_boundaries, _bubble_fill_score, OPTIONS, _upscale
from image_utils import load_image

def test_new_layout(filepath):
    print("=" * 60)
    print(f"TESTING NEW LAYOUT FOR: {os.path.basename(filepath)}")
    print("=" * 60)
    img = load_image(filepath)
    img = _upscale(img)
    part1_grid, part2_grid = _find_bubble_region(img)
    
    # Let's use the columns derived from vertical line detection:
    # label_separator is at ~0.245, right_border is at ~0.986
    part1_cols = [0.245, 0.430, 0.615, 0.801, 0.986]
    
    # For Part 2, let's see where the label separator and right border are.
    # From Atif.png Part 2, let's see if we can detect the lines.
    # Wait, let's see what columns work for Part 2 in Abdurrehman.png.
    # In Abdurrehman.png, the default calibration chose Part 2 columns: [0.085, 0.25, 0.415, 0.58, 0.745]
    # And Part 2 got 100% correct! So those default columns are excellent for Part 2.
    part2_cols = [0.085, 0.25, 0.415, 0.58, 0.745]

    h1, w1 = part1_grid.shape[:2]
    rows1 = _row_boundaries(part1_grid)
    print("\nPart 1 Bubble Scores with NEW columns:")
    for i, qid in enumerate(["Q01", "Q02", "Q03", "Q04", "Q05", "Q06", "Q07", "Q08"]):
        y1, y2 = rows1[i]
        y1 = max(0, y1 + 2)
        y2 = min(h1, y2 - 2)
        scores = []
        for j in range(4):
            x1 = int(part1_cols[j] * w1)
            x2 = int(part1_cols[j + 1] * w1)
            cell = part1_grid[y1:y2, x1:x2]
            scores.append(_bubble_fill_score(cell))
        
        # Calculate best option and clean decision
        sorted_idx = sorted(range(4), key=lambda k: scores[k], reverse=True)
        top_i, second_i = sorted_idx[0], sorted_idx[1]
        top_score, second_score = scores[top_i], scores[second_i]
        
        ans = OPTIONS[top_i]
        if top_score < 12:
            ans = "None"
        elif second_score > 12 and (second_score / top_score) >= 0.82:
            ans = f"Multi:{OPTIONS[top_i]}/{OPTIONS[second_i]}"
            
        print(f"  {qid}: A={scores[0]:.1f}, B={scores[1]:.1f}, C={scores[2]:.1f}, D={scores[3]:.1f} -> Decided={ans}")

if __name__ == "__main__":
    test_new_layout("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Abdurrehman.png")
