"""Task 1: QR code detection and answer-key parsing."""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from pyzbar import pyzbar

from models import QUESTION_IDS, AnswerKey
from image_utils import enhance_for_qr, load_image, resize_max_dimension, rotate_image

# Example: AI Quiz SP2026 Set-C | Part-I: Q1=D Q2=A ... | Part-II: Q1=C ...
PAYLOAD_PATTERN = re.compile(
    r"(?P<quiz>.+?)\s+Set[-\s]?(?P<set>[A-Za-z0-9]+)\s*\|\s*"
    r"Part[-\s]?I:\s*(?P<part1>.*?)\s*\|\s*"
    r"Part[-\s]?II:\s*(?P<part2>.*)",
    re.IGNORECASE,
)
ANSWER_PATTERN = re.compile(r"Q(?:uestion)?\s*0?(\d)\s*=\s*([A-Da-d])", re.IGNORECASE)
NEGATIVE_PATTERN = re.compile(
    r"negative\s*marking\s*[:=]\s*(?P<enabled>yes|true|1|on)"
    r"(?:\s*,\s*(?P<value>-?\d*\.?\d+))?",
    re.IGNORECASE,
)


def _parse_answers_block(text: str) -> Dict[str, str]:
    answers: Dict[str, str] = {}
    for match in ANSWER_PATTERN.finditer(text):
        qid = f"Q{int(match.group(1)):02d}"
        answers[qid] = match.group(2).upper()
    return answers


def parse_qr_payload(payload: str) -> AnswerKey:
    """Parse decoded QR string into structured AnswerKey."""
    payload = payload.strip()
    negative_marking = False
    negative_per_wrong = 0.0

    neg_match = NEGATIVE_PATTERN.search(payload)
    if neg_match:
        negative_marking = True
        if neg_match.group("value"):
            negative_per_wrong = float(neg_match.group("value"))

    match = PAYLOAD_PATTERN.search(payload)
    if not match:
        raise ValueError(f"Unrecognized QR payload format: {payload[:120]}...")

    quiz_id = match.group("quiz").strip()
    set_id = match.group("set").strip().upper()
    part1 = _parse_answers_block(match.group("part1"))
    part2 = _parse_answers_block(match.group("part2"))

    for q in QUESTION_IDS:
        part1.setdefault(q, "")
        part2.setdefault(q, "")

    return AnswerKey(
        quiz_identifier=quiz_id,
        set_identifier=set_id,
        part1=part1,
        part2=part2,
        negative_marking=negative_marking,
        negative_per_wrong=negative_per_wrong,
        raw_payload=payload,
    )


def _decode_from_image(img: np.ndarray) -> Optional[str]:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    for variant in enhance_for_qr(gray):
        codes = pyzbar.decode(variant)
        for code in codes:
            try:
                return code.data.decode("utf-8")
            except UnicodeDecodeError:
                return code.data.decode("latin-1")
    return None


def decode_answer_key(image_source) -> AnswerKey:
    """
    Detect and decode QR code from image path or numpy array.

    Tries multiple rotations and preprocessing passes for robustness.
    """
    if isinstance(image_source, str):
        img = load_image(image_source)
    else:
        img = image_source.copy()

    img = resize_max_dimension(img, 2400)

    for angle in (0, 90, 180, 270):
        rotated = rotate_image(img, angle)
        payload = _decode_from_image(rotated)
        if payload:
            key = parse_qr_payload(payload)
            if angle != 0:
                key.raw_payload += f" [decoded at {angle}° rotation]"
            return key

    # Try upper-right crop (QR is typically top-right on quiz sheets)
    h, w = img.shape[:2]
    crop = img[0 : int(h * 0.35), int(w * 0.55) : w]
    for angle in (0, 90, 180, 270):
        rotated = rotate_image(crop, angle)
        payload = _decode_from_image(rotated)
        if payload:
            return parse_qr_payload(payload)

    raise ValueError(
        "No QR code found. Ensure the image includes a readable QR code in the top-right."
    )


def decode_answer_key_demo(image_path: str) -> Tuple[AnswerKey, str]:
    key = decode_answer_key(image_path)
    lines = [
        f"Quiz: {key.quiz_identifier}",
        f"Set: {key.set_identifier}",
        "Part-I:",
    ]
    for q in QUESTION_IDS:
        lines.append(f"  {q}: {key.part1.get(q, '?')}")
    lines.append("Part-II:")
    for q in QUESTION_IDS:
        lines.append(f"  {q}: {key.part2.get(q, '?')}")
    if key.negative_marking:
        lines.append(f"Negative marking: {key.negative_per_wrong} per wrong answer")
    return key, "\n".join(lines)
