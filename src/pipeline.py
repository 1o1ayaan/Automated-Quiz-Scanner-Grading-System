"""End-to-end quiz processing pipeline."""
from __future__ import annotations

from typing import Any, Dict

import numpy as np

from bubble_reader import read_bubble_sheet
from grader import format_grade_report, grade_quiz, status_symbol
from image_utils import load_image_from_bytes
from models import AnswerKey, StudentAnswers, StudentInfo
from ocr_extractor import extract_student_info
from qr_decoder import decode_answer_key


def process_quiz_image(image_bytes: bytes, filename: str = "quiz.png") -> Dict[str, Any]:
    """Run Tasks 1–4 on a single uploaded image."""
    img = load_image_from_bytes(image_bytes, filename)

    answer_key = decode_answer_key(img)
    student_info = extract_student_info(img)
    student_answers = read_bubble_sheet(img)
    report = grade_quiz(student_answers, answer_key, student_info)

    return {
        "answer_key": answer_key.to_dict(),
        "student_info": student_info.to_dict(),
        "student_answers": student_answers.to_dict(),
        "grade_report": report.to_dict(),
        "summary_text": format_grade_report(report),
        "status_symbols": {
            f"{q.part}_{q.question_id}": status_symbol(q.status)
            for q in report.per_question
        },
    }
