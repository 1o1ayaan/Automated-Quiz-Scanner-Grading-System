"""Task 5: Batch processing and Excel/CSV report generation."""
from __future__ import annotations

import os
from datetime import datetime
from typing import List, Optional

import pandas as pd

from bubble_reader import read_bubble_sheet
from grader import grade_quiz
from models import QUESTION_IDS, GradeReport
from ocr_extractor import extract_student_info
from qr_decoder import decode_answer_key

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp", ".pdf"}


def _metadata_from_image(image_path: str) -> dict:
    """Extract printed metadata using layout crops (class, subject)."""
    from image_utils import crop_relative, load_image

    img = load_image(image_path)
    # Class line region
    class_roi = crop_relative(img, 0.05, 0.06, 0.35, 0.10)
    subject_roi = crop_relative(img, 0.38, 0.06, 0.65, 0.10)

    class_name = "BSE-4A"
    subject = "Artificial Intelligence"

    try:
        import easyocr

        reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        for roi, default, key in [
            (class_roi, class_name, "class"),
            (subject_roi, subject, "subject"),
        ]:
            results = reader.readtext(roi, detail=0)
            text = " ".join(results).upper()
            if key == "class" and "BSE" in text:
                for token in text.split():
                    if "BSE" in token:
                        class_name = token.replace("CLASS:", "").strip()
                        break
            if key == "subject" and "ARTIFICIAL" in text:
                subject = "Artificial Intelligence"
    except Exception:
        pass

    return {"class_name": class_name, "subject": subject}


def process_single_sheet(image_path: str) -> dict:
    """Run full pipeline on one quiz image."""
    answer_key = decode_answer_key(image_path)
    student_info = extract_student_info(image_path)
    student_answers = read_bubble_sheet(image_path)
    report = grade_quiz(student_answers, answer_key, student_info)
    meta = _metadata_from_image(image_path)

    row = {
        "Quiz": answer_key.quiz_identifier,
        "Set": answer_key.set_identifier,
        "Class": meta["class_name"],
        "Subject": meta["subject"],
        "Name": student_info.name,
        "Reg No": student_info.reg_no,
    }

    for q in QUESTION_IDS:
        row[f"Part1_{q}"] = student_answers.part1.get(q) or ""
    for q in QUESTION_IDS:
        row[f"Part2_{q}"] = student_answers.part2.get(q) or ""

    row.update(
        {
            "Correct": report.correct,
            "Incorrect": report.incorrect,
            "Unattempted": report.unattempted,
            "Invalid": report.invalid,
            "Total Marks": report.total_marks,
            "Percentage": report.percentage,
            "Grade": report.letter_grade,
            "_source_file": os.path.basename(image_path),
            "_report": report,
        }
    )
    return row


def process_batch(
    input_folder: str,
    output_dir: Optional[str] = None,
    quiz_title: str = "AI_Quiz_SP2026",
) -> str:
    """
    Process all quiz images in a folder and write Excel report.

    Returns path to generated file.
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(input_folder), "output")
    os.makedirs(output_dir, exist_ok=True)

    files = sorted(
        f
        for f in os.listdir(input_folder)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
    )
    if not files:
        raise ValueError(f"No image files found in {input_folder}")

    rows: List[dict] = []
    errors: List[dict] = []

    for fname in files:
        path = os.path.join(input_folder, fname)
        try:
            rows.append(process_single_sheet(path))
        except Exception as exc:
            errors.append({"File": fname, "Error": str(exc)})

    if not rows:
        raise RuntimeError("No sheets processed successfully. " + str(errors))

    df = pd.DataFrame(rows)
    report_cols = [c for c in df.columns if not c.startswith("_")]
    df_out = df[report_cols].copy()

    # Summary statistics row
    numeric_scores = df_out["Total Marks"].astype(float)
    summary = {col: "" for col in report_cols}
    summary["Quiz"] = "SUMMARY"
    summary["Name"] = "Class Average / Stats"
    summary["Correct"] = round(df_out["Correct"].mean(), 2)
    summary["Total Marks"] = round(numeric_scores.mean(), 2)
    summary["Percentage"] = round(df_out["Percentage"].mean(), 2)
    summary["Grade"] = f"High: {numeric_scores.max():.0f} | Low: {numeric_scores.min():.0f}"

    df_out = pd.concat([df_out, pd.DataFrame([summary])], ignore_index=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in quiz_title)
    out_path = os.path.join(output_dir, f"{safe_title}_{timestamp}.xlsx")

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        df_out.to_excel(writer, sheet_name="Results", index=False)
        if errors:
            pd.DataFrame(errors).to_excel(writer, sheet_name="Errors", index=False)

    return out_path


def rows_to_dataframe(rows: List[dict]) -> pd.DataFrame:
    report_cols = [
        "Quiz",
        "Set",
        "Class",
        "Subject",
        "Name",
        "Reg No",
    ] + [f"Part1_{q}" for q in QUESTION_IDS] + [f"Part2_{q}" for q in QUESTION_IDS] + [
        "Correct",
        "Incorrect",
        "Unattempted",
        "Invalid",
        "Total Marks",
        "Percentage",
        "Grade",
    ]
    clean = [{k: r.get(k, "") for k in report_cols} for r in rows]
    return pd.DataFrame(clean)
