"""Data models for the quiz scanner pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


QUESTION_IDS = [f"Q{i:02d}" for i in range(1, 9)]


@dataclass
class AnswerKey:
    quiz_identifier: str
    set_identifier: str
    part1: Dict[str, str]
    part2: Dict[str, str]
    class_name: str = ""
    subject: str = ""
    total_marks: int = 16
    negative_marking: bool = False
    negative_per_wrong: float = 0.0
    raw_payload: str = ""

    def to_dict(self) -> dict:
        return {
            "quiz_identifier": self.quiz_identifier,
            "set_identifier": self.set_identifier,
            "class_name": self.class_name,
            "subject": self.subject,
            "total_marks": self.total_marks,
            "negative_marking": self.negative_marking,
            "negative_per_wrong": self.negative_per_wrong,
            "part1": self.part1,
            "part2": self.part2,
            "raw_payload": self.raw_payload,
        }


@dataclass
class StudentInfo:
    name: str
    reg_no: str
    confidence_name: float = 0.0
    confidence_reg: float = 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "reg_no": self.reg_no,
            "confidence_name": self.confidence_name,
            "confidence_reg": self.confidence_reg,
        }


@dataclass
class StudentAnswers:
    part1: Dict[str, Optional[str]]
    part2: Dict[str, Optional[str]]
    part1_flags: Dict[str, str] = field(default_factory=dict)
    part2_flags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "part1": self.part1,
            "part2": self.part2,
            "part1_flags": self.part1_flags,
            "part2_flags": self.part2_flags,
        }


@dataclass
class QuestionResult:
    question_id: str
    part: str
    student_answer: Optional[str]
    correct_answer: str
    status: str  # correct | incorrect | unattempted | invalid
    flag: Optional[str] = None


@dataclass
class GradeReport:
    quiz_identifier: str
    set_identifier: str
    student_info: StudentInfo
    correct: int
    incorrect: int
    unattempted: int
    invalid: int
    total_marks: float
    max_marks: int
    percentage: float
    letter_grade: str
    per_question: List[QuestionResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "quiz_identifier": self.quiz_identifier,
            "set_identifier": self.set_identifier,
            "student_info": self.student_info.to_dict(),
            "correct": self.correct,
            "incorrect": self.incorrect,
            "unattempted": self.unattempted,
            "invalid": self.invalid,
            "total_marks": self.total_marks,
            "max_marks": self.max_marks,
            "percentage": self.percentage,
            "letter_grade": self.letter_grade,
            "per_question": [
                {
                    "question_id": q.question_id,
                    "part": q.part,
                    "student_answer": q.student_answer,
                    "correct_answer": q.correct_answer,
                    "status": q.status,
                    "flag": q.flag,
                }
                for q in self.per_question
            ],
        }
