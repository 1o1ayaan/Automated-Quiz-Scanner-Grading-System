import os
import sys
import cv2
import numpy as np

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from image_utils import load_image

def find_table_contours(filepath):
    print("=" * 60)
    print(f"FINDING TABLE CONTOURS FOR: {os.path.basename(filepath)}")
    print("=" * 60)
    img = load_image(filepath)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Threshold to get binary image
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 8
    )
    
    # We want to find large rectangular contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Total external contours found: {len(contours)}")
    
    # Sort contours by area
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    # Find contours that are likely the two tables
    tables = []
    h_img, w_img = img.shape[:2]
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        aspect_ratio = float(w) / h if h > 0 else 0
        area_ratio = float(w * h) / (w_img * h_img)
        
        # The quiz tables are large and rectangular (aspect ratio around 0.6 to 1.2)
        if 0.5 <= aspect_ratio <= 1.5 and 0.03 <= area_ratio <= 0.20:
            print(f"Candidate table contour: x={x}, y={y}, w={w}, h={h}, aspect={aspect_ratio:.2f}, area_ratio={area_ratio:.3f}")
            tables.append((x, y, w, h))
            
    print(f"Found {len(tables)} tables.")

if __name__ == "__main__":
    find_table_contours("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Abdurrehman.png")
    find_table_contours("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Atif.png")
