# Automated Quiz Scanner & Grading System

**Course:** Artificial Intelligence (BSE-4A) · **Semester:** SP 2026  
**Web app** for scanning physical quiz sheets: QR answer key, OCR student info, bubble reading, grading, and batch Excel export.

## Tasks Completed

| Task | Description | Status |
|------|-------------|--------|
| **1** | QR code decoding → `decode_answer_key()` | ✅ |
| **2** | Student info OCR → `extract_student_info()` | ✅ |
| **3** | Bubble sheet reading → `read_bubble_sheet()` | ✅ |
| **4** | Quiz grading → `grade_quiz()` | ✅ |
| **5** | Batch processing & Excel report | ✅ |

## Tech Stack

- **Backend:** Python 3.10+, Flask
- **QR:** OpenCV, pyzbar
- **OCR:** EasyOCR (+ optional Tesseract fallback)
- **Image processing:** OpenCV, NumPy
- **Reports:** pandas, openpyxl
- **Frontend:** HTML, CSS, JavaScript

## Folder Structure

```
quiz-scanner/
├── src/                    # Core modules + Flask app
│   ├── qr_decoder.py       # Task 1
│   ├── ocr_extractor.py    # Task 2
│   ├── bubble_reader.py    # Task 3
│   ├── grader.py           # Task 4
│   ├── batch_processor.py  # Task 5
│   ├── pipeline.py
│   └── app.py
├── samples/                # Test quiz images
├── output/                 # Generated Excel reports
├── scripts/                # CLI demos
├── templates/
├── static/
└── README.md
```

## Installation

### 1. Prerequisites

- **Python 3.10+**
- **ZBar** (for QR decoding):
  - Windows: install from [ZBar releases](https://sourceforge.net/projects/zbar/files/) or `choco install zbar`
  - macOS: `brew install zbar`
  - Linux: `sudo apt install libzbar0`

### 2. Create virtual environment

```bash
cd quiz-scanner
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** First run downloads EasyOCR models (~100 MB). Processing one sheet may take 30–60 seconds initially.

### 4. (Optional) PDF support

Install [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) and add to PATH, then:

```bash
pip install pdf2image
```

## How to Run

### Web application

```bash
cd quiz-scanner
python src/app.py
```

Open **http://127.0.0.1:5000**

- **Single Sheet:** upload one quiz image → view answer key, OCR, bubbles, grade breakdown
- **Batch Upload:** upload multiple images → download timestamped `.xlsx` report

### CLI demo (all tasks)

```bash
python scripts/run_demo.py
```

### Generate batch sample output

```bash
python scripts/generate_sample_batch.py
```

Creates `samples/batch/` (5 copies) and `output/AI_Quiz_SP2026_*.xlsx`.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Web UI |
| POST | `/api/scan` | Single image (`file` field) |
| POST | `/api/batch` | Multiple images (`files` field) |
| GET | `/api/download/<filename>` | Download Excel report |

## QR Payload Format

```
AI Quiz SP2026 Set-C | Part-I: Q1=D Q2=A Q3=B Q4=A Q5=D Q6=A Q7=A Q8=B | Part-II: Q1=C Q2=D Q3=D Q4=D Q5=C Q6=C Q7=C Q8=B
```

Optional negative marking:

```
... | Negative marking: yes, 0.25
```

## Sample Data

- `samples/Ayan-sample.png` — class sample (Name: Ayan, Reg: FA24-BSE-005)
- `output/AI_Quiz_SP2026_sample_output.xlsx` — example batch report (after running generate script)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Unable to find zbar shared library` | Install ZBar and ensure DLL is on PATH (Windows) |
| QR not found | Ensure QR is visible; try higher-resolution scan |
| Slow OCR | Normal on first run; GPU EasyOCR optional |
| Wrong bubbles | Re-scan with flat alignment; check fill threshold in `bubble_reader.py` |

## Academic Integrity

Built with open-source libraries (OpenCV, EasyOCR, pyzbar, Flask).

## Author

Ayan(FA24-BSE-005), Abdurrehman(FA24-BSE-001), Syed Muhammad Haziq(FA24-BSE-031).
