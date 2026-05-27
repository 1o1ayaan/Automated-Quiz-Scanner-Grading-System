import os
import sys
import cv2
import numpy as np

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from bubble_reader import _find_bubble_region, _row_boundaries, _bubble_fill_score, OPTIONS, _upscale, PART1_COL_BOUNDS, PART1_PRESETS, PART2_COL_BOUNDS, PART2_PRESETS
from image_utils import load_image

def new_column_layout_quality(grid_img: np.ndarray, col_bounds: List[float], rows: List[tuple]) -> float:
    h, w = grid_img.shape[:2]
    total_diff = 0.0
    for y1, y2 in rows:
        y1c, y2c = max(0, y1 + 2), min(h, y2 - 2)
        scores = [
            _bubble_fill_score(grid_img[y1c:y2c, int(col_bounds[j] * w) : int(col_bounds[j + 1] * w)])
            for j in range(4)
        ]
        ordered = sorted(scores, reverse=True)
        total_diff += (ordered[0] - ordered[1])
    return total_diff

def calibrate_with_new_metric(grid_img, c0_min, c0_max, fallback, presets):
    rows = _row_boundaries(grid_img)
    candidates = [fallback] + [list(p) for p in presets]
    
    for c0 in np.arange(c0_min, c0_max, 0.005):
        for cw in np.arange(0.13, 0.22, 0.005):
            cols = [c0 + i * cw for i in range(5)]
            if cols[-1] > 0.92:
                continue
            candidates.append(cols)
            
    # Find best candidate using new metric
    best_cols = max(candidates, key=lambda c: new_column_layout_quality(grid_img, c, rows))
    return best_cols

def test_file(filepath):
    print("=" * 60)
    print(f"TESTING NEW METRIC FOR: {os.path.basename(filepath)}")
    print("=" * 60)
    img = load_image(filepath)
    img = _upscale(img)
    part1_grid, part2_grid = _find_bubble_region(img)
    
    p1_cols = calibrate_with_new_metric(part1_grid, 0.18, 0.28, PART1_COL_BOUNDS, PART1_PRESETS)
    p2_cols = calibrate_with_new_metric(part2_grid, 0.08, 0.16, PART2_COL_BOUNDS, PART2_PRESETS)
    
    print("Detected Part 1 columns:", [round(x, 3) for x in p1_cols])
    print("Detected Part 2 columns:", [round(x, 3) for x in p2_cols])
    
    # Read Part 1 with new columns
    h1, w1 = part1_grid.shape[:2]
    rows1 = _row_boundaries(part1_grid)
    print("\nPart 1 Answers Decided:")
    for i, qid in enumerate(["Q01", "Q02", "Q03", "Q04", "Q05", "Q06", "Q07", "Q08"]):
        y1, y2 = rows1[i]
        y1 = max(0, y1 + 2)
        y2 = min(h1, y2 - 2)
        scores = []
        for j in range(4):
            x1 = int(p1_cols[j] * w1)
            x2 = int(p1_cols[j + 1] * w1)
            cell = part1_grid[y1:y2, x1:x2]
            scores.append(_bubble_fill_score(cell))
        sorted_idx = sorted(range(4), key=lambda k: scores[k], reverse=True)
        top_i, second_i = sorted_idx[0], sorted_idx[1]
        top_score, second_score = scores[top_i], scores[second_i]
        
        ans = OPTIONS[top_i]
        if top_score < 12:
            ans = "-"
        elif second_score > 12 and (second_score / top_score) >= 0.82:
            ans = f"Multi:{OPTIONS[top_i]}/{OPTIONS[second_i]}"
        print(f"  {qid}: A={scores[0]:.0f}, B={scores[1]:.0f}, C={scores[2]:.0f}, D={scores[3]:.0f} -> Decided={ans}")

if __name__ == "__main__":
    test_file("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Abdurrehman.png")
