# main.py — DoseAI Modern UI with multilingual voice
# Run: streamlit run streamlit_ui/main.py

import streamlit as st
import requests

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="DoseAI – Smart Medicine Info",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "http://127.0.0.1:5000"

# ── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
/* Overall background */
.main { background-color: #0f1117; }

/* Medicine card */
.medicine-card {
    background: linear-gradient(135deg, #1e2130, #252840);
    border-radius: 16px;
    padding: 24px;
    margin: 16px 0;
    border: 1px solid #3a3f5c;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

/* Section cards */
.section-card {
    background: #1a1d2e;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 10px 0;
    border-left: 4px solid #4f8ef7;
}

.section-card.warning  { border-left-color: #f7c948; }
.section-card.danger   { border-left-color: #f74f4f; }
.section-card.success  { border-left-color: #4fba6f; }
.section-card.info     { border-left-color: #4f8ef7; }

/* Source badge */
.badge-local  {
    background: #1a3a2a; color: #4fba6f;
    padding: 4px 12px; border-radius: 20px;
    font-size: 13px; font-weight: 600;
    display: inline-block; margin-bottom: 12px;
}
.badge-api {
    background: #1a2a3a; color: #4f8ef7;
    padding: 4px 12px; border-radius: 20px;
    font-size: 13px; font-weight: 600;
    display: inline-block; margin-bottom: 12px;
}

/* Medicine name title */
.medicine-title {
    font-size: 2rem; font-weight: 800;
    color: #ffffff; margin: 8px 0 16px 0;
}

/* Section heading */
.section-heading {
    font-size: 0.85rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
    color: #8892b0; margin-bottom: 8px;
}

/* Voice section */
.voice-section {
    background: #151823;
    border-radius: 12px;
    padding: 20px;
    margin-top: 20px;
    border: 1px solid #2a2f4a;
}

/* Divider */
.custom-divider {
    border: none; border-top: 1px solid #2a2f4a;
    margin: 20px 0;
}

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def search_medicine(name: str) -> dict:
    try:
        response = requests.get(
            f"{BACKEND_URL}/medicine/{name.strip()}",
            timeout=15
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error {response.status_code}: {response.text}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Flask backend. Is `python run.py` running?"}
    except Exception as e:
        return {"error": str(e)}


def speak_section(medicine_info: dict, language: str, section: str):
    with st.spinner(f"🔄 Generating {language} audio..."):
        try:
            response = requests.post(
                url     = f"{BACKEND_URL}/speak",
                json    = {
                    "medicine_info": medicine_info,
                    "language":      language,
                    "section":       section,
                },
                timeout = 30
            )
            if response.status_code == 200:
                audio_bytes = response.content
                if len(audio_bytes) > 0:
                    st.success(f"✅ Audio ready in {language}")
                    st.audio(audio_bytes, format="audio/mp3")
                else:
                    st.error("❌ Empty audio returned.")
            else:
                st.error(f"❌ Flask error {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to Flask backend.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


def render_medicine_card(info: dict):
    """Renders a modern card UI for medicine info."""

    source = info.get("source", "unknown")

    # Source badge
    if source == "local":
        st.markdown('<span class="badge-local">✅ Local Database — Indian Medicine</span>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-api">🌐 OpenFDA API</span>',
                    unsafe_allow_html=True)

    # Medicine name
    st.markdown(f'<div class="medicine-title">💊 {info.get("name", "Medicine")}</div>',
                unsafe_allow_html=True)

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # ── Info sections ─────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        # Usage
        st.markdown("""
        <div class="section-card success">
            <div class="section-heading">📋 Usage / What it's for</div>
        </div>
        """, unsafe_allow_html=True)
        st.write(info.get("usage", "Not available"))

        st.markdown("<br>", unsafe_allow_html=True)

        # Side Effects
        st.markdown("""
        <div class="section-card warning">
            <div class="section-heading">⚠️ Side Effects</div>
        </div>
        """, unsafe_allow_html=True)
        st.write(info.get("side_effects", "Not available"))

    with col2:
        # Dosage
        st.markdown("""
        <div class="section-card info">
            <div class="section-heading">💉 Dosage & Administration</div>
        </div>
        """, unsafe_allow_html=True)
        st.write(info.get("dosage", "Not available"))

        st.markdown("<br>", unsafe_allow_html=True)

        # Warnings
        st.markdown("""
        <div class="section-card danger">
            <div class="section-heading">🚨 Overdose & Warnings</div>
        </div>
        """, unsafe_allow_html=True)
        st.write(info.get("overdose", "Not available"))
        st.write(info.get("warnings", "Not available"))

    # ── Voice Section ─────────────────────────────────────────
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown('<div class="voice-section">', unsafe_allow_html=True)
    st.markdown("### 🔊 Voice Assistant")
    st.caption("Select language and section, then click a button to hear it read aloud.")

    vcol1, vcol2 = st.columns(2)
    with vcol1:
        language = st.selectbox(
            "🌐 Language",
            ["English", "Hindi", "Kannada"],
            key="lang_select"
        )
    with vcol2:
        section = st.selectbox(
            "📂 Section to Read",
            ["summary", "dosage", "side_effects", "overdose", "warnings", "full"],
            key="section_select"
        )

    # Voice buttons
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button("▶️ Summary", use_container_width=True):
            speak_section(info, language, "summary")
    with b2:
        if st.button("▶️ Dosage", use_container_width=True):
            speak_section(info, language, "dosage")
    with b3:
        if st.button("▶️ Side Effects", use_container_width=True):
            speak_section(info, language, "side_effects")
    with b4:
        if st.button("▶️ Full Info", use_container_width=True):
            speak_section(info, language, "full")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Raw JSON (dev mode) ───────────────────────────────────
    with st.expander("🛠️ Raw JSON — Developer Mode"):
        st.json(info)


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/pill.png", width=60)
    st.title("DoseAI")
    st.caption("Smart Medicine Information System")
    st.markdown("---")

    st.markdown("#### 💡 Quick Search")
    quick_medicines = ["Dolo 650", "Crocin", "Pantoprazole", "Azithromycin", "Metformin"]
    for med in quick_medicines:
        if st.button(med, key=f"sidebar_{med}", use_container_width=True):
            st.session_state["search_query"] = med
            st.session_state["auto_search"]  = True

    st.markdown("---")
    st.markdown("#### ℹ️ About")
    st.caption("DoseAI helps you understand medicines — usage, dosage, side effects — read aloud in English, Hindi, or Kannada.")
    st.caption("⚕️ Always consult a doctor for medical advice.")


# ─────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────
def main():

    # Header
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px 0;'>
        <span style='font-size:3rem;'>💊</span>
        <h1 style='color:#ffffff; margin:0; font-size:2.5rem; font-weight:800;'>
            DoseAI
        </h1>
        <p style='color:#8892b0; font-size:1rem; margin-top:6px;'>
            Smart Medicine Information System
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2 = st.tabs(["🔍 Search Medicine", "📷 Scan Medicine Strip"])

    # ══════════════════════════════════════════════════════════
    # TAB 1 — Search
    # ══════════════════════════════════════════════════════════
    with tab1:

        # Search bar
        col1, col2 = st.columns([5, 1])
        with col1:
            default_query = st.session_state.get("search_query", "")
            search_input  = st.text_input(
                label            = "Medicine Name",
                value            = default_query,
                placeholder      = "e.g. Dolo 650, Ibuprofen, Metformin...",
                label_visibility = "collapsed"
            )
        with col2:
            search_btn = st.button("🔍 Search", type="primary", use_container_width=True)

        # Auto-search when sidebar button clicked
        auto_search = st.session_state.pop("auto_search", False)

        if (search_btn or auto_search) and search_input.strip():
            with st.spinner(f"🔍 Looking up '{search_input}'..."):
                result = search_medicine(search_input.strip())

            if "error" in result:
                st.error(f"❌ {result['error']}")
                if "suggestion" in result:
                    st.info(f"💡 {result['suggestion']}")
            else:
                st.session_state["medicine_info"] = result
                st.session_state["searched"]       = True

        elif (search_btn or auto_search) and not search_input.strip():
            st.warning("⚠️ Please enter a medicine name first.")

        # Display result card
        if st.session_state.get("searched") and "medicine_info" in st.session_state:
            render_medicine_card(st.session_state["medicine_info"])

    # ══════════════════════════════════════════════════════════
    # TAB 2 — Scan Strip
    # ══════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 📷 Scan Medicine Strip")
        st.caption("Upload a clear photo of a medicine strip or box. DoseAI will read the name automatically.")

        uploaded = st.file_uploader(
            "Upload medicine image",
            type=["jpg", "jpeg", "png", "bmp"],
            help="Take a well-lit photo of the medicine strip and upload it here."
        )

        if uploaded:
            st.image(uploaded, caption="Uploaded Image", width=400)

            if st.button("🔍 Scan & Identify", type="primary"):
                with st.spinner("🔄 Running OCR on image..."):
                    try:
                        files    = {"image": (uploaded.name, uploaded.getvalue(), uploaded.type)}
                        response = requests.post(
                            f"{BACKEND_URL}/scan", files=files, timeout=30
                        )
                        scan_result = response.json()
                    except Exception as e:
                        scan_result = {"error": str(e)}

                if "error" in scan_result:
                    st.error(f"❌ Scan failed: {scan_result['error']}")
                else:
                    st.success("✅ OCR Complete!")

                    with st.expander("📝 Raw OCR Text"):
                        st.code(scan_result.get("raw_text", "Nothing detected"))

                    candidates = scan_result.get("medicine_candidates", [])

                    if candidates:
                        st.markdown("### 💊 Detected Names — Click to Look Up:")
                        for candidate in candidates:
                            if st.button(f"🔍 {candidate}", key=f"scan_{candidate}"):
                                with st.spinner(f"Looking up {candidate}..."):
                                    med_result = search_medicine(candidate)
                                if "error" not in med_result:
                                    st.session_state["medicine_info"] = med_result
                                    st.session_state["searched"]       = True
                                    st.info("✅ Switching to Search tab — click 🔍 Search Medicine tab above.")
                                else:
                                    st.error(f"❌ {med_result['error']}")
                    else:
                        st.warning("⚠️ No medicine names detected. Try a clearer image.")


if __name__ == "__main__":
    main()