from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class SequenceEnrollmentCreateRequest(BaseModel):
    lead_id: int
    next_run_at: datetime | None = None


class SequenceEnrollmentResponse(BaseModel):
    id: int
    lead_id: int
    sequence_id: int
    current_step: int
    status: str
    next_run_at: datetime | None
    enrolled_at: datetime

    model_config = {"from_attributes": True}


class MessageSendRequest(BaseModel):
    lead_id: int
    channel: str
    subject: str | None = None
    body_text: str
    enrollment_id: int | None = None
    step_id: int | None = None
    external_message_id: str | None = None


class MessageSendResponse(BaseModel):
    status: str
    message_id: int
    channel: str
    lead_id: int


class TwilioWebhookPayload(BaseModel):
    from_phone: str = Field(alias="From")
    body: str = Field(default="", alias="Body")
    message_status: str | None = Field(default=None, alias="MessageStatus")


class GmailInboundPayload(BaseModel):
    from_email: EmailStr
    subject: str | None = None
    body: str = ""
