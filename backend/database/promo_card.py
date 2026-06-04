from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import Field
from .base import AppBaseModel

class PromoCardBase(AppBaseModel):
    title: str
    subtitle: Optional[str] = None
    badge_text: str = "Weekend Discount"
    badge_link: str = "#"
    button_text: str = "Shop Now"
    button_link: str = "#"
    image_url: str
    order: int = 1
    status: str = "active" # "active" or "inactive"

class PromoCardCreate(PromoCardBase):
    pass

class PromoCardUpdate(AppBaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    badge_text: Optional[str] = None
    badge_link: Optional[str] = None
    button_text: Optional[str] = None
    button_link: Optional[str] = None
    image_url: Optional[str] = None
    order: Optional[int] = None
    status: Optional[str] = None

class PromoCardOut(PromoCardBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
