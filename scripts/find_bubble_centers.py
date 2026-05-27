import os
import sys
import cv2
import numpy as np

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from bubble_reader import _find_bubble_region, _upscale
from image_utils import load_image

def find_circles(filepath):
    print("=" * 60)
    print(f"FINDING BUBBLE CIRCLES FOR: {os.path.basename(filepath)}")
    print("=" * 60)
    img = load_image(filepath)
    img = _upscale(img)
    part1_grid, part2_grid = _find_bubble_region(img)
    
    for grid_idx, grid in enumerate([part1_grid, part2_grid]):
        gray = cv2.cvtColor(grid, cv2.COLOR_BGR2GRAY) if len(grid.shape) == 3 else grid
        h, w = gray.shape
        
        # Adaptive threshold to find circles
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 8
        )
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size and circularity
        centers = []
        for c in contours:
            x, y, cw, ch = cv2.boundingRect(c)
            aspect_ratio = float(cw) / ch if ch > 0 else 0
            # A bubble in upscaled image should be around 15-40 pixels in diameter
            if 15 <= cw <= 50 and 15 <= ch <= 50 and 0.8 <= aspect_ratio <= 1.2:
                # Calculate circularity
                area = cv2.contourArea(c)
                perimeter = cv2.arcLength(c, True)
                circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                if circularity > 0.4:
                    centers.append((x + cw // 2, y + ch // 2))
                    
        print(f"Part {grid_idx+1}: Found {len(centers)} circle-like contours.")
        if centers:
            # Let's cluster centers by X coordinate to find column alignments
            xs = [pt[0] for pt in centers]
            ys = [pt[1] for pt in centers]
            
            # Simple histogram of Xs to see where columns are
            hist, bin_edges = np.histogram(xs, bins=20, range=(0, w))
            print(f"Part {grid_idx+1} bubble X histogram bins:")
            for b in range(len(hist)):
                if hist[b] > 2:
                    print(f"  Bin {b} ({int(bin_edges[b])}-{int(bin_edges[b+1])}px): {hist[b]} bubbles")

if __name__ == "__main__":
    find_circles("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Abdurrehman.png")
    find_circles("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Atif.png")
