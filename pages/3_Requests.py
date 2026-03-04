import json
import streamlit as st
import sqlite3
import os
import pandas as pd
from agents_logic import generate_multi_user_story

st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        font-weight: bold;
        border-radius: 8px;
    }
    div.stButton > button:first-child {
        background-color: #4B2680;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

root_path = os.path.dirname(os.path.dirname(__file__))
img_path = os.path.join(root_path, "myRequests.png")

if os.path.exists(img_path):
    st.image(img_path, width="stretch")
else:
    st.error(f"File not found. Looking in: {img_path}")

cols = st.columns(6)
# Filling the row
cols[0].write("7581")
cols[1].write("Agentic Commerce State of the Nation POV")
cols[2].write("Sales & Solutioning Materials")
cols[3].write("Consumer Good & Services, Retail, Travel")
cols[4].write("18 Feb 2026")
cols[5].markdown("**CI - In Progress**") # Status as requested

st.divider()
st.subheader("Final Synthesis")
st.info("After receiving the answers from the 3 conversations of after 15 days a slide will be available.")

if "active_interview" in st.session_state:
    sub_id = st.session_state.active_interview['id']

    # Action Button
    if st.button("Generate Slide", type="primary", width="stretch"):
        with st.status("🧠 Synthesizing insights...", expanded=True) as status:
            # try:
            #     with sqlite3.connect("submissions.db") as conn:
            #         cursor = conn.cursor()
            #         cursor.execute("SELECT transcript FROM submissions")
            #         rows = cursor.fetchall()
            #     master_transcript = {}
            #     for row in rows:
            #         # Load the JSON from the current row
            #         individual_data = json.loads(row[0]) if row[0] else {}
            #         # Merge it into the master dictionary
            #         master_transcript.update(individual_data)
            #
            #     # Convert merged dict back to JSON string for the generator
            #     consolidated_json = json.dumps(master_transcript)
            #
            #     # Generate PPTX
            #     path_to_pptx = generate_multi_user_story(sub_id, consolidated_json)
            #     path_to_pptx
            master_transcript = {}
            for item in st.session_state.all_responses:
                master_transcript.update(item)
            consolidated_json = json.dumps(master_transcript)
            path_to_pptx = generate_multi_user_story(sub_id, consolidated_json)
            st.session_state.final_pptx_path = path_to_pptx
            status.update(label="✅ Synthesis Complete!", state="complete")
            #except Exception as e:
            #    st.error(f"Error: {e}")

    # DOWNLOAD LINK (Appear after generation)
    if "final_pptx_path" in st.session_state:
        file_path = st.session_state.final_pptx_path
        #file_path = f"exports/Strategic_Synthesis_Example.pptx"
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                # Creating a styled link/button for download
                st.download_button(
                    label="🚀 Download Generated PowerPoint",
                    data=f,
                    file_name=os.path.basename(file_path),
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    width="stretch"
                )
        else:
            file_path = f"exports/Strategic_Synthesis_Example.pptx"
            with open(file_path, "rb") as f:
                # Creating a styled link/button for download
                st.download_button(
                    label="🚀 Download Generated PowerPoint",
                    data=f,
                    file_name=os.path.basename(file_path),
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    width="stretch"
                )

# Footer note
st.caption("Contextual Intelligence Engine v1.0 | Powered by GPT-4o & CrewAI")