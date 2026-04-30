# scanner.py
# Handles image preprocessing and OCR text extraction.
# Improved accuracy with grayscale, thresholding, and noise removal.

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import re
import os

# ── WINDOWS ONLY — Uncomment if tesseract not found ──────────
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def preprocess_image(image) -> Image.Image:
    """
    Improves image quality before OCR.
    Accepts PIL Image or numpy array.

    Steps:
    1. Convert to numpy array
    2. Resize if too small
    3. Convert to grayscale
    4. Increase contrast
    5. Apply threshold (black text, white background)
    6. Remove noise
    7. Return as PIL Image
    """

    # Convert PIL to numpy if needed
    if isinstance(image, Image.Image):
        img_array = np.array(image.convert("RGB"))
    else:
        img_array = image

    # Step 1: Resize if image is too small (min 1000px wide)
    h, w = img_array.shape[:2]
    if w < 1000:
        scale  = 1000 / w
        img_array = cv2.resize(
            img_array,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_LINEAR
        )

    # Step 2: Convert to grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    # Step 3: Increase contrast using CLAHE
    clahe    = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)

    # Step 4: Remove noise with gaussian blur
    blurred = cv2.GaussianBlur(contrast, (1, 1), 0)

    # Step 5: Apply Otsu thresholding
    _, thresh = cv2.threshold(
        blurred, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Step 6: Morphological cleanup — removes small dots/noise
    kernel  = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Return as PIL Image for pytesseract
    return Image.fromarray(cleaned)


def extract_text_from_image(image_input) -> dict:
    """
    Main OCR function.
    Accepts PIL Image, numpy array, or file path.

    Returns:
        dict: {
            "raw_text": "...",
            "medicine_candidates": [...]
        }
    """

    try:
        # Load image based on input type
        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                return {"error": f"File not found: {image_input}"}
            pil_image = Image.open(image_input)

        elif isinstance(image_input, np.ndarray):
            pil_image = Image.fromarray(
                cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB)
            )

        elif isinstance(image_input, Image.Image):
            pil_image = image_input

        else:
            return {"error": "Unsupported image format."}

        # Preprocess image
        processed_image = preprocess_image(pil_image)

        # Run OCR with best config for medicine strips
        # psm 6  = assume a uniform block of text
        # psm 11 = sparse text (good for strips with scattered text)
        # We try both and pick the one with more text
        config_block  = "--psm 6 --oem 3"
        config_sparse = "--psm 11 --oem 3"

        text_block  = pytesseract.image_to_string(processed_image, config=config_block)
        text_sparse = pytesseract.image_to_string(processed_image, config=config_sparse)

        # Use whichever gave more text
        raw_text = text_block if len(text_block) >= len(text_sparse) else text_sparse
        raw_text = raw_text.strip()

        if not raw_text:
            return {
                "raw_text": "",
                "medicine_candidates": [],
                "message": "No text detected. Try a clearer, well-lit image."
            }

        # Extract medicine name candidates
        candidates = extract_medicine_candidates(raw_text)

        return {
            "raw_text":            raw_text,
            "medicine_candidates": candidates
        }

    except pytesseract.TesseractNotFoundError:
        return {
            "error": "Tesseract OCR not found. Please install it.",
            "help":  "Windows: https://github.com/UB-Mannheim/tesseract/wiki | Mac: brew install tesseract"
        }

    except Exception as e:
        return {"error": f"OCR failed: {str(e)}"}


def extract_medicine_candidates(raw_text: str) -> list:
    """
    Extracts likely medicine names from OCR text.

    Strategy:
    - Medicine names are usually in the first few lines
    - They are 3-25 characters long
    - Filter out common non-medicine words
    - Return top 5 candidates
    """

    IGNORE_WORDS = {
        "tablets", "tablet", "capsules", "capsule", "syrup",
        "injection", "each", "contains", "manufactured", "marketed",
        "store", "below", "keep", "out", "children", "reach",
        "before", "expiry", "batch", "mfg", "exp", "ltd", "pvt",
        "india", "pharma", "laboratories", "lab", "healthcare",
        "strip", "pack", "box", "use", "only", "not", "for",
        "the", "and", "with", "this", "that", "from", "drug",
        "read", "leaflet", "schedule", "rx", "prescription",
        "composition", "indications", "dosage", "warning"
    }

    lines      = raw_text.split('\n')
    candidates = []

    for line in lines[:10]:  # Top 10 lines
        line = line.strip()
        if not line or len(line) > 60:
            continue

        words = re.findall(r'[A-Za-z]+', line)

        for word in words:
            word_lower = word.lower()

            if word_lower in IGNORE_WORDS:
                continue
            if len(word) < 3 or len(word) > 25:
                continue
            if word.isupper() and len(word) <= 2:
                continue
            # Skip words that are all digits
            if word.isdigit():
                continue

            candidates.append(word.title())

    # Also try to detect "Name + Number" patterns like "Dolo 650", "Crocin 500"
    # This regex finds patterns like "Ibuprofen 400" or "Metformin 500mg"
    combo_pattern = re.findall(
        r'([A-Za-z]{3,20})\s*(\d{2,4})\s*(mg|ml|g)?',
        raw_text,
        re.IGNORECASE
    )
    for match in combo_pattern:
        name   = match[0].title()
        number = match[1]
        combo  = f"{name} {number}"
        if name.lower() not in IGNORE_WORDS:
            candidates.insert(0, combo)  # Add to front — high confidence

    # Remove duplicates while preserving order
    seen   = set()
    unique = []
    for c in candidates:
        if c.lower() not in seen:
            seen.add(c.lower())
            unique.append(c)

    return unique[:6]  # Top 6 candidates