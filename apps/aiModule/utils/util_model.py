import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_sales.settings')
django.setup()
from apps.aiModule.models import ChatMessageHistory
from apps.users.models import LeadModel
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime, timedelta


def get_chat_message_by_id(lead_id):
    messages = ChatMessageHistory.objects.filter(lead_id=lead_id)
    messages_list = []
    for message in messages:
        folow_up = message.follow_up_date if message.follow_up_date else 'None'
        content = f"""Time Created: {message.created_at} Follow Up Due Date: {folow_up} Today's Date: {datetime.today()}
        Wrote by {message.wroteBy} interest level: {message.interestLevel} Type: {message.messageType} 
        Heading: {message.heading} Body: {message.body}"""
        if message.aiType == 'ai':
            messages_list.append(AIMessage(content=content))
        elif message.aiType == 'human':
            messages_list.append(HumanMessage(content=content))
    return messages_list
    


def add_chat_message(lead_id, heading, body, messageType='none', aiType='none', interestLevel='none', wroteBy='none', follow_up_day=0, key_points=None):
    # create datefield from follow_up_day
    if follow_up_day == 0:
        follow_up_date = None
    else:
        follow_up_date = datetime.today() + timedelta(days=follow_up_day)
    try:
        lead = LeadModel.objects.get(id=lead_id)
        chat_message = ChatMessageHistory.objects.create(
            lead=lead,
            heading=heading,
            body=body,
            messageType=messageType,
            aiType=aiType,
            interestLevel=interestLevel,
            wroteBy=wroteBy,
            follow_up_date=follow_up_date,
            key_points=key_points,
        )
        return chat_message
    except LeadModel.DoesNotExist:
        return None

def save_call_message(lead_id, text):
    try:
        return add_chat_message(
            lead_id=lead_id,
            heading='Call',
            body=text,
            messageType='call',
            aiType='human',
            wroteBy='agent',

        )
    except Exception as e:
        return None



def save_ai_message(lead_id, state):
    # check if the message is instance of AIMessage
    return add_chat_message(
        lead_id=lead_id,
        heading=state.heading,
        body=state.body,
        messageType='call' if state.contact_type == 'call' else 'email',
        aiType='ai',
        interestLevel=str(state.interest_level),
        wroteBy='ai',
        follow_up_day=state.follow_up_date,
        key_points=state.key_points
    )

if __name__ == "__main__":
    lead_id = 1  # Example lead ID
    print(get_chat_message_by_id(1))
