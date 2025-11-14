from langchain_openai import ChatOpenAI
from apps.aiModule.utils.output_extractor import MessageResponse
from apps.emailModule.utils import send_email

from apps.emailModule.outlook import OutlookEmail

outlookEmail = OutlookEmail()

def summary(context):
    llm = ChatOpenAI(model='gpt-4.1-mini').with_structured_output(MessageResponse)
    system_prompt = f"""
        You're expert content writer. You will be given a the text of call.
        Your job is to create short summary of the call capturing important points.
        That call will be between client and sales agent.
        Here is the call:
        {context}
    """

    response = llm.invoke(system_prompt)
    return response

def send_summary_email(transcript_text, agent_smtp_email, agent_smtp_password, lead_email, email_provider):
    summaryResponse = summary(transcript_text)
    if email_provider == 'gmail':
        send_email(agent_smtp_email, agent_smtp_password, lead_email, summaryResponse.heading, summaryResponse.body)
        return True
    elif email_provider == 'outlook':
        is_true, message = outlookEmail.send_outlook_email(agent_smtp_password, lead_email, summaryResponse.heading , summaryResponse.body)
        if not is_true:
            return True
    return False

