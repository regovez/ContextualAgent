import os
import streamlit as st
from database import approve_submission
from architect_utils import generate_strategic_questions
from fixed_questions import question1, question2, question3, question4, question5, question6

DOC_PATH = "docs/Agentic Commerce State of the Nation POV.pdf"
DOC_NAME = "Agentic Commerce State of the Nation POV.pdf"

st.set_page_config(
    page_title="Contextual Intelligence PoC",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. SETUP SESSION STATE ---
if "dynamic_questions" not in st.session_state:
    st.session_state.dynamic_questions = []
if "question_backups" not in st.session_state:
    st.session_state.question_backups = {} # Stores previous versions for Undo

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
    st.image(img_path, width="stretch")
else:
    st.error(f"File not found. Looking in: {img_path}")

# --- ARCHITECT AGENT TRIGGER ---
if st.button("APPROVE", key="init_approve"):
    with st.status("🧠 Architect Agent: Analyzing Document...", expanded=True) as status:
        try:
            dynamic_questions = generate_strategic_questions(DOC_PATH, DOC_NAME)
            st.session_state.dynamic_questions = dynamic_questions
            st.session_state.analysis_complete = True
            status.update(label="✅ Initial Questions Generated", state="complete", expanded=False)
        except Exception as e:
            st.error(f"Error during analysis: {e}")

# --- EDITABLE REVIEW SECTION ---
if st.session_state.get("analysis_complete"):

    st.divider()
    st.subheader("📋 Standard Deal/Project Questions")
    for i, q in enumerate([question1, question2, question3, question4, question5, question6], 1):
        st.markdown(f"**Question {i}:** {q}")

    st.divider()
    st.subheader("📋 Generated Strategic Questions")
    st.info("You can regenerate individual questions. Use the 'Undo' button to revert to the previous version.")

    if "regen_status" not in st.session_state:
        # Initialize all 4 dynamic questions as "Not Regenerated" (False)
        st.session_state.regen_status = {i: False for i in range(len(st.session_state.dynamic_questions))}

    # Iterate through generated questions
    for i, q in enumerate(st.session_state.dynamic_questions):
        display_idx = i + 7

        # Container for each question's row
        with st.container():
            col_text, col_reg, col_undo = st.columns([0.7, 0.15, 0.15])

            with col_text:
                st.markdown(f"**Question {display_idx}:** {q}")

            with col_reg:
                is_disabled = st.session_state.regen_status.get(i, False)
                # Individual Regenerate Button
                if st.button(f"🔄 Regen Q{display_idx}", key=f"reg_{display_idx}", disabled=is_disabled):
                    with st.spinner(f"Refining Q{display_idx}..."):
                        # Backup current version before changing
                        st.session_state.question_backups[i] = q

                        # Fetch fresh batch and pick one to replace
                        fresh_batch = generate_strategic_questions(DOC_PATH, DOC_NAME)
                        st.session_state.dynamic_questions[i] = fresh_batch[i]
                        st.session_state.regen_status[i] = True
                        st.rerun()

            with col_undo:
                # Individual Undo Button
                # Only enabled if a backup exists for this index
                has_backup = i in st.session_state.question_backups
                if st.button(f"↩️ Undo Q{display_idx}", key=f"undo_{display_idx}", disabled=not has_backup):
                    # Swap current with backup
                    current_val = st.session_state.dynamic_questions[i]
                    st.session_state.dynamic_questions[i] = st.session_state.question_backups[i]
                    st.session_state.question_backups[i] = current_val  # Allows toggling back
                    st.rerun()
        st.write("")  # Spacer

    st.divider()

    # --- FINAL APPROVAL ---
    if st.button("Approve Questions", type="primary", use_container_width=True):
        SUB_ID = 100
        DOC_NAME = "Agentic Commerce State of the Nation POV.pdf"
        try:
            # Initialize stakeholder records
            approve_submission(1, SUB_ID, DOC_NAME, "sushmita.bhamidipati")
            approve_submission(2, SUB_ID, DOC_NAME, "vikalp.tandon")
            approve_submission(3, SUB_ID, DOC_NAME, "samuel.t.agris")

            st.session_state.active_interview = {
                "id": SUB_ID,
                "path": DOC_NAME,
                "questions": st.session_state.dynamic_questions,
                "user": "sushmita.bhamidipati"
            }
            st.success("✅ Context Intelligence Agent will start conversation with: **sushmita.bhamidipati, vikalp.tandon, samuel.t.agris**")
            st.balloons()
        except Exception as e:
            st.error(f"Error saving to database: {e}")

st.caption("Contextual Intelligence Engine v1.0 | Powered by GPT-4o & CrewAI")