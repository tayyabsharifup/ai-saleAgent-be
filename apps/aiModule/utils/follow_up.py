from apps.aiModule.utils.output_extractor import InterestLevel, FollowUpPlan, MessageResponse, ShouldFollowUp
from apps.aiModule.utils.util_model import get_chat_message_by_id, save_ai_message
from apps.users.models.manager_model import ManagerModel
from apps.users.models.lead_model import LeadModel
from langchain_core.messages import AIMessage
from IPython.display import Image
from typing import Literal
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
# import sys
import django

# # Add the project root to the Python path
# sys.path.append('/home/dawood/Desktop/ai_sales')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_sales.settings')
django.setup()


load_dotenv(override=True)


class SalesState(BaseModel):
    interest_level: str = ""
    heading: str = ""
    body: str = ""
    follow_up_date: int = 0
    contact_type: str = ""


class AITool:
    def __init__(self, lead_id):
        self.lead_id = lead_id
        self.messages = get_chat_message_by_id(lead_id)
        self.graph = self._build_graph()
        self.follow_up_rules = {
            "SHORT": [
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
            "MID": [
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
            "LONG": [
                {"contact_type": "mail", "days": 80},
                {"contact_type": "mail", "days": 180},
                {"contact_type": "mail", "days": 320}
            ],
            "None": [

            ]
        }

    def initialDecideNode(self, state: SalesState) -> Literal['classifier', '__end__']:
        if not self.messages:
            return END
        else:
            llm = ChatOpenAI(
                model='gpt-4.1-mini', temperature=0).with_structured_output(ShouldFollowUp)
            system_prompt = f"""
                You are Expert Follow Up planner. By giving the list of the Message interaction between Client, Agent and AI module.
                There would two scenario to which write a follow-up plan.
                First, Client has replied to your response by email or we have a call and now we need a response from AI.
                Second, You would decide that either we need to create follow up for Client if the client has no response and due date is passed and
                client did not responed or we do not need to make plan either waiting for client to response to our query or the due date is not passed yet.
                Here are follow_up rules based on the interest and number of days the client has not responsed
                {self.follow_up_rules}
            """
            system_message = SystemMessage(content=system_prompt)
            messages = [system_message] + self.messages
            response = llm.invoke(messages)
            print(response)
            if response and response.follow_up:
                return 'classifier'
            else:
                return END

    # def initialResponseNode(self, state: SalesState):
    #     system_prompt = """

    #         """
    #     try:
    #         manager = ManagerModel.objects.get(agent_model__leadmodel__id=self.lead_id)
    #         language = manager.language
    #         offer = manager.offer
    #         selling_point = manager.selling_point
    #         faq = manager.faq

    #     except Exception as e:
    #         language = ''
    #         offer = ''
    #         selling_point = ''
    #         faq = ''

    #     llm = ChatOpenAI(model='gpt-4.1-mini', temperature=0).with_structured_output(MessageResponse)
    #     system_prompt = f"""
    #     You are AI sales Assistant and Based on the information About the Lead and Agent.
    #     Generate Few Talking point for Lead Call
    #     Info About Client: {LeadModel.objects.get(id=self.lead_id).info}
    #     Language: {language}
    #     Offer: {offer}
    #     Selling Point: {selling_point}
    #     FAQ: {faq}
    #     """
    #     system_message = SystemMessage(content=system_prompt)
    #     messages = [system_message] + self.messages
    #     response = llm.invoke(messages)
    #     if response:
    #         state.heading = response.heading
    #         state.body = response.body
    #         state.contact_type = 'call'
    #         state.follow_up_date = 1
    #         state.interest_level = 'none'
    #         if not save_ai_message(self.lead_id, state):
    #             raise Exception("Failed to save AI message")
    #     else:
    #         raise Exception("Failed to generate response")
    #     return state

    def interestNode(self, state: SalesState):
        llm = ChatOpenAI(model='gpt-4.1-mini',
                         temperature=0).with_structured_output(InterestLevel)
        system_prompt = """
        Analyze the following sales conversation and classify the prospect's interest level into exactly one of these categories:
        
        SHORT: High interest - prospect shows clear buying signals, asks specific questions about pricing/closing, mentions timeline
        MID: Moderate interest - prospect shows some interest but has questions or concerns, needs more information
        LONG: Low interest - prospect is just exploring options, no clear commitment signals, general inquiries
        None: No interest - prospect explicitly states they are not interested or does not respond positively

        Make sure to keep the classification consistent with the conversation context
        And do not change the interest level unless there is a clear indication of a change in the prospect's engagement or interest.
        Try to classify the interest level based on the latest messages in the conversation.
        
        """
        system_message = SystemMessage(content=system_prompt)
        messages = [system_message] + self.messages
        response = llm.invoke(messages)
        if response and isinstance(response, InterestLevel):
            state.interest_level = response.level
        else:
            state.interest_level = 'none'
        return state

    def responseNode(self, state: SalesState):
        try:
            manager = ManagerModel.objects.get(
                agent_model__leadmodel__id=self.lead_id)
            language = manager.language
            offer = manager.offer
            selling_point = manager.selling_point
            faq = manager.faq

        except Exception as e:
            language = ''
            offer = ''
            selling_point = ''
            faq = ''

        llm = ChatOpenAI(model='gpt-4.1-mini',
                         temperature=0).with_structured_output(MessageResponse)
        system_prompt = f"""
        Based on the prospect's interest level, generate a follow-up response
        It would be one of the following:
        Contact Type either 'call' or 'mail': {state.contact_type}
        If Contact Type is call then generate point to talk about as bullet points,
        If email then generate email content.
        Interest Level: {state.interest_level}
        Info About Client: {LeadModel.objects.get(id=self.lead_id).info}
        Language: {language}
        Offer: {offer}
        Selling Point: {selling_point}
        FAQ: {faq}

        and here are products details:
            MoveAround
            Operated with a joystick from the basket

            MoveAround MA60
            Working Height: 6m
            Platform Size: 0.53m x 0.76m
            Weight: 466 kg
            Platform load: 150 kg

            MoveAround MA50
            Working Height: 5m
            Platform Size: 0.53m x 0.76m
            Weight: 331 kg
            Platform load: 150 kg

            MoveAround MA50-R
            Working Height: 5m
            Platform Size: 0.56m x 0.52m
            Weight: 343 kg
            Platform load: 150 kg

            PushAround
            Manually moved to where it's needed

            PushAround PA60
            Working Height: 6m
            Platform Size: 0.53m x 0.76m
            Weight: 466 kg
            Platform load: 150 kg

            PushAround PA50
            Working Height: 5m
            Platform Size: 0.53m x 0.76m
            Weight: 331 kg
            Platform load: 150 kg

            PushAround PA35
            Working Height: 5m
            Platform Size: 0.56m x 0.52m
            Weight: 343 kg
            Platform load: 150 kg

            StockPicker
            Drivable and has height-adjustable lifting table

            StockAround SP50
            Working Height: 5m
            Platform Size: 0.63m x 0.59m
            Weight: 386 kg
            Platform load: 165 kg
        """
        system_message = SystemMessage(content=system_prompt)
        messages = [system_message] + self.messages
        response = llm.invoke(messages)
        if response:
            state.heading = response.heading
            state.body = response.body
            if not save_ai_message(self.lead_id, state):
                raise Exception("Failed to save AI message")
        else:
            raise Exception("Failed to generate response")
        return state

    def followUpNode(self, state: SalesState):
        llm = ChatOpenAI(
            model='gpt-4.1', temperature=0).with_structured_output(FollowUpPlan)
        system_prompt = """
            You are AI-Assistant for Sales Agent.
            You are generating a follow-up response for Sales Agent to the client. 
            Consider the number of AI messages in the conversation and the interest level of the client.
            Response for client who did not respond to the last message.
            If the interest level is 'SHORT', generate a follow-up response with a contact type and days based on the follow-up rules.
            If the interest level is 'MID', generate a follow-up response with a contact type and days based on the follow-up rules.
            If the interest level is 'LONG', generate a follow-up response with a contact type and days based on the follow-up rules.
            If the interest level is 'None', Just return empty response and 0 days.
            Here is follow-up plan:
                "SHORT": [
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
                "MID": [
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
                "LONG": [
                    {"contact_type": "mail", "days": 80},
                    {"contact_type": "mail", "days": 180},
                    {"contact_type": "mail", "days": 320}
                ],
                "None": []
            
            You will decide either to make a call or send email and how many days later based on follow-up rules.
            Also, keep in mind that we have the contact information like Email and Phone.
            Follow up date SHOULD be greater than 0.
        """

        system_message = SystemMessage(content=system_prompt)
        messages = [system_message] + self.messages
        response = llm.invoke(messages)

        if response and isinstance(response, FollowUpPlan):
            state.follow_up_date = int(response.days)
            state.contact_type = response.contact_type
        else:
            state.follow_up_date = 0
            state.contact_type = 'none'

        return state

    def _build_graph(self):
        # Building the state graph
        builder = StateGraph(SalesState)
        builder.add_node('initial_decide', self.initialDecideNode)
        # builder.add_node('initial_response', self.initialResponseNode)
        builder.add_node('classifier', self.interestNode)
        builder.add_node('follow_up', self.followUpNode)
        builder.add_node('response', self.responseNode)

        builder.add_conditional_edges(START, self.initialDecideNode)
        # builder.add_edge('initial_response', END)
        builder.add_edge('classifier', 'follow_up')
        builder.add_edge('follow_up', 'response')
        builder.add_edge('response', END)
        return builder.compile()


def refreshAI(lead_id):
    ai_tool = AITool(lead_id)
    final_state = ai_tool.graph.invoke(SalesState())
    return final_state


if __name__ == "__main__":
    # print(f"Today's Date: {today_tool()}")
    # print(f"Date after adding 5 days: {add_days_tool(5)}")
    # lead_id = 2  # Example lead ID
    # ai_tool = AITool(lead_id)
    # image_data = ai_tool.graph.get_graph().draw_mermaid_png()
    # with open("follow_up_graph.png", "wb") as f:
    #     f.write(image_data)
    # print("Graph image saved to follow_up_graph.png")
    # Image(image_data)

    # print(ai_tool.messages)
    # if isinstance(ai_tool.messages[-1], AIMessage):
    #     print(ai_tool.messages[-1].content)
    # final_state = ai_tool.graph.invoke(SalesState())
    # print(final_state)

    refreshAI(2)
