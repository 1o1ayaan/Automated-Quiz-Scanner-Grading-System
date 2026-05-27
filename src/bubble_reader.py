"""Task 3: Bubble sheet detection and answer extraction."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from models import QUESTION_IDS, StudentAnswers
from image_utils import crop_relative, load_image

OPTIONS = ["A", "B", "C", "D"]

# Fallback column bounds if auto-calibration fails
PART1_COL_BOUNDS = [0.205, 0.375, 0.545, 0.715, 0.885]
PART2_COL_BOUNDS = [0.10, 0.245, 0.39, 0.535, 0.68]
UPSCALE_FACTOR = 4
MIN_FILL_PIXELS = 18
MULTI_FILL_RATIO = 0.82  # second/top must exceed this to flag multi-fill
SCORE_CAP = 300  # ignore table-line artifacts in a column


def _upscale(img: np.ndarray) -> np.ndarray:
    if UPSCALE_FACTOR <= 1:
        return img
    return cv2.resize(
        img,
        None,
        fx=UPSCALE_FACTOR,
        fy=UPSCALE_FACTOR,
        interpolation=cv2.INTER_CUBIC,
    )


def _bubble_fill_score(cell: np.ndarray) -> float:
    """Count dark pixels inside central circle (robust for filled bubbles)."""
    if cell.size == 0:
        return 0.0
    if len(cell.shape) == 3:
        gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    else:
        gray = cell.copy()

    h, w = gray.shape
    size = min(h, w)
    if size < 4:
        return 0.0

    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, (w // 2, h // 2), max(2, int(size * 0.30)), 255, -1)
    raw = float(np.sum((gray < 110) & (mask > 0)))
    return min(raw, SCORE_CAP)


def _detect_horizontal_lines(grid_img: np.ndarray) -> List[int]:
    """Return Y coordinates of horizontal table lines."""
    gray = cv2.cvtColor(grid_img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 8
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(w // 3, 40), 1))
    horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    projection = np.sum(horizontal, axis=1)

    threshold = w * 0.35 * 255
    clusters: List[List[int]] = []
    for y, value in enumerate(projection):
        if value < threshold:
            continue
        if not clusters or y - clusters[-1][-1] > 5:
            clusters.append([y])
        else:
            clusters[-1].append(y)

    return [int(np.mean(cluster)) for cluster in clusters]


def _row_boundaries(grid_img: np.ndarray) -> List[Tuple[int, int]]:
    """Eight question rows from detected table lines (skip header band)."""
    lines = _detect_horizontal_lines(grid_img)
    h = grid_img.shape[0]

    if len(lines) >= 10:
        pairs = list(zip(lines[1:9], lines[2:10]))
    elif len(lines) >= 9:
        pairs = list(zip(lines[1:9], lines[2:9])) + [(lines[8], min(lines[8] + (lines[8] - lines[7]), h - 1))]
    else:
        top = int(h * 0.11)
        body = h - top
        step = body / 8
        pairs = [(int(top + i * step), int(top + (i + 1) * step)) for i in range(8)]

    return pairs[:8]


def _column_layout_quality(
    grid_img: np.ndarray, col_bounds: List[float], rows: List[Tuple[int, int]]
) -> float:
    """Score how well a column layout separates filled bubbles (higher is better)."""
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
        if top >= MIN_FILL_PIXELS:
            contrast = top - second
            total_contrast += contrast
            if contrast >= 10:
                clear_rows += 1

    return clear_rows * 100 + total_contrast


def _calibrate_column_bounds(
    grid_img: np.ndarray,
    c0_min: float,
    c0_max: float,
    fallback: List[float],
    presets: List[List[float]],
) -> List[float]:
    """
    Pick column boundaries from search + known-good presets for this quiz layout.

    Chooses the layout with the most clearly separated bubble fills per row.
    """
    rows = _row_boundaries(grid_img)
    candidates: List[List[float]] = [fallback] + [list(p) for p in presets]

    # Dynamically select search range based on Part 1 or Part 2 crop
    if c0_min < 0.15:
        # Part 2 OMR grid
        search_c0_min, search_c0_max = 0.07, 0.11
        search_cw_min, search_cw_max = 0.160, 0.170
    else:
        # Part 1 OMR grid
        search_c0_min, search_c0_max = 0.20, 0.23
        search_cw_min, search_cw_max = 0.165, 0.175

    for c0 in np.arange(search_c0_min, search_c0_max + 0.001, 0.005):
        for cw in np.arange(search_cw_min, search_cw_max + 0.001, 0.005):
            cols = [c0 + i * cw for i in range(5)]
            if cols[-1] > 0.95:
                continue
            candidates.append(cols)

    return max(candidates, key=lambda c: _column_layout_quality(grid_img, c, rows))


PART1_PRESETS = [
    [0.175, 0.345, 0.515, 0.685, 0.855],
    [0.205, 0.375, 0.545, 0.715, 0.885],
]
PART2_PRESETS = [
    [0.085, 0.25, 0.415, 0.58, 0.745],
    [0.10, 0.24, 0.38, 0.52, 0.66],
    [0.10, 0.245, 0.39, 0.535, 0.68],
]


def _read_part_grid(
    grid_img: np.ndarray, col_bounds: List[float]
) -> Tuple[Dict[str, Optional[str]], Dict[str, str]]:
    answers: Dict[str, Optional[str]] = {}
    flags: Dict[str, str] = {}
    h, w = grid_img.shape[:2]
    rows = _row_boundaries(grid_img)

    for i, qid in enumerate(QUESTION_IDS):
        y1, y2 = rows[i]
        y1 = max(0, y1 + 2)
        y2 = min(h, y2 - 2)

        scores: List[float] = []
        for j in range(4):
            x1 = int(col_bounds[j] * w)
            x2 = int(col_bounds[j + 1] * w)
            cell = grid_img[y1:y2, x1:x2]
            scores.append(_bubble_fill_score(cell))

        sorted_idx = sorted(range(4), key=lambda k: scores[k], reverse=True)
        top_i, second_i = sorted_idx[0], sorted_idx[1]
        top_score, second_score = scores[top_i], scores[second_i]

        if top_score < MIN_FILL_PIXELS:
            answers[qid] = None
            flags[qid] = "unattempted"
        elif (
            second_score > MIN_FILL_PIXELS
            and top_score > 0
            and (second_score / top_score) >= MULTI_FILL_RATIO
        ):
            answers[qid] = None
            flags[qid] = f"invalid_multi:{OPTIONS[top_i]}/{OPTIONS[second_i]}"
        else:
            answers[qid] = OPTIONS[top_i]

    return answers, flags


def _find_bubble_region(img: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    part1 = crop_relative(img, 0.025, 0.172, 0.485, 0.40)
    part2 = crop_relative(img, 0.515, 0.172, 0.975, 0.40)
    return part1, part2


def read_bubble_sheet(image_source) -> StudentAnswers:
    if isinstance(image_source, str):
        img = load_image(image_source)
    else:
        img = image_source.copy()

    img = _upscale(img)
    part1_grid, part2_grid = _find_bubble_region(img)

    part1_cols = _calibrate_column_bounds(
        part1_grid, 0.18, 0.28, PART1_COL_BOUNDS, PART1_PRESETS
    )
    part2_cols = _calibrate_column_bounds(
        part2_grid, 0.08, 0.16, PART2_COL_BOUNDS, PART2_PRESETS
    )

    part1_answers, part1_flags = _read_part_grid(part1_grid, part1_cols)
    part2_answers, part2_flags = _read_part_grid(part2_grid, part2_cols)

    return StudentAnswers(
        part1=part1_answers,
        part2=part2_answers,
        part1_flags=part1_flags,
        part2_flags=part2_flags,
    )


def read_bubble_sheet_demo(image_path: str) -> Tuple[StudentAnswers, str]:
    answers = read_bubble_sheet(image_path)
    lines = ["Part-I:"]
    for q in QUESTION_IDS:
        ans = answers.part1.get(q)
        flag = answers.part1_flags.get(q, "")
        suffix = f" [{flag}]" if flag else ""
        lines.append(f"  {q}: {ans or '-'}{suffix}")
    lines.append("Part-II:")
    for q in QUESTION_IDS:
        ans = answers.part2.get(q)
        flag = answers.part2_flags.get(q, "")
        suffix = f" [{flag}]" if flag else ""
        lines.append(f"  {q}: {ans or '-'}{suffix}")
    return answers, "\n".join(lines)
