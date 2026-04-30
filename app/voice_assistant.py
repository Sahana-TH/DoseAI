# voice_assistant.py
# Converts medicine information text into spoken audio.
# Supports English, Hindi, and Kannada using Google TTS.

from gtts import gTTS
import pygame
import os
import time
import hashlib

# ── LANGUAGE CONFIG ───────────────────────────────────────────
SUPPORTED_LANGUAGES = {
    "English":  "en",
    "Hindi":    "hi",
    "Kannada":  "kn"
}

# Where audio files are saved
AUDIO_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'audio')


def ensure_audio_dir():
    """Creates the audio directory if it doesn't exist."""
    os.makedirs(AUDIO_DIR, exist_ok=True)


def generate_audio_filename(text: str, lang_code: str) -> str:
    """
    Generates a unique filename based on text content + language.
    Uses hashing so the same text+language reuses the same file (caching).
    
    Example: "ibuprofen_en_a3f9c1.mp3"
    """
    hash_str = hashlib.md5(f"{text}{lang_code}".encode()).hexdigest()[:8]
    return os.path.join(AUDIO_DIR, f"medicine_{lang_code}_{hash_str}.mp3")


def text_to_speech(text: str, language: str = "English") -> dict:
    """
    Converts text to speech and saves as MP3.
    
    Args:
        text (str): The text to speak
        language (str): "English", "Hindi", or "Kannada"
    
    Returns:
        dict: {"success": True, "filepath": "..."} or {"error": "..."}
    """
    
    ensure_audio_dir()
    
    # Validate language
    if language not in SUPPORTED_LANGUAGES:
        return {"error": f"Language '{language}' not supported. Choose from: {list(SUPPORTED_LANGUAGES.keys())}"}
    
    lang_code = SUPPORTED_LANGUAGES[language]
    
    # Clean text — remove special characters that sound bad when read aloud
    clean_text = text.replace("*", "").replace("#", "").replace("–", "-")
    clean_text = clean_text[:500]  # Limit length to avoid very long audio
    
    # Generate filepath
    filepath = generate_audio_filename(clean_text, lang_code)
    
    # Check cache — if file already exists, skip generation
    if os.path.exists(filepath):
        return {"success": True, "filepath": filepath, "cached": True}
    
    try:
        # Generate speech using gTTS
        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        tts.save(filepath)
        
        return {"success": True, "filepath": filepath, "cached": False}
    
    except Exception as e:
        return {"error": f"Failed to generate audio: {str(e)}"}


def play_audio(filepath: str) -> dict:
    """
    Plays an MP3 file using pygame.
    
    Args:
        filepath (str): Path to the MP3 file
    
    Returns:
        dict: {"success": True} or {"error": "..."}
    """
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        
        # Wait for audio to finish playing
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        pygame.mixer.quit()
        return {"success": True}
    
    except Exception as e:
        return {"error": f"Failed to play audio: {str(e)}"}


def speak_medicine_info(medicine_info: dict, language: str = "English", 
                         section: str = "summary") -> dict:
    """
    High-level function: Takes medicine info dict and speaks a section.
    
    Args:
        medicine_info (dict): The medicine data from Flask API
        language (str): "English", "Hindi", or "Kannada"
        section (str): "summary", "dosage", "side_effects", "warnings"
    
    Returns:
        dict: result of play_audio
    """
    
    name = medicine_info.get("name", "this medicine")
    
    # Build the text to speak based on section
    if section == "summary":
        text = f"{name}. {medicine_info.get('usage', 'Usage information not available.')[:300]}"
    
    elif section == "dosage":
        text = f"Dosage for {name}: {medicine_info.get('dosage', 'Dosage information not available.')[:300]}"
    
    elif section == "side_effects":
        text = f"Side effects of {name}: {medicine_info.get('side_effects', 'Not available.')[:300]}"
    
    elif section == "warnings":
        text = f"Warning for {name}: {medicine_info.get('warnings', 'Not available.')[:300]}"
    
    else:
        return {"error": f"Unknown section '{section}'."}
    
    # Generate audio file
    result = text_to_speech(text, language)
    
    if "error" in result:
        return result
    
    # Play it
    return play_audio(result["filepath"])


# ── TEST BLOCK ────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing Voice Assistant...")
    
    test_info = {
        "name": "Paracetamol",
        "usage": "Used to relieve mild to moderate pain and reduce fever.",
        "dosage": "Adults take one tablet every four to six hours. Do not exceed four tablets in 24 hours.",
        "side_effects": "Generally well tolerated. Rare side effects include nausea and skin reactions.",
        "warnings": "Do not take with alcohol. Avoid in liver disease."
    }
    
    print("\n🔊 Speaking in English...")
    speak_medicine_info(test_info, language="English", section="summary")
    
    print("🔊 Speaking dosage in Hindi...")
    speak_medicine_info(test_info, language="Hindi", section="dosage")
    
    print("✅ Voice test complete!")