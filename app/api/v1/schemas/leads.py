from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, model_validator


class CF7LeadPayload(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    message: str | None = None
    source: str = "website_cf7"
    metadata_json: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize_name(self) -> "CF7LeadPayload":
        if self.name and not self.first_name and not self.last_name:
            parts = self.name.strip().split(" ", 1)
            self.first_name = parts[0]
            self.last_name = parts[1] if len(parts) > 1 else None
        return self


class LeadPatchRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    status: str | None = None
    score: int | None = None
    notes: str | None = None
    metadata_json: dict[str, Any] | None = None


class LeadTagRequest(BaseModel):
    tag: str


class LeadResponse(BaseModel):
    id: int
    first_name: str | None
    last_name: str | None
    email: EmailStr | None
    phone: str | None
    source: str
    status: str
    score: int
    notes: str | None
    metadata_json: dict[str, Any]
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
