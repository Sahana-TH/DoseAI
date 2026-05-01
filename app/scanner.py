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
    
    candidates = []
    text_lower = raw_text.lower()
    
    # ── STEP 1: Direct keyword search in raw text ─────────────
    # These are checked character by character in the OCR output
    DIRECT_SEARCH = [
        ("paracetamol",  "Paracetamol"),
        ("dolo",         "Dolo 650"),
        ("dolo-650",     "Dolo 650"),
        ("dolo 650",     "Dolo 650"),
        ("ibuprofen",    "Ibuprofen"),
        ("crocin",       "Crocin"),
        ("azithromycin", "Azithromycin"),
        ("metformin",    "Metformin"),
        ("pantoprazole", "Pantoprazole"),
        ("amoxicillin",  "Amoxicillin"),
        ("cetirizine",   "Cetirizine"),
        ("omeprazole",   "Omeprazole"),
        ("aspirin",      "Aspirin"),
        ("combiflam",    "Combiflam"),
        ("sinarest",     "Sinarest"),
        ("allegra",      "Allegra"),
    ]
    
    for keyword, display_name in DIRECT_SEARCH:
        if keyword in text_lower:
            if display_name not in candidates:
                candidates.append(display_name)
    
    # ── STEP 2: Regex pattern for "Name + Number" combos ──────
    combo_matches = re.findall(
        r'([A-Za-z]{3,20})\s*[\-]?\s*(\d{2,4})\s*(mg|ml|g|mcg)?',
        raw_text, re.IGNORECASE
    )
    for match in combo_matches:
        name  = match[0].strip().title()
        num   = match[1].strip()
        combo = f"{name} {num}"
        IGNORE = {"tablets", "tablet", "each", "strip", "pack", "price", "batch", "mfg", "exp"}
        if name.lower() not in IGNORE and len(name) >= 3:
            if combo not in candidates:
                candidates.append(combo)

    # ── STEP 3: If nothing found yet, return top words ────────
    if not candidates:
        IGNORE_WORDS = {
            "tablets", "tablet", "capsules", "capsule", "each",
            "contains", "store", "keep", "children", "before",
            "expiry", "batch", "mfg", "exp", "ltd", "pvt",
            "india", "pharma", "strip", "pack", "box", "use",
            "the", "and", "with", "from", "drug", "price",
            "read", "schedule", "prescription", "side", "uses"
        }
        lines = raw_text.split('\n')
        for line in lines[:8]:
            words = re.findall(r'[A-Za-z]{4,20}', line)
            for word in words:
                if word.lower() not in IGNORE_WORDS:
                    titled = word.title()
                    if titled not in candidates:
                        candidates.append(titled)

    # Remove duplicates
    seen   = set()
    unique = []
    for c in candidates:
        if c.lower() not in seen:
            seen.add(c.lower())
            unique.append(c)

    return unique[:6]