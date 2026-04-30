# DoseAI - Medicine Assistant

AI-powered medicine lookup and voice assistant.

## Setup

```bash
pip install -r requirements.txt
```

## Running

**Flask API:**
```bash
cd app
flask run
```

**Streamlit UI:**
```bash
streamlit run streamlit_ui/main.py
```

## Project Structure

- `app/` - Flask backend (API routes, medicine lookup, voice assistant)
- `streamlit_ui/` - Streamlit frontend
- `data/` - Local medicine database
- `static/audio/` - Generated audio files
- `tests/` - Unit tests