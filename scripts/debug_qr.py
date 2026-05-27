import cv2
import os
import sys
from pyzbar import pyzbar

def test_qr(img_path):
    print(f"Testing {img_path}")
    img_orig = cv2.imread(img_path)
    if img_orig is None:
        print("Could not read image!")
        return

    # Try different sizes
    for size in [1200, 1600, 2000, 2400, 3000, None]:
        if size is not None:
            h, w = img_orig.shape[:2]
            scale = size / max(h, w)
            img = cv2.resize(img_orig, (int(w * scale), int(int(h * scale))))
        else:
            img = img_orig.copy()
            
        h, w = img.shape[:2]
        print(f"Trying size: {w}x{h}")
        
        # Try full image and crop at different angles
        # Crop region for QR (top right)
        crops = [
            img, 
            img[0 : int(h * 0.35), int(w * 0.55) : w]
        ]
        
        for crop_idx, c in enumerate(crops):
            for angle in (0, 90, 180, 270):
                if angle == 90:
                    r = cv2.rotate(c, cv2.ROTATE_90_CLOCKWISE)
                elif angle == 180:
                    r = cv2.rotate(c, cv2.ROTATE_180)
                elif angle == 270:
                    r = cv2.rotate(c, cv2.ROTATE_90_COUNTERCLOCKWISE)
                else:
                    r = c.copy()
                    
                gray = cv2.cvtColor(r, cv2.COLOR_BGR2GRAY) if len(r.shape) == 3 else r
                
                # Check different thresholds
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                variants = [
                    gray,
                    clahe.apply(gray),
                    cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
                    cv2.adaptiveThreshold(cv2.GaussianBlur(gray, (3, 3), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10),
                    # Extra threshold: adaptive threshold with different block sizes
                    cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 51, 15),
                    cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 51, 15)
                ]
                
                for var_idx, variant in enumerate(variants):
                    codes = pyzbar.decode(variant)
                    if codes:
                        print(f"SUCCESS! size={size}, crop={crop_idx}, angle={angle}, variant={var_idx}")
                        print("Payload:", codes[0].data.decode('utf-8'))
                        return

    print("ALL COMBINATIONS FAILED!")

if __name__ == "__main__":
    test_qr("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Hamza.png")
