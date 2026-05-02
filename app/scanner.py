# scanner.py
# Handles image preprocessing and OCR text extraction.
# Improved accuracy with grayscale, thresholding, and noise removal.

import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
import os
import sys

# ── AUTO-DETECT Tesseract path ────────────────────────────────
# Windows
if sys.platform == "win32":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Linux/Render — tesseract is in PATH after apt-get install
# No need to set path on Linux

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
        config_block  = "--psm 6 --oem 3"
        config_sparse = "--psm 11 --oem 3"

        # Try on processed image
        text_block  = pytesseract.image_to_string(processed_image, config=config_block)
        text_sparse = pytesseract.image_to_string(processed_image, config=config_sparse)
        
        # Try on raw unprocessed image (sometimes preprocessing destroys text in bad lighting)
        text_raw = pytesseract.image_to_string(pil_image, config=config_sparse)

        # Use whichever gave more text
        texts = [text_block, text_sparse, text_raw]
        raw_text = max(texts, key=len).strip()

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
    
    # Extended list of common medicines to match against
    KNOWN_MEDICINES = {
        "paracetamol": "Paracetamol",
        "dolo": "Dolo 650",
        "dolo 650": "Dolo 650",
        "dolo-650": "Dolo 650",
        "ibuprofen": "Ibuprofen",
        "crocin": "Crocin",
        "azithromycin": "Azithromycin",
        "azithral": "Azithromycin",
        "metformin": "Metformin",
        "glycomet": "Metformin",
        "pantoprazole": "Pantoprazole",
        "amoxicillin": "Amoxicillin",
        "cetirizine": "Cetirizine",
        "omeprazole": "Omeprazole",
        "aspirin": "Aspirin",
        "combiflam": "Combiflam",
        "sinarest": "Sinarest",
        "allegra": "Allegra",
    }
    
    # ── STEP 1: Direct exact match in the raw text ─────────────
    for keyword, display_name in KNOWN_MEDICINES.items():
        if keyword in text_lower:
            if display_name not in candidates:
                candidates.append(display_name)
                
    # ── STEP 2: Fuzzy matching against known medicines ─────────
    # Helps correct minor OCR typos (e.g. "Paracetamo1" -> "Paracetamol")
    words = re.findall(r'[a-z0-9]{4,}', text_lower)
    known_keys = list(KNOWN_MEDICINES.keys())
    
    for word in words:
        if word.isdigit():
            continue
        # Use difflib to find close matches
        cutoff_val = 0.7 if len(word) <= 5 else 0.8
        matches = difflib.get_close_matches(word, known_keys, n=1, cutoff=cutoff_val)
        if matches:
            matched_key = matches[0]
            display_name = KNOWN_MEDICINES[matched_key]
            if display_name not in candidates:
                candidates.append(display_name)
    
    # ── STEP 3: Regex pattern for "Name + Number" combos ──────
    combo_matches = re.findall(
        r'([A-Za-z]{3,20})\s*[\-]?\s*(\d{2,4})\s*(mg|ml|g|mcg)?',
        raw_text, re.IGNORECASE
    )
    
    IGNORE_WORDS = {
        "tablets", "tablet", "capsules", "capsule", "each",
        "contains", "store", "keep", "children", "before",
        "expiry", "batch", "mfg", "exp", "ltd", "pvt", "private", "limited",
        "india", "pharma", "strip", "pack", "box", "use",
        "the", "and", "with", "from", "drug", "price",
        "read", "schedule", "prescription", "side", "uses",
        "dosage", "warning", "mrp", "date", "rs", "inclusive",
        "taxes", "all", "directed", "physician", "cool",
        "dry", "place", "protect", "light", "moisture",
        "manufacturing", "manufactured", "marketed", "registered",
        "trademark", "composition", "base", "colour",
        "approved", "colours", "mg", "ml"
    }

    for match in combo_matches:
        name  = match[0].strip().title()
        num   = match[1].strip()
        combo = f"{name} {num}"
        if name.lower() not in IGNORE_WORDS and len(name) >= 3:
            if combo not in candidates:
                candidates.append(combo)

    # ── STEP 4: If nothing found yet, return top words ────────
    if not candidates:
        lines = raw_text.split('\n')
        for line in lines[:8]:
            line_words = re.findall(r'[A-Za-z]{4,20}', line)
            for word in line_words:
                if word.lower() not in IGNORE_WORDS:
                    titled = word.title()
                    if titled not in candidates:
                        candidates.append(titled)

    # Remove duplicates but preserve order
    seen   = set()
    unique = []
    for c in candidates:
        if c.lower() not in seen:
            seen.add(c.lower())
            unique.append(c)

    return unique[:6]