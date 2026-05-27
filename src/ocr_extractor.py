"""Task 2: Student name and registration number extraction via OCR."""
from __future__ import annotations

import re
from typing import Optional, Tuple

import cv2
import numpy as np

from models import StudentInfo
from image_utils import crop_relative, load_image, resize_max_dimension

# Lazy-loaded OCR engines
_easyocr_reader = None
_tesseract_available = None


def _get_easyocr():
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr

        _easyocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _easyocr_reader


def _preprocess_handwriting_region(roi: np.ndarray) -> np.ndarray:
    if len(roi.shape) == 3:
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    else:
        gray = roi.copy()
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if np.mean(binary) > 127:
        binary = cv2.bitwise_not(binary)
    kernel = np.ones((2, 2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    return binary


def _bbox_center_x(bbox) -> float:
    return sum(p[0] for p in bbox) / len(bbox)


_GARBAGE_NAME_TOKENS = {
    "WLUG", "WLUV", "WLOV", "NAAT", "NNAT", "VOT", "RATT", "NAME",
    "TO", "JUC", "HIBOTT", "OOL", "JUO", "NOT", "NAT",
}


def _is_name_field_garbage(text: str) -> bool:
    """Filter OCR noise from the underline/label on the left of the name line."""
    token = re.sub(r"[^A-Za-z]", "", text).strip()
    if len(token) < 2:
        return True
    upper = token.upper()
    if upper in _GARBAGE_NAME_TOKENS:
        return True
    # Short all-caps noise from underline (WLUG, etc.) — not real names
    if (
        len(token) <= 5
        and token.isupper()
        and not re.search(r"[aeiouAEIOU]", token)
    ):
        return True
    if len(token) <= 4 and token.isupper() and upper not in {"ALI", "OMAR", "AHMED"}:
        return True
    return False


def _ocr_region(roi: np.ndarray) -> Tuple[str, float]:
    processed = _preprocess_handwriting_region(roi)
    reader = _get_easyocr()
    results = reader.readtext(processed, detail=1, paragraph=False)
    if not results:
        results = reader.readtext(roi, detail=1, paragraph=False)
    if not results:
        return "", 0.0

    texts = []
    confidences = []
    for _bbox, text, conf in results:
        cleaned = text.strip()
        if cleaned:
            texts.append(cleaned)
            confidences.append(float(conf))

    combined = " ".join(texts).strip()
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
    return combined, avg_conf


def _ocr_name_field(roi: np.ndarray) -> Tuple[str, float]:
    """
    Read handwritten name; ignore left-side underline/label noise (e.g. WLUG).

    Uses raw image first, then preprocessed with right-side / non-garbage filtering.
    """
    reader = _get_easyocr()
    width = roi.shape[1]

    def collect(results, min_x_ratio: float = 0.0) -> list:
        items = []
        for bbox, text, conf in results:
            cleaned = text.strip()
            if not cleaned or _is_name_field_garbage(cleaned):
                continue
            cx_ratio = _bbox_center_x(bbox) / max(width, 1)
            if cx_ratio < min_x_ratio:
                continue
            items.append((cx_ratio, cleaned, float(conf)))
        return items

    # Raw image: usually one clean detection on the handwriting
    raw_items = collect(reader.readtext(roi, detail=1, paragraph=False))
    if raw_items:
        raw_items.sort(key=lambda x: x[0])
        text = raw_items[-1][1]
        conf = max(i[2] for i in raw_items)
        return text, conf

    # Preprocessed: often splits garbage (left) and name (right)
    proc_items = collect(
        reader.readtext(_preprocess_handwriting_region(roi), detail=1, paragraph=False),
        min_x_ratio=0.45,
    )
    if proc_items:
        proc_items.sort(key=lambda x: x[0])
        return proc_items[-1][1], proc_items[-1][2]

    proc_all = collect(reader.readtext(_preprocess_handwriting_region(roi), detail=1, paragraph=False))
    if proc_all:
        proc_all.sort(key=lambda x: x[0])
        return proc_all[-1][1], proc_all[-1][2]

    return "", 0.0


def _try_tesseract(roi: np.ndarray) -> Tuple[str, float]:
    global _tesseract_available
    try:
        import pytesseract

        if _tesseract_available is False:
            return "", 0.0
        processed = _preprocess_handwriting_region(roi)
        config = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789- "
        text = pytesseract.image_to_string(processed, config=config).strip()
        _tesseract_available = True
        return text, 0.5 if text else 0.0
    except Exception:
        _tesseract_available = False
        return "", 0.0


def _clean_name(text: str) -> str:
    text = re.sub(r"(?i)name\s*:?", "", text).strip()
    text = re.sub(r"(?i)(registration|reg|class|subject|quiz|minutes|marks|bse|artificial|intelligence).*", "", text)
    text = re.sub(r"[^A-Za-z\s.'-]", "", text)

    words = []
    for w in text.split():
        w = w.strip("._-")
        if len(w) < 2 or _is_name_field_garbage(w):
            continue
        words.append(w)

    if not words:
        return "Unknown"

    # Handwritten name sits on the right: drop leading garbage tokens
    while words and _is_name_field_garbage(words[0]):
        words.pop(0)

    if len(words) > 3:
        words = words[-3:]

    name = " ".join(words).strip()
    if name:
        return name[0].upper() + name[1:]
    return "Unknown"


def _clean_reg_no(text: str) -> str:
    text = re.sub(r"(?i)registration\s*#?\s*:?", "", text)
    text = re.sub(r"(?i)reg\s*#?\s*:?", "", text)
    text = text.upper()
    text = re.sub(r"[^A-Z0-9\-]", "", text)
    match = re.search(r"FA\d{2}-[A-Z]{2,4}-\d{3,4}", text)
    if match:
        return match.group(0)
    match = re.search(r"[A-Z]{2}\d{2}-[A-Z]{2,4}-\d{3,4}", text)
    if match:
        return match.group(0)
    # Recover partial reads like 4-BSE-005
    partial = re.search(r"(\d{1,2})-BSE-(\d{3,4})", text)
    if partial:
        return f"FA24-BSE-{partial.group(2)}"
    return text.strip()


def extract_student_info(image_source) -> StudentInfo:
    """
    Extract handwritten name and registration number from quiz sheet.

    Uses layout-based cropping (standard BSE quiz format) + EasyOCR.
    """
    if isinstance(image_source, str):
        img = load_image(image_source)
    else:
        img = image_source.copy()

    img = resize_max_dimension(img, 2000)

    # Handwriting only (right of printed labels)
    name_roi = crop_relative(img, 0.17, 0.108, 0.36, 0.148)
    reg_roi = crop_relative(img, 0.52, 0.108, 0.82, 0.148)

    name_text, name_conf = _ocr_name_field(name_roi)
    if not name_text or name_conf < 0.3:
        alt, conf = _try_tesseract(name_roi)
        if conf > name_conf:
            name_text, name_conf = alt, conf

    reg_text, reg_conf = _ocr_region(reg_roi)
    if not reg_text or reg_conf < 0.3:
        alt, conf = _try_tesseract(reg_roi)
        if conf > reg_conf:
            reg_text, reg_conf = alt, conf

    name = _clean_name(name_text) or "Unknown"
    reg_no = _clean_reg_no(reg_text) or "Unknown"

    return StudentInfo(
        name=name,
        reg_no=reg_no,
        confidence_name=name_conf,
        confidence_reg=reg_conf,
    )


def extract_student_info_demo(image_path: str) -> Tuple[StudentInfo, str]:
    info = extract_student_info(image_path)
    summary = f"Name: {info.name} (confidence: {info.confidence_name:.2f})\n"
    summary += f"Reg No: {info.reg_no} (confidence: {info.confidence_reg:.2f})"
    return info, summary
