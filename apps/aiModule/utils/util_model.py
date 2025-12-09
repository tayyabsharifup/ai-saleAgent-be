import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_sales.settings')
django.setup()
from django.utils import timezone
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage, AIMessage
from apps.users.models import LeadModel
from apps.aiModule.models import ChatMessageHistory


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


def get_last_ai_interest(messages):
    while messages:
        last = messages.pop()
        if last.aiType == 'ai':
            return str(last.interestLevel)
    return None


def get_initial_decide(lead_id) -> bool:
    follow_up_rules = {
        "short": [
            {"contact_type": "call", "days": 1},
            {"contact_type": "call_or_mail", "days": 3},
            {"contact_type": "call", "days": 3},
            {"contact_type": "call", "days": 6},
            {"contact_type": "call_or_mail", "days": 9},
            {"contact_type": "call", "days": 12},
            {"contact_type": "call_or_mail", "days": 20},
            {"contact_type": "call_or_mail", "days": 40},
            {"contact_type": "call_or_mail", "days": 100},
            {"contact_type": "call_or_mail", "days": 200}
        ],
        "mid": [
            {"contact_type": "call", "days": 7},
            {"contact_type": "call_or_mail", "days": 14},
            {"contact_type": "call_or_mail", "days": 14},
            {"contact_type": "call", "days": 28},
            {"contact_type": "mail", "days": 48},
            {"contact_type": "mail", "days": 48},
            {"contact_type": "call", "days": 60},
            {"contact_type": "mail", "days": 100},
            {"contact_type": "mail", "days": 140},
            {"contact_type": "mail", "days": 250}
        ],
        "long": [
            {"contact_type": "mail", "days": 80},
            {"contact_type": "mail", "days": 180},
            {"contact_type": "mail", "days": 320}
        ],
        "none": []
    }
    messages = list(ChatMessageHistory.objects.filter(lead_id=lead_id))
    last = messages.pop()
    print(f'last - {last}')

    if last.wroteBy == 'ai':
        print('ai message')
        return False
    elif last.wroteBy == 'client' or last.wroteBy == 'none':
        print('client message')
        return True
    elif last.wroteBy == 'agent':
        interest = get_last_ai_interest(
            list(ChatMessageHistory.objects.filter(lead_id=lead_id)))
        print(interest)
        days = (timezone.now() - last.created_at).days
        print(f'days - {days}')
        num = 0
        last = messages.pop()
        while last.wroteBy == 'agent':
            print('More than one agent message')
            num += 1
            last = messages.pop()

        # Check if num is within the bounds of the follow_up_rules for the given interest level
        if interest in follow_up_rules and num < len(follow_up_rules[interest]):
            if follow_up_rules[interest][num]['days'] <= days:
                print('agent last days passed')
                print(
                    f'interest - {interest} num - {num} follow up logic days - {follow_up_rules[interest][num]['days']}')

                return True
            else:
                print('agent last days not passed')
                return False
        else:
            print(
                f'num ({num}) is out of range for interest level ({interest}).')
            return False
    else:
        print("Error not wroteBy valid found")
        return False


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
            wroteBy='client',

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
