from langchain_openai import ChatOpenAI
from apps.aiModule.utils.output_extractor import MessageResponse
from apps.emailModule.utils import send_email

def summary(context):
    llm = ChatOpenAI(model='gpt-4.1-mini', temperature=0).with_structured_output(MessageResponse)
    system_prompt = f"""
        You're expert content writer. You will be given a the text of call.
        Your job is to create short summary of the call capturing important points.
        That call will be between client and sales agent.
        Here is the call:
        {context}
    """

    response = llm.invoke(system_prompt)
    return response

def send_summary_email(transcript_text, agent_smtp_email, agent_smtp_password, lead_email):
    summaryResponse = summary(transcript_text)
    if summaryResponse:
        send_email(agent_smtp_email, agent_smtp_password, lead_email, summaryResponse.heading, summaryResponse.body)
        return True
    return False

