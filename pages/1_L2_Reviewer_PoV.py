import os
import streamlit as st
import pandas as pd
import sqlite3
from database import approve_submission
from architect_utils import generate_strategic_questions
from fixed_questions import question1, question2, question3, question4, question5, question6, question7, question8

st.set_page_config(
    page_title="Contextual Intelligence PoC",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
img_path = os.path.join(root_path, "image.png")

if os.path.exists(img_path):
    st.image(img_path, use_container_width=True)
else:
    st.error(f"File not found. Looking in: {img_path}")


if st.button("APPROVE", key="init_approve"):
    with st.status("🧠 Architect Agent: Analyzing Document & Generating Questions...", expanded=True) as status:
        try:
            DOC_PATH = "docs/Agentic Commerce State of the Nation POV.pdf"
            DOC_NAME = "Agentic Commerce State of the Nation POV.pdf"

            dynamic_questions = generate_strategic_questions(DOC_PATH, DOC_NAME)

            st.session_state.dynamic_questions = dynamic_questions
            st.session_state.analysis_complete = True

            status.update(label="✅ Contextual Intelligence Process Begin", state="complete", expanded=False)
        except Exception as e:
            st.error(f"Error during analysis: {e}")

if st.session_state.get("analysis_complete"):
    st.divider()
    st.subheader("📋 Standard Deal/Project Questions")
    st.markdown(f"**Question {1}:** {question1}")
    st.markdown(f"**Question {2}:** {question2}")
    st.markdown(f"**Question {3}:** {question3}")
    st.markdown(f"**Question {4}:** {question4}")
    st.markdown(f"**Question {5}:** {question5}")
    st.markdown(f"**Question {6}:** {question6}")
    st.markdown(f"**Question {7}:** {question7}")
    st.markdown(f"**Question {8}:** {question8}")

    st.divider()
    st.subheader("📋 Generated Strategic Questions")

    # Checkbox logic for selecting AI-generated questions
    selected_dynamic = []
    for i, q in enumerate(st.session_state.dynamic_questions, 9):  # Starting at 9 following fixed Qs
        if st.checkbox(f"Keep Question {i}: {q}", value=True, key=f"q_check_{i}"):
            selected_dynamic.append(q)

    st.divider()
    st.subheader("✍️ Add Custom Questions")
    st.info("Add up to 3 custom questions to refine the discovery process.")

    custom_q1 = st.text_input("Custom Question 1", key="c_q1")
    custom_q2 = st.text_input("Custom Question 2", key="c_q2")
    custom_q3 = st.text_input("Custom Question 3", key="c_q3")

    # Filter out empty inputs
    custom_questions = [q for q in [custom_q1, custom_q2, custom_q3] if q.strip()]

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Re-Generate"):
            st.info("Re-generation logic will be implemented in the next phase.")

    with col2:
        if st.button("Approve Questions"):
            DOC_NAME = "Agentic Commerce State of the Nation POV.pdf"

            try:
                # Registro en DB para los 3 perfiles (IDs ficticios 1, 2, 3)
                approve_submission(1, 100, DOC_NAME, "sushmita.bhamidipati")
                approve_submission(2, 100, DOC_NAME, "vikalp.tandon")
                approve_submission(3, 100, DOC_NAME, "samuel.t.agris")

                # Set Session State para la página de conversación
                st.session_state.active_interview = {
                    "id": 100,
                    "path": DOC_NAME,
                    "questions": st.session_state.dynamic_questions,
                    "user": "sushmita.bhamidipati"
                }

                st.success(
                    "✅ Context Intelligence Agent will start conversation with: **sushmita.bhamidipati, vikalp.tandon, samuel.t.agris**")
            except Exception as e:
                st.error(f"Error saving to database: {e}")

# Footer note
st.caption("Contextual Intelligence Engine v1.0 | Powered by GPT-4o & CrewAI")