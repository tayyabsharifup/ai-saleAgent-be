from pydantic import BaseModel, Field
from enum import Enum


class InterestCategory(str, Enum):
    SHORT = "short"
    MID = "mid"
    LONG = "long"
    NONE = "none"


class InterestLevel(BaseModel):
    level: InterestCategory = Field(
        default=InterestCategory.NONE,
        description="The interest level of the lead, categorized as SHORT, MID, LONG, or NONE."
    )


class ContactType(str, Enum):
    CALL = "call"
    EMAIL = "email"


class FollowUpPlan(BaseModel):
    days: int = Field(
        description="Number of days after which the follow-up should occur."
    )
    contact_type: ContactType = Field(
        default=ContactType.CALL,
        description="Type of contact for the follow-up, either CALL or EMAIL."
    )

class ShouldFollowUp(BaseModel):
    follow_up: bool = Field(description="Whether a follow-up is needed.")

class MessageResponse(BaseModel):
    heading: str = Field(description="Heading of the message.")
    body: str = Field(description="Body of the message.")
    key_points: list[str] = Field(default_factory=list, description="Optional list of 3-4 key summary points from the chat history.")
