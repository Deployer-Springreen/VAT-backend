from fastapi import APIRouter, HTTPException
from typing import List
from db import db
from database.base import SuccessResponse
from utils.json_helper import mongo_dumps, mongo_loads

router = APIRouter(prefix="/promo-cards", tags=["Promo Cards"])

@router.get("", response_model=SuccessResponse)
async def get_active_promo_cards():
    cards = await db.promo_cards.find({"status": "active"}).sort("order", 1).to_list(100)
    return SuccessResponse(data=mongo_loads(mongo_dumps(cards)))
