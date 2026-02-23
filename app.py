import streamlit as st
from database import init_db

# 1. CREATE THE DATABASE AND TABLES ON STARTUP
init_db()

# Configure the page and sidebar once for the whole app
st.set_page_config(
    page_title="Contextual Intelligence PoC",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Redirect Logic
# If the user just lands on the home page, we show a welcome or redirect
st.title("Welcome to the Contextual Intelligence PoC")

st.markdown("""
### Getting Started
1. **Knowledge Curator Validation:** Go to the Inbox to approve pending documents.
2. **Conversation:** Conduct the conversation with the submitter.
3. **Tracker:** Monitor progress and download results.
""")

if st.button("🚀 Start with Knowledge Curator Validation Page"):
    st.switch_page("pages/1_Knowledge_Curator_Validation.py")

# persistent Sidebar Info
st.sidebar.info("Select a stage from the list above to begin.")