import cv2
import os
import sys
import numpy as np

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from bubble_reader import _find_bubble_region, _upscale
from image_utils import load_image

def detect_vertical_lines(filepath):
    print("=" * 60)
    print(f"VERTICAL LINE DETECTION FOR: {os.path.basename(filepath)}")
    print("=" * 60)
    img = load_image(filepath)
    img = _upscale(img)
    part1_grid, part2_grid = _find_bubble_region(img)
    
    for idx, grid_img in enumerate([part1_grid, part2_grid]):
        gray = cv2.cvtColor(grid_img, cv2.COLOR_BGR2GRAY) if len(grid_img.shape) == 3 else grid_img
        h, w = gray.shape
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 8
        )
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(h // 3, 40)))
        vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        projection = np.sum(vertical, axis=0)

        threshold = h * 0.30 * 255
        clusters = []
        for x, value in enumerate(projection):
            if value < threshold:
                continue
            if not clusters or x - clusters[-1][-1] > 10:
                clusters.append([x])
            else:
                clusters[-1].append(x)

        lines = [int(np.mean(cluster)) for cluster in clusters]
        print(f"Part {idx+1} detected vertical lines (absolute pixels):", lines)
        print(f"Part {idx+1} detected vertical lines (relative ratios):", [round(x / w, 3) for x in lines])

if __name__ == "__main__":
    detect_vertical_lines("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Abdurrehman.png")
    detect_vertical_lines("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Atif.png")
