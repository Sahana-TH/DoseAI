# scanner.py
# Handles image capture and OCR text extraction from medicine strips.
# Pipeline: Image → Preprocess → OCR → Extract medicine name → Lookup

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import re
import os

# ── WINDOWS ONLY: Set Tesseract path ─────────────────────────
# Uncomment and update this line if you're on Windows:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """
    Enhances image quality before OCR.
    Better image = better text recognition.
    
    Pipeline:
    1. Convert to grayscale (removes color noise)
    2. Increase contrast
    3. Apply threshold (makes text black, background white)
    4. Remove noise
    """
    
    # Step 1: Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Step 2: Increase contrast using CLAHE
    # (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)
    
    # Step 3: Apply Otsu's thresholding
    # Automatically finds the best threshold value
    _, thresh = cv2.threshold(
        contrast, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    
    # Step 4: Remove small noise with morphological operations
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return cleaned


def extract_text_from_image(image_input) -> dict:
    """
    Main OCR function. Accepts file path or numpy array.
    
    Args:
        image_input: filepath (str) OR numpy array (from webcam)
    
    Returns:
        dict: {"raw_text": "...", "medicine_candidates": [...]}
    """
    
    try:
        # Load image based on input type
        if isinstance(image_input, str):
            # File path provided
            if not os.path.exists(image_input):
                return {"error": f"Image file not found: {image_input}"}
            image = cv2.imread(image_input)
        
        elif isinstance(image_input, np.ndarray):
            # Numpy array from webcam
            image = image_input
        
        else:
            # PIL Image (from Streamlit file uploader)
            image = cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)
        
        if image is None:
            return {"error": "Could not load image. Try a clearer photo."}
        
        # Preprocess for better OCR
        processed = preprocess_image(image)
        
        # Convert back to PIL for pytesseract
        pil_image = Image.fromarray(processed)
        
        # Run OCR
        # config: psm 6 = assume uniform block of text (good for medicine strips)
        raw_text = pytesseract.image_to_string(
            pil_image,
            config='--psm 6 --oem 3'
        )
        
        # Extract medicine name candidates
        candidates = extract_medicine_candidates(raw_text)
        
        return {
            "raw_text": raw_text.strip(),
            "medicine_candidates": candidates
        }
    
    except pytesseract.TesseractNotFoundError:
        return {
            "error": "Tesseract OCR engine not found. Please install it.",
            "help": "Windows: https://github.com/UB-Mannheim/tesseract/wiki | Mac: brew install tesseract"
        }
    
    except Exception as e:
        return {"error": f"OCR failed: {str(e)}"}


def extract_medicine_candidates(raw_text: str) -> list:
    """
    Intelligently extracts likely medicine names from OCR text.
    
    Strategy:
    - Medicine names are usually the LARGEST text (first lines)
    - They are typically 4-20 characters long
    - They often appear before dosage numbers
    - Filter out common non-medicine words
    """
    
    # Words that are NOT medicine names
    IGNORE_WORDS = {
        "tablets", "tablet", "capsules", "capsule", "syrup",
        "injection", "mg", "ml", "each", "contains", "manufactured",
        "store", "below", "keep", "children", "reach", "use",
        "before", "expiry", "batch", "mfg", "exp", "ltd", "pvt",
        "india", "pharma", "laboratories", "lab", "healthcare"
    }
    
    lines = raw_text.split('\n')
    candidates = []
    
    for line in lines[:8]:  # Focus on first 8 lines (medicine name is usually at top)
        line = line.strip()
        
        if len(line) < 3 or len(line) > 50:
            continue
        
        # Remove numbers and special characters for name extraction
        words = re.findall(r'[A-Za-z]+', line)
        
        for word in words:
            word_lower = word.lower()
            
            # Skip ignored words and very short words
            if word_lower in IGNORE_WORDS or len(word) < 3:
                continue
            
            # Skip all-uppercase short words (likely abbreviations)
            if word.isupper() and len(word) <= 3:
                continue
            
            candidates.append(word.title())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_candidates = []
    for c in candidates:
        if c.lower() not in seen:
            seen.add(c.lower())
            unique_candidates.append(c)
    
    return unique_candidates[:5]  # Return top 5 candidates


def capture_from_webcam() -> np.ndarray:
    """
    Captures a single frame from the default webcam.
    Used for testing outside of Streamlit.
    
    Returns:
        numpy array of the captured frame
    """
    cap = cv2.VideoCapture(0)  # 0 = default camera
    
    if not cap.isOpened():
        return None
    
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        return frame
    return None


# ── TEST BLOCK ────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing OCR Scanner...")
    print("This test uses your webcam — hold a medicine strip in front of camera")
    
    frame = capture_from_webcam()
    
    if frame is None:
        print("❌ Webcam not accessible. Test with an image file instead:")
        print("   Modify this block to use: extract_text_from_image('path/to/medicine.jpg')")
    else:
        print("📸 Frame captured! Running OCR...")
        result = extract_text_from_image(frame)
        
        if "error" in result:
            print(f"❌ {result['error']}")
        else:
            print(f"\n📝 Raw OCR Text:\n{result['raw_text']}")
            print(f"\n💊 Medicine Candidates: {result['medicine_candidates']}")