import os
import sys
import cv2
import numpy as np

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from bubble_reader import _find_bubble_region, _calibrate_column_bounds, _row_boundaries, _bubble_fill_score, OPTIONS, PART1_COL_BOUNDS, PART1_PRESETS, PART2_COL_BOUNDS, PART2_PRESETS, _upscale
from image_utils import load_image

def debug_bubbles_for_file(filepath):
    print("=" * 60)
    print(f"DEBUGGING BUBBLES FOR: {os.path.basename(filepath)}")
    print("=" * 60)
    img = load_image(filepath)
    img = _upscale(img)
    part1_grid, part2_grid = _find_bubble_region(img)
    
    part1_cols = _calibrate_column_bounds(part1_grid, 0.18, 0.28, PART1_COL_BOUNDS, PART1_PRESETS)
    part2_cols = _calibrate_column_bounds(part2_grid, 0.08, 0.16, PART2_COL_BOUNDS, PART2_PRESETS)
    
    print("Part 1 columns:", [round(x, 3) for x in part1_cols])
    print("Part 2 columns:", [round(x, 3) for x in part2_cols])
    
    h1, w1 = part1_grid.shape[:2]
    rows1 = _row_boundaries(part1_grid)
    print("\nPart 1 Bubble Scores:")
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
        print(f"  {qid}: A={scores[0]:.1f}, B={scores[1]:.1f}, C={scores[2]:.1f}, D={scores[3]:.1f} -> Best={OPTIONS[np.argmax(scores)]}")

    h2, w2 = part2_grid.shape[:2]
    rows2 = _row_boundaries(part2_grid)
    print("\nPart 2 Bubble Scores:")
    for i, qid in enumerate(["Q01", "Q02", "Q03", "Q04", "Q05", "Q06", "Q07", "Q08"]):
        y1, y2 = rows2[i]
        y1 = max(0, y1 + 2)
        y2 = min(h2, y2 - 2)
        scores = []
        for j in range(4):
            x1 = int(part2_cols[j] * w2)
            x2 = int(part2_cols[j + 1] * w2)
            cell = part2_grid[y1:y2, x1:x2]
            scores.append(_bubble_fill_score(cell))
        print(f"  {qid}: A={scores[0]:.1f}, B={scores[1]:.1f}, C={scores[2]:.1f}, D={scores[3]:.1f} -> Best={OPTIONS[np.argmax(scores)]}")

if __name__ == "__main__":
    debug_bubbles_for_file("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Abdurrehman.png")
