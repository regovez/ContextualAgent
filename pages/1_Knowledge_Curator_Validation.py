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
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

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
            # Initial generation of 5 dynamic questions
            dynamic_questions = generate_strategic_questions(DOC_PATH, DOC_NAME)

            # Store as a dictionary to track index-specific edits and selection
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

    # Track checked indices for both Regenerate and Edit actions
    selected_indices = []

    for i, q in enumerate(st.session_state.dynamic_questions):
        display_idx = i + 7
        col_check, col_text = st.columns([0.1, 0.9])

        with col_check:
            is_checked = st.checkbox(f" ", key=f"select_{display_idx}")
            if is_checked:
                selected_indices.append(i)

        with col_text:
            # Display as clean text until Edit Mode is activated
            st.markdown(f"**Question {display_idx}:** {q}")

    st.write("")

    # --- 3. ACTION BUTTONS ---
    col_reg, col_edit, col_app = st.columns(3)

    with col_reg:
        if st.button("Re-Generate Selected"):
            if not selected_indices:
                st.warning("Please select questions to replace.")
            else:
                with st.spinner("🔄 Architect Agent refining..."):
                    fresh_batch = generate_strategic_questions(DOC_PATH,DOC_NAME)
                    for idx in selected_indices:
                        st.session_state.dynamic_questions[idx] = fresh_batch[idx]
                    st.rerun()

    with col_edit:
        if st.button("Edit Selected"):
            if not selected_indices:
                st.warning("Please select questions to edit.")
            else:
                st.session_state.edit_mode = True
                st.session_state.indices_to_edit = selected_indices

    # --- 4. DYNAMIC EDIT FIELDS (Appears only after clicking Edit) ---
    if st.session_state.edit_mode:
        st.info("✍️ Modify the selected questions below:")
        temp_updates = {}

        for idx in st.session_state.indices_to_edit:
            display_idx = idx + 5
            # Create a text input for each selected question
            temp_updates[idx] = st.text_input(
                f"Edit Question {display_idx}",
                value=st.session_state.dynamic_questions[idx],
                key=f"input_edit_{display_idx}"
            )

        if st.button("Save Manual Edits"):
            # Update the master list with the new typed content
            for idx, new_text in temp_updates.items():
                st.session_state.dynamic_questions[idx] = new_text

            # Close edit mode and refresh the printed list
            st.session_state.edit_mode = False
            st.success("✅ Edits saved to the master list.")
            st.rerun()


    with col_app:
        if st.button("Approve Questions"):
            # Use exactly what is currently visible in the text inputs
            #final_approved = current_screen_questions
            SUB_ID = 100

            try:
                # Initialize stakeholder records
                approve_submission(1, SUB_ID, DOC_NAME, "sushmita.bhamidipati")
                approve_submission(2, SUB_ID, DOC_NAME, "vikalp.tandon")
                approve_submission(3, SUB_ID, DOC_NAME, "samuel.t.agris")

                # Move the edited, on-screen text to the next phase
                st.session_state.active_interview = {
                    "id": SUB_ID,
                    "path": DOC_NAME,
                    "questions": st.session_state.dynamic_questions,
                    "user": "sushmita.bhamidipati"
                }

                st.success("✅ Context Intelligence Agent will start conversation with: **sushmita.bhamidipati, vikalp.tandon, samuel.t.agris**")
                # Optional: st.switch_page("pages/2_Conversation.py")
            except Exception as e:
                st.error(f"Error saving to database: {e}")

st.caption("Contextual Intelligence Engine v1.0 | Powered by GPT-4o & CrewAI")