# main.py — DoseAI Streamlit Frontend
# Run with: streamlit run streamlit_ui/main.py

import streamlit as st
import requests
import json

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="DoseAI – Smart Medicine Info",
    page_icon="💊",
    layout="centered"
)

# ── CONSTANTS ─────────────────────────────────────────────────
BACKEND_URL = "http://localhost:5000"

# ── HELPER FUNCTIONS ──────────────────────────────────────────
def fetch_medicine(name: str) -> dict:
    """Calls our Flask backend and returns medicine data."""
    try:
        response = requests.get(
            f"{BACKEND_URL}/medicine/{name.strip()}",
            timeout=10
        )
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is Flask running? (python run.py)"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def fetch_local_list() -> list:
    """Fetches list of locally available medicines for suggestions."""
    try:
        response = requests.get(f"{BACKEND_URL}/medicines/local", timeout=5)
        data = response.json()
        return [m["name"] for m in data.get("medicines", [])]
    except:
        return []


def display_medicine_card(info: dict):
    """Renders a clean medicine info card."""
    
    st.markdown(f"## 💊 {info.get('name', 'Unknown')}")
    
    source = info.get("source", "unknown")
    if source == "local":
        st.success("✅ Source: Local Database (Indian Medicine)")
    else:
        st.info("🌐 Source: OpenFDA API (US Database)")
    
    st.divider()
    
    # Usage
    with st.expander("📋 Usage / What it's for", expanded=True):
        st.write(info.get("usage", "Not available"))
    
    # Dosage
    with st.expander("💉 Dosage & Administration", expanded=True):
        st.write(info.get("dosage", "Not available"))
    
    # Side Effects
    with st.expander("⚠️ Side Effects"):
        st.write(info.get("side_effects", "Not available"))
    
    # Overdose
    with st.expander("🚨 Overdose Risk"):
        st.warning(info.get("overdose", "Not available"))
    
    # Warnings
    with st.expander("🔴 Warnings"):
        st.error(info.get("warnings", "Not available"))


# ── MAIN UI ───────────────────────────────────────────────────
def main():
    
    # Header
    st.title("🏥 DoseAI")
    st.subheader("Smart Medicine Information System")
    st.caption("Search any medicine to get usage, dosage, side effects & more.")
    
    st.divider()
    
    # Show locally available medicines as quick suggestions
    local_medicines = fetch_local_list()
    if local_medicines:
        st.markdown("**💡 Quick search (local database):**")
        cols = st.columns(len(local_medicines))
        for i, med in enumerate(local_medicines):
            if cols[i].button(med, key=f"btn_{i}"):
                st.session_state["search_query"] = med.lower()
    
    st.divider()
    
    # Search bar
    search_input = st.text_input(
        "🔍 Enter medicine name",
        value=st.session_state.get("search_query", ""),
        placeholder="e.g. ibuprofen, dolo 650, metformin...",
        key="search_input"
    )
    
    search_btn = st.button("Search 💊", type="primary")
    
    # Trigger search
    if search_btn and search_input.strip():
        with st.spinner(f"Looking up '{search_input}'..."):
            result = fetch_medicine(search_input)
        
        st.divider()
        
        if "error" in result:
            st.error(f"❌ {result['error']}")
            if "suggestion" in result:
                st.info(f"💡 {result['suggestion']}")
        else:
            display_medicine_card(result)
            
            # Raw JSON toggle (useful for developers)
            with st.expander("🛠️ View Raw JSON (Developer Mode)"):
                st.json(result)
    
    elif search_btn and not search_input.strip():
        st.warning("⚠️ Please enter a medicine name before searching.")
    
    # Footer
    st.divider()
    st.caption("⚕️ DoseAI is for informational purposes only. Always consult a doctor or pharmacist.")


if __name__ == "__main__":
    main()

    # Add this import at the top
import subprocess
import sys

# Add this new function
def speak_section(medicine_info: dict, language: str, section: str):
    """Calls the voice assistant to speak a section."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/speak",
            json={
                "medicine_info": medicine_info,
                "language": language,
                "section": section
            },
            timeout=15
        )
        result = response.json()
        if "error" in result:
            st.error(f"Voice error: {result['error']}")
        else:
            st.success("🔊 Playing audio...")
    except Exception as e:
        st.error(f"Could not connect to voice service: {e}")


# Replace your display_medicine_card function with this updated version:
def display_medicine_card(info: dict):
    """Renders medicine info card with voice controls."""
    
    st.markdown(f"## 💊 {info.get('name', 'Unknown')}")
    
    source = info.get("source", "unknown")
    if source == "local":
        st.success("✅ Source: Local Database (Indian Medicine)")
    else:
        st.info("🌐 Source: OpenFDA API")
    
    # ── VOICE CONTROLS ────────────────────────────────────────
    st.markdown("### 🔊 Listen to this information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        language = st.selectbox(
            "Choose Language",
            ["English", "Hindi", "Kannada"],
            key="lang_select"
        )
    
    with col2:
        section = st.selectbox(
            "Choose Section to Read",
            ["summary", "dosage", "side_effects", "warnings"],
            key="section_select"
        )
    
    if st.button("▶️ Read Aloud", type="primary"):
        with st.spinner("Generating audio..."):
            speak_section(info, language, section)
    
    st.divider()
    
    # ── INFO SECTIONS ─────────────────────────────────────────
    with st.expander("📋 Usage / What it's for", expanded=True):
        st.write(info.get("usage", "Not available"))
    
    with st.expander("💉 Dosage & Administration", expanded=True):
        st.write(info.get("dosage", "Not available"))
    
    with st.expander("⚠️ Side Effects"):
        st.write(info.get("side_effects", "Not available"))
    
    with st.expander("🚨 Overdose Risk"):
        st.warning(info.get("overdose", "Not available"))
    
    with st.expander("🔴 Warnings"):
        st.error(info.get("warnings", "Not available"))
    
    with st.expander("🛠️ View Raw JSON (Developer Mode)"):
        st.json(info)