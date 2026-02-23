import re
import ast
import random
import PyPDF2
from agents_logic import gpt4o
from crewai import Agent, Task, Crew

def extract_pdf_text(file_path):
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages[:5]:
                text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def generate_strategic_questions(file_path=None, file_name="Document"):
    # --- STEP 1: ATTEMPT PDF READING ---
    doc_content = None
    try:
        doc_content = extract_pdf_text(file_path)
    except Exception as e:
        print(f"PDF Reading failed. Error: {e}")

    # --- STEP 2: RUN AGENT OR FALLBACK ---
    # We try to get the 4 dynamic questions first
    dynamic_questions = None
    if doc_content and "Error" not in doc_content:
        dynamic_questions = run_architect_agent(doc_content, file_name)
        print("Questions Generated!")

    # Fallback for the 4 dynamic questions if PDF fails or Agent fails
    if not dynamic_questions:
        print("Dynamic Questions")
        fallback_pool = [
            f"What led you to prioritize the specific goals outlined in '{file_name}'?",
            "How did you decide on the primary strategic approach used here?",
            "What's the main thought behind the way this solution is structured?",
            "Who did you have in mind when you drafted the key value propositions?",
            "What makes this specific document stand out for you compared to similar ones?"
        ]
        dynamic_questions = random.sample(fallback_pool, 4)

    return dynamic_questions


def run_architect_agent(content, name):
    architect_agent = Agent(
        role="Warm Strategic Partner",
        goal="Infer document context and generate 4 concise, discovery-driven questions.",
        backstory="""You are a thoughtful AI partner. Your tone is appreciative and human-centric. 
        You analyze documents to uncover unspoken insights, motivations, and reasoning. 
        You act like a curious colleague, not a clinical auditor.""",
        llm=gpt4o,
        verbose=False
    )

    architect_task = Task(
        description=f"""
        1. Infer the context of '{name}' (e.g., persuasion, summary, proposal, success story).
        2. Content to analyze:
        ---
        {content}
        ---

        Generate exactly 4 concise, discovery-driven questions to uncover unspoken insights.
        - Questions must be short (ideally one sentence).
        - Invite reflection on intent, reasoning, or emotional undertones.
        - Use natural phrasing like: 'What led you to...', 'How did you decide...', 'What's the main thought behind...'.
        - Avoid asking things already explicitly answered in the text.

        Output Format: Return ONLY a Python-style list of 4 strings.
        Example: ["Question A", "Question B", "Question C", "Question D"]
        """,
        agent=architect_agent,
        expected_output="A Python list containing exactly 4 strings."
    )

    crew = Crew(agents=[architect_agent], tasks=[architect_task])
    result = crew.kickoff()

    try:
        raw_output = str(result)
        match = re.search(r"\[.*\]", raw_output, re.DOTALL)
        if match:
            questions = ast.literal_eval(match.group())
            if len(questions) == 4:
                return questions
        raise ValueError("Agent output format incorrect")
    except Exception as e:
        print(f"Architect Agent failed: {e}")
        return None