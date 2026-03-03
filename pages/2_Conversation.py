import sqlite3
import time
import streamlit as st
from agents_logic import get_agent_feedback
from database import save_answer, save_complete_questioning
from fixed_questions import question6, question7, question8, answer2, answer3

st.set_page_config(
    page_title="Contextual Intelligence PoC",
    page_icon="🤖",
    layout="wide"
)

# 1. INITIALIZATION
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False
if "consent_given" not in st.session_state:
    st.session_state.consent_given = False
if "nudge_count" not in st.session_state:
    st.session_state.nudge_count = 0


def apply_custom_css():
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def type_response(text):
    if not text.startswith("🤖 **CI_Agent**"):
        text = f"🤖 **CI_Agent**: {text}"
    with st.chat_message("assistant"):
        st.markdown(text, unsafe_allow_html=True)
    return text


apply_custom_css()

# --- CONVERSATION SETUP ---
if "active_interview" not in st.session_state:
    st.info("Please approve a document in the L2 Reviewer Queue first to start a conversation.")
    st.stop()

conversation_data = st.session_state.active_interview
submitter_name = conversation_data.get("user", "submitter")
doc_path = conversation_data.get("path", "the document")
dynamic_questions = conversation_data.get("questions", [])

# Logic: f1 (impact matrix) counts as 1 section, f2-f6 follow.
# total_dynamic = 4 (Usually questions 7, 8, 9, 10)
total_dynamic = len(dynamic_questions)

st.title(f"💬 Conversation with {submitter_name}")

# 2. GREETING LOGIC
if not st.session_state.conversation_started:
    greeting = (
                f"Hello {submitter_name}! You’re receiving this survey because you were listed as the contact for `{doc_path}`.\n\n"
                f"Your work stood out to us, and we’d love to understand a bit more about the thinking behind it and any expected client context.\n"
                f"We have a few quick questions — around 5 minutes — and your perspective will help strengthen future narratives across teams.\nThanks for taking the time to share your insight.\n\n"
                f"Shall we begin our conversation?"
            )
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    st.session_state.conversation_started = True

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f"👤 **{submitter_name}** : {message['content']}")
        else:
            st.markdown(message["content"])

# --- PHASE B: THE STRUCTURED FORM (Independent Rendering) ---
if st.session_state.consent_given and st.session_state.current_q_index == 1:
    st.warning("Please fill out the Fundamentals Form below to proceed.")

    with st.form("mandatory_questions_form"):
        st.subheader("📋 Project Fundamentals")
        st.markdown("**1. Rate the business impact of this submission on the following parameters:**")

        f1_ai = st.select_slider("• AI / GenAI:",
                                 options=["Low Impact", "Medium-Low", "Medium", "Medium-High", "High Impact"],
                                 value="Medium")
        f1_data = st.select_slider("• Data:",
                                   options=["Low Impact", "Medium-Low", "Medium", "Medium-High", "High Impact"],
                                   value="Medium")
        f1_ecosystem = st.select_slider("• Ecosystem:",
                                        options=["Low Impact", "Medium-Low", "Medium", "Medium-High", "High Impact"],
                                        value="Medium")
        f1_talent = st.select_slider("• Talent:",
                                     options=["Low Impact", "Medium-Low", "Medium", "Medium-High", "High Impact"],
                                     value="Medium")
        f1_methods = st.select_slider("• Methods:",
                                      options=["Low Impact", "Medium-Low", "Medium", "Medium-High", "High Impact"],
                                      value="Medium")
        f1_asset = st.select_slider("• Asset or Solution:",
                                    options=["Low Impact", "Medium-Low", "Medium", "Medium-High", "High Impact"],
                                    value="Medium")

        st.divider()

        # Remaining Fixed Questions
        f2 = st.multiselect("2. Which of the following best describes the nature of this submission?",
                            options=["Differentiates Company in early-stage conversations",
                                     "Enables innovative business model or pricing", "Solution architecting",
                                     "Pricing & profitability", "Delivery optimization", "Innovation enablement",
                                     "Leverages M&A", "Others"])

        f3 = st.multiselect("3. Which client role or persona was this shared with or is going to be targeted to?"
                            " (E.g. CFO, Thought Leaders, Industry Consultants etc.)",
                            options=["Executive Leadership (C-Suite)", "Board member", "Management & Strategic leads",
                                     "SMEs/Consultants", "Others"])

        f4 = st.multiselect("4. What is the primary competitive advantage (USP) of this solution compared to standard "
                            "market offerings? (Select top 3)",
                            options=["Speed: Deploys significantly faster (e.g., pre-built accelerators).",
                                     "Cost: Significantly cheaper TCO than competitors.",
                                     "Uniqueness: Uses proprietary IP/Tech that others don't have.",
                                     "Industry Specificity: tailored deeply to a specific vertical (niche).",
                                     "Simplicity: Easier to adopt/integrate than complex alternatives.",
                                     "Ecosystem: Leverages a strong alliance (e.g., exclusive Microsoft/AWS tier).",
                                     "Others"],
                            max_selections=3)

        f5 = st.multiselect("5. Which primary market challenge or client trigger is this material designed to address?",
                            options=["Cost Pressure: Clients needing to reduce OpEx/CapEx immediately.",
                                     "Innovation Gap: Clients falling behind competitors/market trends.",
                                     "Compliance/Risk: New regulations (e.g., ESG, GDPR) requiring urgent action.",
                                     "Legacy Modernization: Moving off outdated platforms.",
                                     "Speed to Market: Accelerating product launches.",
                                     "Customer Experience: Fixing broken user/customer journeys.",
                                     "Others"])

        f6 = st.multiselect("6. In which scenarios should a sales team AVOID pitching this solution? "
                            "(Select the primary 'Non-Starter’)",
                            options=["Small Budget: The setup cost is too high for small deals.",
                                     "Low Tech Maturity: Client lacks the team to manage/run this.",
                                     "Short Timeline: Implementation takes too long for quick wins.",
                                     "Custom Heavy: Client wants a highly bespoke solution (this is a standard "
                                     "product).",
                                     "Regulation Heavy: This solution is not yet compliant with strict standards "
                                     "(e.g., HIPAA/FedRAMP).",
                                     "Others"])

        if st.form_submit_button(f"Next ({total_dynamic} questions remaining)"):
            if not f2 or not f3 or not f4 or not f5 or not f6:
                st.error("⚠️ All sections must have at least one selection before proceeding.")
            else:
                form_map = {
                    "AI / GenAI": f1_ai, "Data": f1_data, "Ecosystems": f1_ecosystem,
                    "Talent": f1_talent, "Methods": f1_methods, "Asset": f1_asset,
                    "Nature": str(f2), "Persona": str(f3), "USP": str(f4),
                    "Primary Market Challenge": str(f5), "Avoidance": str(f6)
                }
            for q, a in form_map.items():
                save_answer(1, q, a)

            # Move to the first dynamic question (Question 7)
            st.session_state.current_q_index = 7
            first_dynamic_q = dynamic_questions[0]

            # Calculation for remaining: if we are at Q7 of 10, 3 remain (8, 9, 10)
            remaining = total_dynamic - 1
            response_text = f"{first_dynamic_q} ({remaining} remaining questions)"

            # 3. Add to history so it persists after rerun
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            st.rerun()

# --- CHAT INPUT LOGIC ---
if prompt := st.chat_input("Enter your response..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response_text = ""

    # PHASE A: CONSENT
    if not st.session_state.consent_given:
        if any(word in prompt.lower() for word in ["yes", "sure", "ok", "ready", "claro", "si", "go ahead"]):
            st.session_state.consent_given = True
            st.session_state.current_q_index = 1
            st.rerun()
        else:
            response_text = "Shall we begin our conversation? (Yes/No)"

    # PHASE C: AI CHAT (Questions 7-10)
    elif st.session_state.current_q_index >= 7:
        # Map current_q_index (7, 8, 9, 10) to dynamic_questions list index (0, 1, 2, 3)
        list_idx = st.session_state.current_q_index - 7

        if list_idx < total_dynamic:
            current_q_text = dynamic_questions[list_idx]
            agent_feedback = get_agent_feedback(prompt, current_q_text, st.session_state.messages[-5:])

            if "PROCEED" in agent_feedback or st.session_state.nudge_count >= 1:
                sub_id = st.session_state.active_interview.get('id', 100)
                save_answer(sub_id, current_q_text, prompt)
                st.session_state.nudge_count = 0

                # Check if there is another question after this one
                if list_idx + 1 < total_dynamic:
                    st.session_state.current_q_index += 1
                    next_q_text = dynamic_questions[list_idx + 1]
                    remaining = total_dynamic - (list_idx + 2)
                    response_text = f"{next_q_text} ({remaining} remaining questions)"

                else:
                    response_text = "That was the final question! Thanks for your time."
                    st.session_state.current_q_index = 999
                    save_complete_questioning(2, answer2)
                    save_complete_questioning(3, answer3)
            else:
                st.session_state.nudge_count += 1
                response_text = f"{agent_feedback}\n\n*(Note: If the next answer is also short, I'll move to the next question automatically.)*"

    # Final Response Rendering
    if response_text:
        final_text = type_response(response_text)
        st.session_state.messages.append({"role": "assistant", "content": final_text})