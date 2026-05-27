import os
import sys

# Ensure root and src are on path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from scripts.test_individual_bubbles import debug_bubbles_for_file

if __name__ == "__main__":
    debug_bubbles_for_file("c:/Users/297/Desktop/AI project(cursor)/quiz-scanner/samples/Atif.png")
