"""Shared image loading and preprocessing utilities."""
from __future__ import annotations

import os
from typing import List, Tuple

import cv2
import numpy as np

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def load_image(path: str) -> np.ndarray:
    """Load an image from disk; supports PDF first page via optional pdf2image."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        try:
            from pdf2image import convert_from_path

            pages = convert_from_path(path, first_page=1, last_page=1, dpi=200)
            if not pages:
                raise ValueError(f"No pages found in PDF: {path}")
            rgb = np.array(pages[0])
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        except ImportError as exc:
            raise ImportError(
                "PDF support requires pdf2image and poppler. "
                "Install: pip install pdf2image"
            ) from exc

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Could not read image: {path}")
    return img


def load_image_from_bytes(data: bytes, filename: str = "upload.png") -> np.ndarray:
    """Decode image from uploaded bytes."""
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        try:
            return load_image(tmp_path)
        finally:
            os.unlink(tmp_path)

    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode uploaded image")
    return img


def resize_max_dimension(img: np.ndarray, max_dim: int = 2000) -> np.ndarray:
    h, w = img.shape[:2]
    scale = min(1.0, max_dim / max(h, w))
    if scale >= 1.0:
        return img
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def rotate_image(img: np.ndarray, angle: int) -> np.ndarray:
    if angle == 0:
        return img
    if angle == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if angle == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    if angle == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    raise ValueError(f"Unsupported rotation angle: {angle}")


def enhance_for_qr(gray: np.ndarray) -> List[np.ndarray]:
    """Return multiple preprocessed variants to improve QR detection."""
    variants = [gray]
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    variants.append(clahe.apply(gray))
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(otsu)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    adaptive = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
    )
    variants.append(adaptive)
    # Extra robust adaptive thresholding variants for diverse scanner contrasts
    variants.append(cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 51, 15))
    variants.append(cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 51, 15))
    return variants


def crop_relative(img: np.ndarray, x1: float, y1: float, x2: float, y2: float) -> np.ndarray:
    h, w = img.shape[:2]
    xa, ya = int(x1 * w), int(y1 * h)
    xb, yb = int(x2 * w), int(y2 * h)
    return img[ya:yb, xa:xb].copy()
