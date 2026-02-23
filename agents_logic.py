import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from designer_utils import create_executive_pptx, create_multi_user_pptx
from dotenv import load_dotenv

# 1. Configuration
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
gpt4o = ChatOpenAI(model_name="gpt-4o", temperature=0.6, openai_api_key=api_key)


def get_agent_feedback(user_response, current_question, history):
    interviewer = Agent(
        role="High-Quality Interviewer",
        goal="Extract substantive insights through a Quality-First loop.",
        backstory="""#Mission: Your goal is to ensure every answer is substantive, clear, and valuable for a final 
        report, while making the user feel heard and supported. 
        #Method: Analyze the user's response. A response is considered "Garbage" if it is shorter than 10 words, uses 
        vague fillers (e.g., "I don't know," "same as before"), or fails to address the core of the question. 
        The Candid Nudge: If a response is unsatisfactory, do not move forward. Instead, use a short follow-up to 
        encourage expansion.
        If quality is good, start your response with 'PROCEED'.
        #Personality You are approachable, positive, and professional. You act as a supportive consultant rather than 
        an interrogator. Your tone is candid but always encourages the user to provide their best insights.
        """,
        llm=gpt4o
    )

    task = Task(
        description=f"Evaluate: '{user_response}' for Q: '{current_question}'. History: {history}",
        expected_output="A conversational response. Start with 'PROCEED' if the answer is good.",
        agent=interviewer
    )

    return Crew(agents=[interviewer], tasks=[task]).kickoff().raw

def generate_multi_user_story(sub_id, data):
    file_path = create_multi_user_pptx(sub_id,data, gpt4o)
    return file_path


def run_designer_task(sub_id, submitter, transcript_json):
    # Generate the actual file using our utility
    file_path = create_executive_pptx(sub_id, submitter, transcript_json, gpt4o)
    return file_path