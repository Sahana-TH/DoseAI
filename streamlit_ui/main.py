# filepath: streamlit_ui/main.py
import streamlit as st
import requests
import os

API_URL = os.environ.get('API_URL', 'http://localhost:5000')

st.title("💊 DoseAI - Medicine Assistant")

st.markdown("### Search for Medicine Information")

medicine_name = st.text_input("Enter medicine name:")

if st.button("Search"):
    if medicine_name:
        try:
            response = requests.get(f"{API_URL}/medicine/{medicine_name}")
            if response.status_code == 200:
                data = response.json()
                st.success(f"Found: {data.get('name')}")
                st.write(f"**Uses:** {data.get('uses', 'N/A')}")
                st.write(f"**Dosage:** {data.get('dosage', 'N/A')}")
                st.write(f"**Side Effects:** {data.get('side_effects', 'N/A')}")
            else:
                st.error("Medicine not found!")
        except Exception as e:
            st.error(f"Error connecting to API: {e}")