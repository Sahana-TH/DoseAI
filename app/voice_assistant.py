# filepath: app/voice_assistant.py
import os
from gtts import gTTS

def generate_speech(text, output_file):
    """
    Convert text to speech and save as audio file.
    
    Args:
        text: Text to convert to speech
        output_file: Path to save the audio file
    """
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)
    return output_file

def get_audio_path(filename):
    """Get the full path for an audio file."""
    return os.path.join(os.path.dirname(__file__), '..', 'static', 'audio', filename)