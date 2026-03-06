from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class CampaignCreateRequest(BaseModel):
    platform: str
    campaign_name: str
    objective: str
    status: str = "draft"
    daily_budget: Decimal | None = None
    total_budget: Decimal | None = None
    cpa_target: Decimal | None = None
    start_date: date | None = None
    end_date: date | None = None
    icp_segment: str | None = None
    season_tag: str | None = None
    created_by: str = "human"


class AdCreativeCreateRequest(BaseModel):
    headline: str | None = None
    body_text: str | None = None
    image_url: str | None = None
    video_url: str | None = None
    cta_text: str | None = None
    cta_url: str | None = None
    variant_label: str | None = None
    status: str = "active"


class AdCreativeResponse(BaseModel):
    id: int
    campaign_id: int
    headline: str | None
    body_text: str | None
    image_url: str | None
    video_url: str | None
    cta_text: str | None
    cta_url: str | None
    variant_label: str | None
    status: str

    model_config = {"from_attributes": True}


class CampaignResponse(BaseModel):
    id: int
    platform: str
    campaign_name: str
    objective: str
    status: str
    daily_budget: Decimal | None
    total_budget: Decimal | None
    cpa_target: Decimal | None
    start_date: date | None
    end_date: date | None
    icp_segment: str | None
    season_tag: str | None
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
