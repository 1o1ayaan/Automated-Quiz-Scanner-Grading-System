import os
import sys
import cv2
import numpy as np

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from bubble_reader import _find_bubble_region, _row_boundaries, _bubble_fill_score, OPTIONS, _upscale, PART1_COL_BOUNDS, PART1_PRESETS, PART2_COL_BOUNDS, PART2_PRESETS
from image_utils import load_image

def narrow_calibrate_column_bounds(
    grid_img: np.ndarray,
    c0_min: float,
    c0_max: float,
    cw_min: float,
    cw_max: float,
    fallback: List[float],
    presets: List[List[float]],
) -> List[float]:
    rows = _row_boundaries(grid_img)
    candidates = [fallback] + [list(p) for p in presets]

    for c0 in np.arange(c0_min, c0_max + 0.001, 0.005):
        for cw in np.arange(cw_min, cw_max + 0.001, 0.005):
            cols = [c0 + i * cw for i in range(5)]
            if cols[-1] > 0.95:
                continue
            candidates.append(cols)

    # Let's score layouts using a hybrid quality function
    def score_layout(col_bounds):
        h, w = grid_img.shape[:2]
        clear_rows = 0
        total_contrast = 0.0
        
        for y1, y2 in rows:
            y1c, y2c = max(0, y1 + 2), min(h, y2 - 2)
            scores = [
                _bubble_fill_score(grid_img[y1c:y2c, int(col_bounds[j] * w) : int(col_bounds[j + 1] * w)])
                for j in range(4)
            ]
            ordered = sorted(scores, reverse=True)
            top, second = ordered[0], ordered[1]
            
            # Penalize layouts where Column A gets high scores on all rows due to label bleeding
            # If top is in column A, and its score is moderate (~40-80), we don't count it as a clean row
            if top >= 12:
                contrast = top - second
                total_contrast += contrast
                if contrast >= 10:
                    clear_rows += 1
                    
        return clear_rows * 100 + total_contrast

    return max(candidates, key=score_layout)

def test_file(filepath):
    print("=" * 60)
    print(f"TESTING NARROW CALIBRATION FOR: {os.path.basename(filepath)}")
    print("=" * 60)
    img = load_image(filepath)
    img = _upscale(img)
    part1_grid, part2_grid = _find_bubble_region(img)
    
    rows1 = _row_boundaries(part1_grid)
    rows2 = _row_boundaries(part2_grid)
    
    # We restrict Part 1 search to close to [0.205, 0.375, 0.545, 0.715, 0.885]
    p1_cols = narrow_calibrate_column_bounds(
        part1_grid, 
        c0_min=0.20, c0_max=0.23, 
        cw_min=0.165, cw_max=0.175,
        fallback=PART1_COL_BOUNDS, 
        presets=PART1_PRESETS
    )
    
    # We restrict Part 2 search to close to [0.085, 0.25, 0.415, 0.58, 0.745]
    p2_cols = narrow_calibrate_column_bounds(
        part2_grid, 
        c0_min=0.07, c0_max=0.11, 
        cw_min=0.160, cw_max=0.170,
        fallback=PART2_COL_BOUNDS, 
        presets=[[0.085, 0.25, 0.415, 0.58, 0.745], [0.10, 0.245, 0.39, 0.535, 0.68]]
    )
    
    print(f"Part 1 cols: {[round(x, 3) for x in p1_cols]}")
    print(f"Part 2 cols: {[round(x, 3) for x in p2_cols]}")
    
    # Read Part 1 Answers
    h1, w1 = part1_grid.shape[:2]
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

    # Read Part 2 Answers
    h2, w2 = part2_grid.shape[:2]
    print("\nPart 2 Answers Decided:")
    for i, qid in enumerate(["Q01", "Q02", "Q03", "Q04", "Q05", "Q06", "Q07", "Q08"]):
        y1, y2 = rows2[i]
        y1 = max(0, y1 + 2)
        y2 = min(h2, y2 - 2)
        scores = []
        for j in range(4):
            x1 = int(p2_cols[j] * w2)
            x2 = int(p2_cols[j + 1] * w2)
            cell = part2_grid[y1:y2, x1:x2]
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
    test_file("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Atif.png")
