"""Generate sample Excel output and duplicate test images for batch demo."""
from __future__ import annotations

import os
import shutil
import sys

import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

SAMPLE = os.path.join(ROOT, "samples", "Ayan-sample.png")
BATCH_DIR = os.path.join(ROOT, "samples", "batch")
OUTPUT = os.path.join(ROOT, "output")


def main():
    os.makedirs(BATCH_DIR, exist_ok=True)
    os.makedirs(OUTPUT, exist_ok=True)

    if os.path.isfile(SAMPLE):
        for i in range(1, 6):
            dest = os.path.join(BATCH_DIR, f"student_{i:02d}.png")
            shutil.copy(SAMPLE, dest)
        print(f"Created 5 batch images in {BATCH_DIR}")

    from batch_processor import process_batch

    try:
        out = process_batch(BATCH_DIR, OUTPUT, "AI_Quiz_SP2026")
        print(f"Batch report: {out}")
    except Exception as e:
        print(f"Batch processing note: {e}")
        _write_synthetic_output()


def _write_synthetic_output():
    """Fallback sample Excel if pipeline cannot run."""
    from models import QUESTION_IDS

    rows = []
    for i in range(1, 6):
        row = {
            "Quiz": "AI Quiz SP2026",
            "Set": "C",
            "Class": "BSE-4A",
            "Subject": "Artificial Intelligence",
            "Name": f"Student {i}",
            "Reg No": f"FA24-BSE-00{i}",
        }
        for q in QUESTION_IDS:
            row[f"Part1_{q}"] = "A"
            row[f"Part2_{q}"] = "B"
        row.update(
            {
                "Correct": 10 + i,
                "Incorrect": 4,
                "Unattempted": 2,
                "Invalid": 0,
                "Total Marks": 10 + i,
                "Percentage": round((10 + i) / 16 * 100, 2),
                "Grade": "B",
            }
        )
        rows.append(row)

    df = pd.DataFrame(rows)
    summary = {c: "" for c in df.columns}
    summary["Quiz"] = "SUMMARY"
    summary["Name"] = "Class Average / Stats"
    summary["Total Marks"] = df["Total Marks"].mean()
    summary["Percentage"] = df["Percentage"].mean()
    summary["Grade"] = f"High: {df['Total Marks'].max():.0f} | Low: {df['Total Marks'].min():.0f}"
    df = pd.concat([df, pd.DataFrame([summary])], ignore_index=True)

    path = os.path.join(OUTPUT, "AI_Quiz_SP2026_sample_output.xlsx")
    df.to_excel(path, index=False)
    print(f"Synthetic sample written: {path}")


if __name__ == "__main__":
    main()
