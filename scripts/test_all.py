"""Script to test all sample images through the quiz-scanner pipeline and display the results."""
import os
import sys

# Ensure src is on path
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from batch_processor import process_single_sheet
from grader import format_grade_report

def main():
    samples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "samples"))
    if not os.path.isdir(samples_dir):
        print(f"Samples directory not found at {samples_dir}")
        return

    files = [f for f in os.listdir(samples_dir) if f.lower().endswith(".png")]
    if not files:
        print("No png files found in samples directory.")
        return

    print(f"Found {len(files)} files to process: {files}\n")

    for fname in sorted(files):
        fpath = os.path.join(samples_dir, fname)
        print("=" * 60)
        print(f"PROCESSING: {fname}")
        print("=" * 60)
        try:
            row = process_single_sheet(fpath)
            print(f"Quiz: {row['Quiz']} | Set: {row['Set']}")
            print(f"Student Name: {row['Name']} (Expected: {os.path.splitext(fname)[0]})")
            print(f"Registration No: {row['Reg No']}")
            print(f"Correct: {row['Correct']} | Incorrect: {row['Incorrect']} | Unattempted: {row['Unattempted']} | Invalid: {row['Invalid']}")
            print(f"Score: {row['Total Marks']} / 16 ({row['Percentage']}%) | Grade: {row['Grade']}")
            
            # Print individual answers
            part1_ans = [f"Q{i:02d}:{row[f'Part1_Q{i:02d}']}" for i in range(1, 9)]
            part2_ans = [f"Q{i:02d}:{row[f'Part2_Q{i:02d}']}" for i in range(1, 9)]
            print("Part-I Answers : ", " ".join(part1_ans))
            print("Part-II Answers: ", " ".join(part2_ans))
            
            # Print full grade report from the raw object
            print("\nGrade Report Summary:")
            print(row["_report"].student_info)
            print("-" * 60)
        except Exception as e:
            print(f"FAILED to process {fname}: {e}")
            import traceback
            traceback.print_exc()
        print("\n")

if __name__ == "__main__":
    main()
