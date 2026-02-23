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
    st.image(img_path, use_container_width=True)
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

# # Set page config for a wide layout
# st.set_page_config(page_title="Requests", layout="wide")
#
#
# def apply_custom_css():
#     try:
#         with open("style.css") as f:
#             st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#     except FileNotFoundError:
#         pass
#
#
# def get_all_submissions():
#     """Fetch all records from the SQLite database."""
#     try:
#         conn = sqlite3.connect("submissions.db")
#         # Converting to a DataFrame for easier handling
#         df = pd.read_sql_query("SELECT id, path, contact, status FROM submissions", conn)
#         conn.close()
#         return df
#     except Exception as e:
#         st.error(f"Database error: {e}")
#         return pd.DataFrame()
#
#
# def get_status_color(status):
#     """Returns a CSS style based on the status."""
#     colors = {
#         "Pending": "background-color: #f0f0f0; color: #666; border: 1px solid #ccc;",
#         "In Progress": "background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba;",
#         "Interviewing": "background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb;",
#         "Summary Generated": "background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb;"
#     }
#     return colors.get(status, "background-color: #fff; color: #000;")
#
#
# apply_custom_css()
#
# st.title("📊 Workflow Status Tracker")
# st.markdown("Monitor the progress of all document analyses and download final reports.")
#
# # Fetch data
# df = get_all_submissions()
#
# if df.empty:
#     st.info("No submissions found. Please approve documents in the L2 Review Queue first.")
# else:
#     # Header row
#     st.divider()
#     h1, h2, h3, h4 = st.columns([3, 2, 2, 2])
#     h1.write("**File Path**")
#     h2.write("**Contact**")
#     h3.write("**Current Status**")
#     h4.write("**Actions**")
#     st.divider()
#
#     # Data rows
#     for index, row in df.iterrows():
#         c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
#
#         c1.text(row['path'])
#         c2.text(row['contact'])
#
#         # Status Badge
#         status = row['status']
#         c3.markdown(
#             f'<span style="padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 0.85rem; {get_status_color(status)}">'
#             f'{status}</span>',
#             unsafe_allow_html=True
#         )
#
#         # Action Column (Download Logic)
#         if status in ["Summary Generated", "Summary Generating", "✅ PowerPoint Ready!"]:
#             file_path = f"exports/Strategic_Report_{row['id']}.pptx"
#             if os.path.exists(file_path):
#                 with open(file_path, "rb") as f:
#                     c4.download_button(
#                         label="📥 Download PPTX",
#                         data=f,
#                         file_name=f"Summary_{row['submitter']}.pptx",
#                         mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
#                         key=f"btn_{row['id']}"
#                     )
#             else:
#                 c4.warning("File not found")
#         elif status == "Interviewing":
#             c4.info("Ongoing Conversation")
#         else:
#             c4.write("---")
#
# # Sidebar summary
# if st.sidebar.button("🔄 Refresh Data"):
#     st.rerun()

st.divider()
st.subheader("Final Synthesis")
st.info("After receiving the answers from the 3 conversations of after 15 days a slide will be available.")

if "active_interview" in st.session_state:
    sub_id = st.session_state.active_interview['id']

    # Action Button
    if st.button("Generate Slide", type="primary", use_container_width=True):
        with st.status("🧠 Synthesizing insights...", expanded=True) as status:
            try:
                with sqlite3.connect("submissions.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT transcript FROM submissions")
                    rows = cursor.fetchall()
                master_transcript = {}
                for row in rows:
                    # Load the JSON from the current row
                    individual_data = json.loads(row[0]) if row[0] else {}
                    # Merge it into the master dictionary
                    master_transcript.update(individual_data)

                # Convert merged dict back to JSON string for the generator
                consolidated_json = json.dumps(master_transcript)

                # Generate PPTX
                path_to_pptx = generate_multi_user_story(sub_id, consolidated_json)
                st.session_state.final_pptx_path = path_to_pptx

                status.update(label="✅ Synthesis Complete!", state="complete")
            except Exception as e:
                st.error(f"Error: {e}")

    # DOWNLOAD LINK (Appear after generation)
    if "final_pptx_path" in st.session_state:
        file_path = st.session_state.final_pptx_path
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                # Creating a styled link/button for download
                st.download_button(
                    label="🚀 Download Generated PowerPoint",
                    data=f,
                    file_name=os.path.basename(file_path),
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True
                )

# Footer note
st.caption("Contextual Intelligence Engine v1.0 | Powered by GPT-4o & CrewAI")