from db import db
from database.address import AddressEmbedded
from fastapi import HTTPException
import uuid

async def add_address(user_id: str, address: AddressEmbedded):
    address_data = address.model_dump()
    if not address_data.get("address_id"):
        address_data["address_id"] = str(uuid.uuid4())

    result = await db.users.update_one(
        {"_id": user_id},
        {"$push": {"addresses": address_data}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to add address")

async def get_addresses(user_id: str, skip: int = 0, limit: int = 10):
    limit = min(limit, 100)
    user = await db.users.find_one(
        {"_id": user_id},
        {"addresses": {"$slice": [skip, limit]}}
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.get("addresses", [])

async def update_address(user_id: str, address_id: str, address: AddressEmbedded):
    address_data = address.model_dump()
    address_data["address_id"] = address_id # Ensure ID stays same

    result = await db.users.update_one(
        {"_id": user_id, "addresses.address_id": address_id},
        {"$set": {"addresses.$": address_data}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Address not found")
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update address")

async def delete_address(user_id: str, address_id: str):
    result = await db.users.update_one(
        {"_id": user_id},
        {"$pull": {"addresses": {"address_id": address_id}}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Address not found")
