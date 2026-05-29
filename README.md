# Automated Quiz Scanner & Grading System

**Course:** Artificial Intelligence (BSE-4A) · **Semester:** SP 2026  
**Authors:** Ayan (FA24-BSE-005) · Abdurrehman (FA24-BSE-001) · Syed Muhammad Haziq (FA24-BSE-031)

A web application that scans physical printed quiz sheets from images, automatically decodes the answer key from a QR code, reads filled bubbles using computer vision, extracts student information via OCR, grades responses, and exports results to Excel — all without manual data entry.

---

## ✅ Tasks Completed

| Task | Module | Description | Status |
|------|--------|-------------|--------|
| **1** | `qr_decoder.py` | QR code decoding → `decode_answer_key()` | ✅ Done |
| **2** | `ocr_extractor.py` | Student info OCR → `extract_student_info()` | ✅ Done |
| **3** | `bubble_reader.py` | Bubble sheet reading → `read_bubble_sheet()` | ✅ Done |
| **4** | `grader.py` | Quiz grading → `grade_quiz()` | ✅ Done |
| **5** | `batch_processor.py` | Batch processing & Excel/CSV report export | ✅ Done |
| **6** | `image_utils.py` | Image preprocessing & enhancement utilities | ✅ Done |
| **7** | `pipeline.py` | Full end-to-end pipeline integrating all modules | ✅ Done |
| **8** | `app.py` | Flask web server with single & batch upload UI | ✅ Done |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10+, Flask 3.0+ |
| **QR Decoding** | OpenCV, pyzbar |
| **OCR** | EasyOCR 1.7+ (Tesseract fallback optional) |
| **Image Processing** | OpenCV 4.8+, NumPy |
| **Reports** | pandas, openpyxl (`.xlsx`), CSV |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |

---

## 📁 Folder Structure

```
quiz-scanner/
├── src/                          # Core modules + Flask app
│   ├── app.py                    # Flask web server (routes + UI)
│   ├── pipeline.py               # End-to-end processing pipeline
│   ├── qr_decoder.py             # Task 1 — QR answer key decoding
│   ├── ocr_extractor.py          # Task 2 — Student name/reg OCR
│   ├── bubble_reader.py          # Task 3 — Optical mark recognition
│   ├── grader.py                 # Task 4 — Answer grading logic
│   ├── batch_processor.py        # Task 5 — Multi-image batch + Excel export
│   ├── image_utils.py            # Image loading, enhancement, cropping
│   └── models.py                 # Data classes (AnswerKey, GradeReport, etc.)
│
├── scripts/                      # CLI tools & debug utilities
│   ├── run_demo.py               # Run pipeline on all sample images
│   ├── test_all.py               # Batch test all images in samples/
│   ├── generate_sample_batch.py  # Generate bulk sample output
│   ├── debug_qr.py               # Debug QR decoding on a specific image
│   ├── debug_bubbles.py          # Debug bubble region detection
│   ├── debug_visualization.py    # Save visual grid overlays to demo/
│   ├── test_individual_bubbles.py# Inspect per-bubble fill scores
│   └── find_bubble_centers.py    # Calibrate bubble grid coordinates
│
├── samples/                      # Test quiz sheet images (6 real sheets)
│   ├── sample1.png               
│   ├── sample2.png               
│   ├── sample3.png               
│   ├── sample4.png               
│   ├── sample5.png               
│   └── sample6.png               
│
├── output/                       # Generated Excel/CSV reports
├── demo/                         # Debug visualization output images
├── templates/                    # HTML templates for Flask UI
├── static/                       # CSS, JS, and frontend assets
├── Sample output/                # Screenshots of graded results
├── requirements.txt              # Python dependencies
├── run.bat                       # One-click launcher (Windows)
└── README.md
```

---

## ⚙️ Installation

### Prerequisites

- **Python 3.10 or newer** — [Download](https://www.python.org/downloads/)
- **ZBar library** (required for QR decoding):
  - **Windows:** Download from [ZBar SourceForge](https://sourceforge.net/projects/zbar/files/) or run `choco install zbar`
  - **macOS:** `brew install zbar`
  - **Linux:** `sudo apt install libzbar0`

---

### Step 1 — Clone / Open the project

```bash
cd "quiz-scanner"
```

---

### Step 2 — Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** First run downloads EasyOCR models (~100 MB). Processing one sheet takes 30–60 seconds on initial load, then becomes fast.

---

### Step 4 — (Optional) PDF support

Install [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases), add to PATH, then:

```bash
pip install pdf2image
```

---

## 🚀 How to Run

### Option A — One-Click Launch (Windows only)

Simply double-click **`run.bat`** in the project root.

It automatically:
1. Creates the virtual environment if missing
2. Installs all dependencies
3. Starts the Flask server at `http://127.0.0.1:5000`

---

### Option B — Manual Launch

```bash
# Activate venv first
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Start the web server
python src/app.py
```

Then open **http://127.0.0.1:5000** in your browser.

---

### Option C — CLI Demo (no browser)

Run the full pipeline on all images in `samples/` and print results to terminal:

```bash
python scripts/run_demo.py
```

---

### Option D — Batch Test All Sample Images

Test every image in `samples/` and see a grading summary for each:

```bash
python scripts/test_all.py
```

---

### Option E — Generate Sample Batch Report

Creates 5 sample quiz copies and generates a full Excel report:

```bash
python scripts/generate_sample_batch.py
```

Output: `samples/batch/` folder + `output/AI_Quiz_SP2026_*.xlsx`

---

## 🌐 Web App Usage

Once the server is running at **http://127.0.0.1:5000**:

### Single Sheet Mode
1. Click **"Single Sheet"**
2. Upload one quiz image (PNG, JPG, or PDF)
3. View the result:
   - ✅ Decoded answer key (from QR code)
   - 🎓 Student name & registration number (from OCR)
   - 🔵 Bubble readings per question (A/B/C/D or unattempted/invalid)
   - 📊 Grade breakdown (correct / incorrect / unattempted / invalid)
   - 🅰️ Letter grade (A / B / C / D / F)

### Batch Mode
1. Click **"Batch Upload"**
2. Select multiple quiz images at once
3. Click **"Process Batch"**
4. Download the timestamped `.xlsx` Excel report

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Web UI (home page) |
| `POST` | `/api/scan` | Process single image — field: `file` |
| `POST` | `/api/batch` | Process multiple images — field: `files` |
| `GET` | `/api/download/<filename>` | Download generated Excel report |

### Example API call (curl)

```bash
curl -X POST http://127.0.0.1:5000/api/scan \
  -F "file=@samples/sample1.png"
```

---

## 📋 QR Code Payload Format

The QR code on each quiz sheet encodes the full answer key. Format:

```
AI Quiz SP2026 Set-A | Part-I: Q1=D Q2=A Q3=D Q4=A Q5=D Q6=C Q7=D Q8=C | Part-II: Q1=D Q2=C Q3=B Q4=C Q5=B Q6=C Q7=A Q8=B
```

### With negative marking (optional):

```
AI Quiz SP2026 Set-A | Part-I: Q1=D Q2=A ... | Part-II: Q1=D ... | Negative marking: yes, 0.25
```

### Set variants used in testing:

| Set | Part-I | Part-II |
|-----|--------|---------|
| **A** | Q1=D Q2=A Q3=D Q4=A Q5=D Q6=C Q7=D Q8=C | Q1=D Q2=C Q3=B Q4=C Q5=B Q6=C Q7=A Q8=B |
| **B** | Q1=A Q2=B Q3=A Q4=B Q5=B Q6=C Q7=B Q8=B | Q1=A Q2=C Q3=B Q4=A Q5=A Q6=D Q7=D Q8=C |
| **C** | Q1=D Q2=A Q3=B Q4=A Q5=D Q6=A Q7=A Q8=B | Q1=C Q2=D Q3=D Q4=D Q5=C Q6=C Q7=C Q8=B |

---

## 📊 Grading Logic

| Status | Condition | Marks |
|--------|-----------|-------|
| **Correct** | Filled bubble matches answer key | +1 |
| **Incorrect** | Wrong bubble filled | 0 (or −0.25 if negative marking on) |
| **Unattempted** | No bubble filled | 0 |
| **Invalid** | Multiple bubbles filled | 0 |

Letter grades: **A** ≥ 90% · **B** ≥ 80% · **C** ≥ 70% · **D** ≥ 60% · **F** < 60%

---

## 🔍 Debug & Calibration Scripts

These scripts were added during development to diagnose and fix detection issues:

| Script | Purpose |
|--------|---------|
| `scripts/debug_qr.py` | Test QR decoding on a specific image at multiple resolutions |
| `scripts/debug_bubbles.py` | Visualize detected bubble regions on screen |
| `scripts/debug_visualization.py` | Save bubble grid overlay images to `demo/` folder |
| `scripts/test_individual_bubbles.py` | Print per-bubble fill scores for each question |
| `scripts/find_bubble_centers.py` | Recalibrate bubble column/row coordinates |
| `scripts/test_all.py` | Run and print grading results for all images in `samples/` |

### Run a debug visualization

```bash
# Saves overlay images to demo/ showing detected bubble grid
python scripts/debug_visualization.py

# Test QR decoding with multiple image scales
python scripts/debug_qr.py
```

---

## 🐛 Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `Unable to find zbar shared library` | ZBar not installed | Install ZBar and ensure its DLL is on PATH (Windows) |
| QR code not detected | Low resolution or image too large | The decoder auto-tries multiple scales (1200px target works best) |
| Wrong bubble detected | Sheet misaligned or low contrast | Re-scan flat; adjust `MIN_FILL` threshold in `bubble_reader.py` |
| Slow first run | EasyOCR model download | Normal — ~100 MB downloaded once; subsequent runs are fast |
| OCR returns wrong name | Poor scan quality | Increase image resolution; ensure name box is clearly visible |
| Multiple bubbles flagged as invalid | Student filled >1 bubble | Flagged correctly — review original sheet |

---

## 📁 Output Files

After processing, results are saved to:

```
output/
└── AI_Quiz_SP2026_YYYYMMDD_HHMMSS.xlsx    ← Excel batch report
```

The Excel report contains columns:
`Name · Reg No · Set · Correct · Incorrect · Unattempted · Invalid · Score · Max · % · Grade · Q01…Q16 answers`

---

## 🔗 Related Project

> **QuizScannerAR** — the Android companion app — is located in the `QuizScannerAR/` folder at the same level as this project. It performs real-time camera-based grading using the same QR format and grading logic, ported to Kotlin.

---

## 📜 Academic Integrity

Built entirely with open-source libraries: OpenCV, EasyOCR, pyzbar, Flask, pandas, openpyxl.

## 👥 Authors

| Name | Roll No |
|------|---------|
| Ayan | FA24-BSE-005 |
| Abdurrehman | FA24-BSE-001 |
| Syed Muhammad Haziq | FA24-BSE-031 |
