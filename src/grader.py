"""Task 4: Compare student answers to answer key and produce grade report."""
from __future__ import annotations

from typing import List, Optional

from models import (
    QUESTION_IDS,
    AnswerKey,
    GradeReport,
    QuestionResult,
    StudentAnswers,
    StudentInfo,
)


def _letter_grade(percentage: float) -> str:
    if percentage >= 90:
        return "A"
    if percentage >= 80:
        return "B"
    if percentage >= 70:
        return "C"
    if percentage >= 60:
        return "D"
    return "F"


def _evaluate_answer(
    student: Optional[str],
    correct: str,
    flag: Optional[str],
) -> str:
    if flag and flag.startswith("invalid"):
        return "invalid"
    if student is None or student == "":
        return "unattempted"
    if student.upper() == correct.upper():
        return "correct"
    return "incorrect"


def grade_quiz(
    student_answers: StudentAnswers,
    answer_key: AnswerKey,
    student_info: Optional[StudentInfo] = None,
) -> GradeReport:
    """Grade quiz: 1 mark per correct answer unless negative marking in QR payload."""
    per_question: List[QuestionResult] = []
    correct = incorrect = unattempted = invalid = 0
    total_marks = 0.0
    max_marks = len(QUESTION_IDS) * 2

    parts = [
        ("Part-I", student_answers.part1, answer_key.part1, student_answers.part1_flags),
        ("Part-II", student_answers.part2, answer_key.part2, student_answers.part2_flags),
    ]

    for part_name, student_part, key_part, flags in parts:
        for qid in QUESTION_IDS:
            student_ans = student_part.get(qid)
            correct_ans = key_part.get(qid, "")
            flag = flags.get(qid)
            status = _evaluate_answer(student_ans, correct_ans, flag)

            if status == "correct":
                correct += 1
                total_marks += 1.0
            elif status == "incorrect":
                incorrect += 1
                if answer_key.negative_marking:
                    total_marks -= abs(answer_key.negative_per_wrong or 0.25)
            elif status == "unattempted":
                unattempted += 1
            else:
                invalid += 1

            per_question.append(
                QuestionResult(
                    question_id=qid,
                    part=part_name,
                    student_answer=student_ans,
                    correct_answer=correct_ans,
                    status=status,
                    flag=flag,
                )
            )

    total_marks = max(0.0, total_marks)
    percentage = (total_marks / max_marks * 100) if max_marks else 0.0

    return GradeReport(
        quiz_identifier=answer_key.quiz_identifier,
        set_identifier=answer_key.set_identifier,
        student_info=student_info or StudentInfo(name="Unknown", reg_no="Unknown"),
        correct=correct,
        incorrect=incorrect,
        unattempted=unattempted,
        invalid=invalid,
        total_marks=round(total_marks, 2),
        max_marks=max_marks,
        percentage=round(percentage, 2),
        letter_grade=_letter_grade(percentage),
        per_question=per_question,
    )


def status_symbol(status: str) -> str:
    return {"correct": "[OK]", "incorrect": "[X]", "unattempted": "[-]", "invalid": "[!]"}.get(
        status, "?"
    )


def format_grade_report(report: GradeReport) -> str:
    lines = [
        f"Student: {report.student_info.name} ({report.student_info.reg_no})",
        f"Quiz: {report.quiz_identifier} | Set: {report.set_identifier}",
        "",
        f"Score: {report.total_marks:.0f} / {report.max_marks} ({report.percentage:.1f}%) — Grade {report.letter_grade}",
        f"Correct: {report.correct} | Incorrect: {report.incorrect} | "
        f"Unattempted: {report.unattempted} | Invalid: {report.invalid}",
        "",
        "Per-question breakdown:",
    ]
    for q in report.per_question:
        sym = status_symbol(q.status)
        ans = q.student_answer or "-"
        lines.append(
            f"  {sym} {q.part} {q.question_id}: student={ans}, key={q.correct_answer} [{q.status}]"
        )
    return "\n".join(lines)
