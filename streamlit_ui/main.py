# main.py — DoseAI Clean Version (Modern Redesign)
# Run: streamlit run streamlit_ui/main.py

import streamlit as st
import requests
import time

# ── PAGE CONFIG — must be first Streamlit command ─────────────
st.set_page_config(
    page_title = "DoseAI – Smart Medicine Info",
    page_icon  = "💊",
    layout     = "wide"
)

BACKEND_URL = "https://doseai-backend.onrender.com"


# ─────────────────────────────────────────────────────────────
# CSS INJECTION
# ─────────────────────────────────────────────────────────────
def inject_custom_css():
    st.markdown("""
    <style>
    /* Global scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0e1117; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #555; }

    /* Gradient Text Animation */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(-45deg, #FF4B2B, #FF416C, #4A00E0, #8E2DE2);
        background-size: 300% 300%;
        animation: gradientShift 5s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-bottom: 10px;
        display: inline-block;
    }

    /* Typewriter subtitle */
    .typewriter-container {
        display: inline-block;
        overflow: hidden;
        border-right: .15em solid #FF416C;
        white-space: nowrap;
        margin: 0;
        letter-spacing: .05em;
        animation: typing 3s steps(40, end), blink-caret .75s step-end infinite;
        color: #A0AEC0;
        font-size: 1.2rem;
        font-weight: 500;
    }
    @keyframes typing { from { width: 0 } to { width: 100% } }
    @keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: #FF416C; } }

    /* Floating Pill */
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(15deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    .floating-pill {
        display: inline-block;
        animation: float 3s ease-in-out infinite;
        font-size: 3.5rem;
        vertical-align: middle;
        margin-right: 15px;
    }

    /* Card Pop-in Animation */
    @keyframes cardPop {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .animated-card {
        animation: cardPop 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        opacity: 0;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        color: #fff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .animated-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.3);
    }
    
    .delay-1 { animation-delay: 0.1s; }
    .delay-2 { animation-delay: 0.2s; }
    .delay-3 { animation-delay: 0.3s; }
    .delay-4 { animation-delay: 0.4s; }

    /* Card Colors */
    .usage-card { background: linear-gradient(135deg, rgba(13, 59, 30, 0.8), rgba(26, 94, 49, 0.8)); border-left: 5px solid #2ecc71; }
    .dosage-card { background: linear-gradient(135deg, rgba(13, 40, 59, 0.8), rgba(26, 69, 94, 0.8)); border-left: 5px solid #3498db; }
    .side-effects-card { background: linear-gradient(135deg, rgba(59, 43, 13, 0.8), rgba(94, 74, 26, 0.8)); border-left: 5px solid #f1c40f; }
    .warnings-card { background: linear-gradient(135deg, rgba(59, 13, 13, 0.8), rgba(94, 26, 26, 0.8)); border-left: 5px solid #e74c3c; }

    .card-title { font-weight: bold; font-size: 1.1rem; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
    .card-content { font-size: 0.95rem; color: #e2e8f0; line-height: 1.5; }

    /* Search Bar & Buttons Styling */
    [data-testid="stTextInput"] input {
        border-radius: 20px !important;
        border: 2px solid #333 !important;
        padding: 12px 20px !important;
        transition: all 0.3s ease !important;
        background-color: #1e1e1e !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #FF416C !important;
        box-shadow: 0 0 15px rgba(255, 65, 108, 0.3) !important;
    }

    [data-testid="stButton"] button {
        border-radius: 20px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stButton"] button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(255,255,255,0.1);
        border-color: #FF416C;
        color: #FF416C;
    }

    /* Sound Wave Animation */
    @keyframes quiet { 25% { transform: scaleY(.6); } 50% { transform: scaleY(.4); } 75% { transform: scaleY(.8); } }
    @keyframes normal { 25% { transform: scaleY(1); } 50% { transform: scaleY(.4); } 75% { transform: scaleY(.6); } }
    @keyframes loud { 25% { transform: scaleY(1); } 50% { transform: scaleY(.4); } 75% { transform: scaleY(1.2); } }
    .boxContainer {
        display: flex; justify-content: center; align-items: center; height: 30px; gap: 4px; margin: 10px 0;
    }
    .box {
        width: 6px; height: 100%; border-radius: 3px;
        background: linear-gradient(to top, #FF416C, #FF4B2B);
    }
    .box1 { animation: quiet 1.2s ease-in-out infinite; }
    .box2 { animation: normal 1.5s ease-in-out infinite; }
    .box3 { animation: quiet 1.1s ease-in-out infinite; }
    .box4 { animation: loud 1.4s ease-in-out infinite; }
    .box5 { animation: normal 1.3s ease-in-out infinite; }

    /* Tabs styling */
    [data-baseweb="tab"] { transition: all 0.3s ease; border-radius: 8px 8px 0 0; }
    [data-baseweb="tab"]:hover { background-color: rgba(255,255,255,0.05); }

    /* Glowing badge */
    .glow-badge {
        display: inline-block; padding: 4px 12px; border-radius: 12px;
        font-size: 0.8rem; font-weight: bold; margin-bottom: 15px;
    }
    .badge-local { background: rgba(46, 204, 113, 0.15); color: #2ecc71; border: 1px solid rgba(46, 204, 113, 0.4); }
    .badge-api { background: rgba(52, 152, 219, 0.15); color: #3498db; border: 1px solid rgba(52, 152, 219, 0.4); }

    /* Scan animation */
    @keyframes pulse-ring {
        0% { transform: scale(0.8); box-shadow: 0 0 0 0 rgba(255, 65, 108, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 65, 108, 0); }
        100% { transform: scale(0.8); box-shadow: 0 0 0 0 rgba(255, 65, 108, 0); }
    }
    .camera-pulse {
        display: inline-block; animation: pulse-ring 2s infinite; border-radius: 50%;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def search_medicine(name: str) -> dict:
    """Calls Flask /medicine/<name> and returns result."""
    try:
        response = requests.get(f"{BACKEND_URL}/medicine/{name.strip()}", timeout=15)
        if response.status_code == 200: return response.json()
        else: return {"error": f"API error {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Flask backend. Is `python run.py` running?"}
    except Exception as e:
        return {"error": str(e)}


def speak_section(medicine_info: dict, language: str, section: str):
    """Calls Flask /speak and plays audio in Streamlit."""
    with st.spinner(f"Generating {language} audio..."):
        try:
            response = requests.post(
                url     = f"{BACKEND_URL}/speak",
                json    = {"medicine_info": medicine_info, "language": language, "section": section},
                timeout = 30
            )
            if response.status_code == 200:
                audio_bytes = response.content
                if len(audio_bytes) > 0:
                    st.markdown("""
                        <div class="boxContainer">
                            <div class="box box1"></div><div class="box box2"></div>
                            <div class="box box3"></div><div class="box box4"></div>
                            <div class="box box5"></div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.success(f"✅ Playing in {language}")
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                else:
                    st.error("Empty audio returned.")
            else:
                st.error(f"Flask error {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to Flask backend.")
        except Exception as e:
            st.error(f"Error: {str(e)}")


def show_medicine_card(info: dict, key_suffix: str = ""):
    """Shows medicine info in an animated, styled card layout."""

    # Source badge
    source = info.get("source", "")
    if source == "local":
        st.markdown("<div class='glow-badge badge-local'>✅ Source: Local Database (Indian Medicine)</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='glow-badge badge-api'>🌐 Source: OpenFDA API</div>", unsafe_allow_html=True)

    # Medicine name
    st.markdown(f"<h2 style='margin-top:0;'>💊 {info.get('name', 'Medicine')}</h2>", unsafe_allow_html=True)
    st.divider()

    # Two column layout for cards
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="animated-card usage-card delay-1">
            <div class="card-title">📋 Usage</div>
            <div class="card-content">{info.get('usage', 'Not available')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="animated-card side-effects-card delay-3">
            <div class="card-title">⚠️ Side Effects</div>
            <div class="card-content">{info.get('side_effects', 'Not available')}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="animated-card dosage-card delay-2">
            <div class="card-title">💉 Dosage</div>
            <div class="card-content">{info.get('dosage', 'Not available')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="animated-card warnings-card delay-4">
            <div class="card-title">🚨 Overdose & Warnings</div>
            <div class="card-content">
                <b>Overdose:</b> {info.get('overdose', 'Not available')}<br><br>
                <b>Warnings:</b> {info.get('warnings', 'Not available')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Voice section
    st.markdown("### 🔊 Read Aloud")

    vc1, vc2 = st.columns(2)
    with vc1:
        language = st.selectbox("Language", ["English", "Hindi", "Kannada"], key=f"lang_select_{key_suffix}")
    with vc2:
        section = st.selectbox("Section", ["summary", "dosage", "side_effects", "overdose", "warnings", "full"], key=f"section_select_{key_suffix}")

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button("▶️ Summary", use_container_width=True, key=f"btn_sum_{key_suffix}"): speak_section(info, language, "summary")
    with b2:
        if st.button("▶️ Dosage", use_container_width=True, key=f"btn_dos_{key_suffix}"): speak_section(info, language, "dosage")
    with b3:
        if st.button("▶️ Side Effects", use_container_width=True, key=f"btn_sid_{key_suffix}"): speak_section(info, language, "side_effects")
    with b4:
        if st.button("▶️ Full Info", use_container_width=True, key=f"btn_ful_{key_suffix}"): speak_section(info, language, "full")

    st.divider()

    with st.expander("🛠️ Raw JSON (Developer Mode)"):
        st.json(info)


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────

def build_sidebar():
    with st.sidebar:
        st.markdown("<div style='text-align: center;'><span class='floating-pill' style='font-size:2.5rem; margin:0;'>💊</span><h2 style='margin-top:0;'>DoseAI</h2></div>", unsafe_allow_html=True)
        st.caption("<div style='text-align: center;'>Smart Medicine Information</div>", unsafe_allow_html=True)
        st.divider()

        st.markdown("#### 💡 Quick Search")
        quick_list = ["Dolo 650", "Crocin", "Pantoprazole", "Azithromycin", "Metformin"]
        for med in quick_list:
            if st.button(f"💊 {med}", key=f"quick_{med}", use_container_width=True):
                st.session_state["search_query"] = med
                st.session_state["do_search"]    = True

        st.divider()
        st.caption("⚕️ Always consult a doctor for medical advice.")
        
        st.markdown("""
        <div style='position: fixed; bottom: 20px; text-align: center; width: 20%; color: #666; font-size: 0.8rem;'>
            DoseAI Project<br>Created with Streamlit
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    inject_custom_css()
    build_sidebar()

    # ── Header ────────────────────────────────────────────────
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div class="floating-pill">💊</div>
            <div class="hero-title">DoseAI</div>
        </div>
        <div class="typewriter-container">Smart Medicine Information System</div>
        <br><br>
    """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["🔍 Search Medicine", "📷 Scan Medicine Strip"])

    # ══════════════════════════════════════════════════════════
    # TAB 1 — Search
    # ══════════════════════════════════════════════════════════
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([5, 1])
        with col1:
            search_input = st.text_input(
                label            = "Medicine name",
                value            = st.session_state.get("search_query", ""),
                placeholder      = "e.g. Dolo 650, Ibuprofen, Metformin...",
                label_visibility = "collapsed"
            )
        with col2:
            search_btn = st.button("🔍 Search", type="primary", use_container_width=True)

        # Handle sidebar quick search
        do_search = st.session_state.pop("do_search", False)

        if (search_btn or do_search) and search_input.strip():
            with st.spinner(f"Looking up '{search_input}'..."):
                time.sleep(0.5) # Slight delay to show loading animation
                result = search_medicine(search_input.strip())

            if "error" in result:
                st.error(f"❌ {result['error']}")
                if "suggestion" in result:
                    st.info(f"💡 {result['suggestion']}")
            else:
                st.session_state["medicine_info"] = result
                st.session_state["searched"]      = True

        elif (search_btn or do_search) and not search_input.strip():
            st.warning("⚠️ Please enter a medicine name.")

        # Show medicine card
        if st.session_state.get("searched") and "medicine_info" in st.session_state:
            show_medicine_card(st.session_state["medicine_info"], key_suffix="search_tab")

    # ══════════════════════════════════════════════════════════
    # TAB 2 — Camera Scan
    # ══════════════════════════════════════════════════════════
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h4><span class='camera-pulse'>📷</span> Scan Medicine Strip</h4>", unsafe_allow_html=True)
        st.caption("Take a photo or upload an image of a medicine strip or box.")

        input_method = st.radio("Input method:", ["📷 Use Camera", "📁 Upload Image"], horizontal=True)

        image_to_scan = None

        if input_method == "📷 Use Camera":
            st.info("💡 Hold medicine strip steady in good light, then click the camera button.")
            camera_image = st.camera_input("Take a photo")
            if camera_image:
                image_to_scan = camera_image
        else:
            uploaded = st.file_uploader("Upload medicine image", type=["jpg", "jpeg", "png", "bmp"])
            if uploaded:
                image_to_scan = uploaded

        if image_to_scan is not None:
            st.image(image_to_scan, caption="Preview", width=400)

            if st.button("🔍 Scan & Identify", type="primary"):
                # Clear previous selections when scanning a new image
                st.session_state.pop("selected_candidate", None)
                st.session_state.pop("scan_result", None)
                
                with st.spinner("Running Advanced OCR..."):
                    try:
                        img_bytes = image_to_scan.getvalue()
                        files     = {"image": ("capture.jpg", img_bytes, "image/jpeg")}
                        response  = requests.post(f"{BACKEND_URL}/scan", files=files, timeout=30)
                        st.session_state["scan_result"] = response.json()
                    except requests.exceptions.ConnectionError:
                        st.session_state["scan_result"] = {"error": "Cannot connect to Flask backend."}
                    except Exception as e:
                        st.session_state["scan_result"] = {"error": str(e)}

            # Display results if available in session state
            if "scan_result" in st.session_state:
                scan_result = st.session_state["scan_result"]
                
                if "error" in scan_result:
                    st.error(f"❌ {scan_result['error']}")
                else:
                    st.success("✅ OCR Complete!")

                    with st.expander("📝 Raw OCR Text"):
                        st.code(scan_result.get("raw_text", "Nothing detected"))

                    candidates = scan_result.get("medicine_candidates", [])

                    if candidates:
                        st.markdown("### 💊 Detected Medicine Names — Click to Look Up:")
                        btn_cols = st.columns(min(len(candidates), 3))
                        for i, candidate in enumerate(candidates):
                            with btn_cols[i % 3]:
                                if st.button(f"💊 {candidate}", key=f"c_{i}_{candidate}", use_container_width=True):
                                    st.session_state["selected_candidate"] = candidate
                        
                        # Process the selected candidate
                        if "selected_candidate" in st.session_state:
                            candidate = st.session_state["selected_candidate"]
                            with st.spinner(f"Looking up {candidate}..."):
                                med = search_medicine(candidate)

                            if med is None:
                                st.error("No response from backend.")
                            elif "error" in med:
                                st.warning(f"'{candidate}' not found in database.")
                                st.info("💡 Try searching manually in the 🔍 Search Medicine tab.")
                            else:
                                st.session_state["medicine_info"] = med
                                st.session_state["searched"]      = True
                                st.success(f"✅ Found: {med.get('name', candidate)}")
                                st.divider()
                                show_medicine_card(med, key_suffix="scan_tab")


if __name__ == "__main__":
    main()