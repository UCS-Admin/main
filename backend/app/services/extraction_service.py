import re
from pathlib import Path

import pdfplumber
import pytesseract
from PIL import Image


def extract_pdf_text(file_path: str) -> tuple[str, bool]:
    full_text = []
    scanned = False
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if text.strip():
                full_text.append(text)
            else:
                scanned = True
                image = page.to_image(resolution=200).original
                if not isinstance(image, Image.Image):
                    image = Image.open(image)
                full_text.append(pytesseract.image_to_string(image))
    return "\n".join(full_text), scanned


def split_question_blocks(text: str) -> list[str]:
    pattern = r"(?=(?:Q\.?\s*\d+|\(a\)|OR|Marks))"
    blocks = [b.strip() for b in re.split(pattern, text) if b.strip()]
    return blocks


def ensure_upload_dir() -> Path:
    path = Path("uploads")
    path.mkdir(parents=True, exist_ok=True)
    return path



def infer_blueprint_from_text(text: str) -> dict:
    """Heuristic AI-like parser for admin uploaded past papers."""
    blocks = split_question_blocks(text)
    mcq_count = sum(1 for b in blocks if any(k in b.lower() for k in ["(a)", "option", "mcq"]))
    long_count = max(0, len(blocks) - mcq_count)
    total_marks = max(10, mcq_count * 1 + long_count * 5)
    return {
        "totalMarks": total_marks,
        "duration": 120,
        "difficultyRatio": {"easy": 30, "medium": 50, "hard": 20},
        "sections": [
            {"name": "Section A", "type": "MCQ", "count": mcq_count or 5, "marksEach": 1},
            {"name": "Section B", "type": "LONG", "count": long_count or 3, "marksEach": 5},
        ],
    }
