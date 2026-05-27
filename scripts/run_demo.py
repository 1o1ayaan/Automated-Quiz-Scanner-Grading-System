"""CLI demo for all quiz scanner tasks."""
from __future__ import annotations

import os
import sys

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(SRC))

SAMPLE = os.path.join(os.path.dirname(__file__), "..", "samples", "Ayan-sample.png")


def main():
    if not os.path.isfile(SAMPLE):
        print(f"Sample not found: {SAMPLE}")
        sys.exit(1)

    print("=" * 60)
    print("Task 1: QR Code Decoding")
    print("=" * 60)
    from qr_decoder import decode_answer_key_demo

    try:
        key, text = decode_answer_key_demo(SAMPLE)
        print(text)
    except Exception as e:
        print(f"QR decode failed: {e}")

    print("\n" + "=" * 60)
    print("Task 2: Student Information (OCR)")
    print("=" * 60)
    from ocr_extractor import extract_student_info_demo

    info, text = extract_student_info_demo(SAMPLE)
    print(text)

    print("\n" + "=" * 60)
    print("Task 3: Bubble Sheet Reading")
    print("=" * 60)
    from bubble_reader import read_bubble_sheet_demo

    answers, text = read_bubble_sheet_demo(SAMPLE)
    print(text)

    print("\n" + "=" * 60)
    print("Task 4: Quiz Grading")
    print("=" * 60)
    from grader import format_grade_report, grade_quiz
    from qr_decoder import decode_answer_key
    from bubble_reader import read_bubble_sheet
    from ocr_extractor import extract_student_info

    try:
        key = decode_answer_key(SAMPLE)
    except Exception:
        from models import AnswerKey

        key = AnswerKey(
            quiz_identifier="AI Quiz SP2026",
            set_identifier="DEMO",
            part1={f"Q{i:02d}": "A" for i in range(1, 9)},
            part2={f"Q{i:02d}": "B" for i in range(1, 9)},
        )
        print("(Using demo answer key — QR not decoded)")

    ans = read_bubble_sheet(SAMPLE)
    info = extract_student_info(SAMPLE)
    report = grade_quiz(ans, key, info)
    print(format_grade_report(report))


if __name__ == "__main__":
    main()
