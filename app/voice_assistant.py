# voice_assistant.py
# Converts text to speech with automatic translation support.
# Supports English, Hindi, and Kannada.

from gtts import gTTS
from deep_translator import GoogleTranslator
import os
import hashlib

# ── LANGUAGE CONFIG ───────────────────────────────────────────
SUPPORTED_LANGUAGES = {
    "English": "en",
    "Hindi":   "hi",
    "Kannada": "kn"
}

# Audio files saved here
AUDIO_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'audio')


def ensure_audio_dir():
    os.makedirs(AUDIO_DIR, exist_ok=True)


def translate_text(text: str, target_language: str) -> str:
    """
    Translates text to the target language.
    If language is English or translation fails, returns original text.

    Args:
        text            (str): Text to translate
        target_language (str): "English", "Hindi", or "Kannada"

    Returns:
        str: Translated text
    """
    if target_language == "English":
        return text  # No translation needed

    lang_code = SUPPORTED_LANGUAGES.get(target_language, "en")

    try:
        translated = GoogleTranslator(
            source="en",
            target=lang_code
        ).translate(text[:4500])  # Google limit is 5000 chars
        return translated

    except Exception as e:
        print(f">>> Translation failed ({target_language}): {e}")
        print(">>> Falling back to English")
        return text  # Return original English if translation fails


def text_to_speech(text: str, language: str = "English") -> dict:
    """
    Translates text to selected language, then converts to MP3.

    Args:
        text     (str): English text to speak
        language (str): "English", "Hindi", or "Kannada"

    Returns:
        dict: {"filepath": "path/to/file.mp3"} or {"error": "..."}
    """

    ensure_audio_dir()

    # Validate language
    if language not in SUPPORTED_LANGUAGES:
        return {"error": f"Language '{language}' not supported. Choose: {list(SUPPORTED_LANGUAGES.keys())}"}

    lang_code = SUPPORTED_LANGUAGES[language]

    # Clean text
    clean_text = text.replace("*", "").replace("#", "").replace("–", "-").strip()
    clean_text = clean_text[:500]

    # Step 1: Translate if needed
    print(f">>> Translating to {language}...")
    translated_text = translate_text(clean_text, language)
    print(f">>> Translated: {translated_text[:80]}...")

    # Step 2: Generate unique filename based on translated text + language
    hash_str = hashlib.md5(f"{translated_text}{lang_code}".encode()).hexdigest()[:8]
    filename = f"medicine_{lang_code}_{hash_str}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    # Step 3: Return cached file if exists
    if os.path.exists(filepath):
        print(f">>> Using cached audio: {filename}")
        return {"filepath": filepath}

    # Step 4: Generate audio using gTTS
    try:
        print(f">>> Generating {language} audio...")
        tts = gTTS(text=translated_text, lang=lang_code, slow=False)
        tts.save(filepath)
        print(f">>> Audio saved: {filepath}")
        return {"filepath": filepath}

    except Exception as e:
        return {"error": f"Failed to generate audio: {str(e)}"}


# ── TEST BLOCK ────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing multilingual voice...\n")

    test_text = "Dolo 650 is used to relieve mild to moderate pain and reduce fever."

    for lang in ["English", "Hindi", "Kannada"]:
        print(f"\n--- Testing {lang} ---")
        result = text_to_speech(test_text, lang)
        if "filepath" in result:
            print(f"✅ {lang} audio saved: {result['filepath']}")
        else:
            print(f"❌ Error: {result['error']}")