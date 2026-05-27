import os
import sys
import cv2
import numpy as np

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from bubble_reader import _find_bubble_region, _calibrate_column_bounds, _row_boundaries, _bubble_fill_score, OPTIONS, PART1_COL_BOUNDS, PART1_PRESETS, PART2_COL_BOUNDS, PART2_PRESETS, _upscale
from image_utils import load_image

def save_visualizations(filepath, out_prefix):
    img = load_image(filepath)
    img = _upscale(img)
    part1_grid, part2_grid = _find_bubble_region(img)
    
    part1_cols = _calibrate_column_bounds(part1_grid, 0.18, 0.28, PART1_COL_BOUNDS, PART1_PRESETS)
    part2_cols = _calibrate_column_bounds(part2_grid, 0.08, 0.16, PART2_COL_BOUNDS, PART2_PRESETS)
    
    # Draw Part 1 Grid
    vis1 = part1_grid.copy()
    h1, w1 = part1_grid.shape[:2]
    rows1 = _row_boundaries(part1_grid)
    for i, (y1, y2) in enumerate(rows1):
        cv2.line(vis1, (0, y1), (w1, y1), (0, 255, 0), 1)
        cv2.line(vis1, (0, y2), (w1, y2), (0, 255, 0), 1)
        for j in range(4):
            x1 = int(part1_cols[j] * w1)
            x2 = int(part1_cols[j + 1] * w1)
            cv2.rectangle(vis1, (x1, y1), (x2, y2), (255, 0, 0), 1)
            cell = part1_grid[y1:y2, x1:x2]
            score = _bubble_fill_score(cell)
            cv2.putText(vis1, f"{score:.0f}", (x1 + 5, y1 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            
    # Draw Part 2 Grid
    vis2 = part2_grid.copy()
    h2, w2 = part2_grid.shape[:2]
    rows2 = _row_boundaries(part2_grid)
    for i, (y1, y2) in enumerate(rows2):
        cv2.line(vis2, (0, y1), (w2, y1), (0, 255, 0), 1)
        cv2.line(vis2, (0, y2), (w2, y2), (0, 255, 0), 1)
        for j in range(4):
            x1 = int(part2_cols[j] * w2)
            x2 = int(part2_cols[j + 1] * w2)
            cv2.rectangle(vis2, (x1, y1), (x2, y2), (255, 0, 0), 1)
            cell = part2_grid[y1:y2, x1:x2]
            score = _bubble_fill_score(cell)
            cv2.putText(vis2, f"{score:.0f}", (x1 + 5, y1 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            
    os.makedirs("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/demo", exist_ok=True)
    cv2.imwrite(f"c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/demo/{out_prefix}_part1.png", vis1)
    cv2.imwrite(f"c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/demo/{out_prefix}_part2.png", vis2)
    print(f"Saved visualizations for {out_prefix}")

if __name__ == "__main__":
    save_visualizations("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Abdurrehman.png", "abdurrehman")
    save_visualizations("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Atif.png", "atif")
