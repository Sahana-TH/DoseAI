# main.py — DoseAI Clean Version
# Run: streamlit run streamlit_ui/main.py

import streamlit as st
import requests

# ── PAGE CONFIG — must be first Streamlit command ─────────────
st.set_page_config(
    page_title = "DoseAI – Smart Medicine Info",
    page_icon  = "💊",
    layout     = "wide"
)

BACKEND_URL = "http://127.0.0.1:5000"


# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def search_medicine(name: str) -> dict:
    """Calls Flask /medicine/<name> and returns result."""
    try:
        response = requests.get(
            f"{BACKEND_URL}/medicine/{name.strip()}",
            timeout=15
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error {response.status_code}"}
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
                json    = {
                    "medicine_info": medicine_info,
                    "language":      language,
                    "section":       section
                },
                timeout = 30
            )
            if response.status_code == 200:
                audio_bytes = response.content
                if len(audio_bytes) > 0:
                    st.success(f"✅ Playing in {language}")
                    st.audio(audio_bytes, format="audio/mp3")
                else:
                    st.error("Empty audio returned.")
            else:
                st.error(f"Flask error {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to Flask backend.")
        except Exception as e:
            st.error(f"Error: {str(e)}")


def show_medicine_card(info: dict):
    """Shows medicine info in a clean card layout."""

    # Source badge
    source = info.get("source", "")
    if source == "local":
        st.success("✅ Source: Local Database (Indian Medicine)")
    else:
        st.info("🌐 Source: OpenFDA API")

    # Medicine name
    st.markdown(f"## 💊 {info.get('name', 'Medicine')}")
    st.divider()

    # Two column layout
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📋 Usage")
        st.write(info.get("usage", "Not available"))

        st.markdown("---")

        st.markdown("#### ⚠️ Side Effects")
        st.write(info.get("side_effects", "Not available"))

    with col2:
        st.markdown("#### 💉 Dosage")
        st.write(info.get("dosage", "Not available"))

        st.markdown("---")

        st.markdown("#### 🚨 Overdose & Warnings")
        st.write(info.get("overdose", "Not available"))
        st.write(info.get("warnings", "Not available"))

    st.divider()

    # Voice section
    st.markdown("### 🔊 Read Aloud")

    vc1, vc2 = st.columns(2)
    with vc1:
        language = st.selectbox(
            "Language",
            ["English", "Hindi", "Kannada"],
            key="lang_select"
        )
    with vc2:
        section = st.selectbox(
            "Section",
            ["summary", "dosage", "side_effects", "overdose", "warnings", "full"],
            key="section_select"
        )

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

    st.divider()

    with st.expander("🛠️ Raw JSON (Developer Mode)"):
        st.json(info)


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────

def build_sidebar():
    with st.sidebar:
        st.title("💊 DoseAI")
        st.caption("Smart Medicine Information System")
        st.divider()

        st.markdown("#### 💡 Quick Search")
        quick_list = [
            "Dolo 650", "Crocin", "Pantoprazole",
            "Azithromycin", "Metformin"
        ]
        for med in quick_list:
            if st.button(med, key=f"quick_{med}", use_container_width=True):
                st.session_state["search_query"] = med
                st.session_state["do_search"]    = True

        st.divider()
        st.caption("⚕️ Always consult a doctor for medical advice.")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    build_sidebar()

    # ── Header ────────────────────────────────────────────────
    st.title("💊 DoseAI — Smart Medicine Information System")
    st.caption("Search for medicine info, scan strips, and hear it read aloud in 3 languages.")
    st.divider()

    # ── Tabs ──────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["🔍 Search Medicine", "📷 Scan Medicine Strip"])

    # ══════════════════════════════════════════════════════════
    # TAB 1 — Search
    # ══════════════════════════════════════════════════════════
    with tab1:
        st.subheader("Search by Medicine Name")

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
            show_medicine_card(st.session_state["medicine_info"])

    # ══════════════════════════════════════════════════════════
    # TAB 2 — Camera Scan
    # ══════════════════════════════════════════════════════════
    with tab2:
        st.subheader("📷 Scan Medicine Strip")
        st.caption("Take a photo or upload an image of a medicine strip or box.")

        input_method = st.radio(
            "Input method:",
            ["📷 Use Camera", "📁 Upload Image"],
            horizontal=True
        )

        image_to_scan = None

        if input_method == "📷 Use Camera":
            st.info("💡 Hold medicine strip steady in good light, then click the camera button.")
            camera_image = st.camera_input("Take a photo")
            if camera_image:
                image_to_scan = camera_image

        else:
            uploaded = st.file_uploader(
                "Upload medicine image",
                type=["jpg", "jpeg", "png", "bmp"]
            )
            if uploaded:
                image_to_scan = uploaded

        if image_to_scan is not None:
            st.image(image_to_scan, caption="Preview", width=400)

            if st.button("🔍 Scan & Identify", type="primary"):
                with st.spinner("Running OCR..."):
                    try:
                        img_bytes = image_to_scan.getvalue()
                        files     = {"image": ("capture.jpg", img_bytes, "image/jpeg")}
                        response  = requests.post(
                            f"{BACKEND_URL}/scan",
                            files=files,
                            timeout=30
                        )
                        scan_result = response.json()
                    except requests.exceptions.ConnectionError:
                        scan_result = {"error": "Cannot connect to Flask backend."}
                    except Exception as e:
                        scan_result = {"error": str(e)}

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
                                        show_medicine_card(med)


if __name__ == "__main__":
    main()