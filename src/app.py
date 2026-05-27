"""Flask web application for the Quiz Scanner & Grading System."""
from __future__ import annotations

import os
import sys
import tempfile
import zipfile
from datetime import datetime

from flask import Flask, jsonify, render_template, request, send_file

# Ensure src is on path when running as script
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from batch_processor import process_batch, process_single_sheet, rows_to_dataframe
from pipeline import process_quiz_image

app = Flask(
    __name__,
    template_folder=os.path.join(ROOT_DIR, "templates"),
    static_folder=os.path.join(ROOT_DIR, "static"),
)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "quiz-scanner"})


@app.route("/api/scan", methods=["POST"])
def scan_single():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400
    try:
        result = process_quiz_image(f.read(), f.filename)
        return jsonify({"success": True, "data": result})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/batch", methods=["POST"])
def scan_batch():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    rows = []
    errors = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for f in files:
            if not f.filename:
                continue
            path = os.path.join(tmpdir, f.filename)
            f.save(path)
            try:
                rows.append(process_single_sheet(path))
            except Exception as exc:
                errors.append({"file": f.filename, "error": str(exc)})

    if not rows:
        return jsonify({"success": False, "errors": errors}), 400

    output_dir = os.path.join(ROOT_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(output_dir, f"AI_Quiz_SP2026_{timestamp}.xlsx")

    import pandas as pd

    df = rows_to_dataframe(rows)
    numeric = df["Total Marks"].astype(float)
    summary = {col: "" for col in df.columns}
    summary["Quiz"] = "SUMMARY"
    summary["Name"] = "Class Average / Stats"
    summary["Correct"] = round(df["Correct"].mean(), 2)
    summary["Total Marks"] = round(numeric.mean(), 2)
    summary["Percentage"] = round(df["Percentage"].mean(), 2)
    summary["Grade"] = f"High: {numeric.max():.0f} | Low: {numeric.min():.0f}"
    df = pd.concat([df, pd.DataFrame([summary])], ignore_index=True)
    df.to_excel(out_path, index=False, sheet_name="Results")

    return jsonify(
        {
            "success": True,
            "processed": len(rows),
            "errors": errors,
            "download": f"/api/download/{os.path.basename(out_path)}",
            "rows": [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows],
        }
    )


@app.route("/api/download/<filename>")
def download_file(filename):
    output_dir = os.path.join(ROOT_DIR, "output")
    path = os.path.join(output_dir, filename)
    if not os.path.isfile(path):
        return jsonify({"error": "File not found"}), 404
    return send_file(path, as_attachment=True)


def main():
    print(f"Quiz Scanner running at http://127.0.0.1:5000")
    print(f"Project root: {ROOT_DIR}")
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
