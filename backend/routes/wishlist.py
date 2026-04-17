from fastapi import APIRouter, HTTPException, Depends
from db import db
from database.wishlist import AddToWishlistBulkRequest
from database.base import SuccessResponse
from utils.security import get_current_user
from services.wishlist_service import bulk_add_wishlist

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


# ✅ BULK ADD
@router.post("/bulk-add", response_model=SuccessResponse[dict])
async def bulk_add_to_wishlist(
    data: AddToWishlistBulkRequest,
    current_user_id: str = Depends(get_current_user)
):
    msg = await bulk_add_wishlist(current_user_id, data.product_ids)
    return SuccessResponse(message=msg)


# ✅ GET
@router.get("/", response_model=SuccessResponse[dict])
async def get_wishlist(current_user_id: str = Depends(get_current_user)):

    wishlist = await db.wishlist.find_one({"_id": current_user_id})

    if not wishlist:
        return SuccessResponse(data={"items": []})

    return SuccessResponse(data=wishlist)


# ✅ REMOVE
@router.delete("/remove/{product_id}", response_model=SuccessResponse[dict])
async def remove_item(product_id: str, current_user_id: str = Depends(get_current_user)):

    result = await db.wishlist.update_one(
        {"_id": current_user_id},
        {"$pull": {"items": {"product_id": product_id}}}
    )

    if result.modified_count == 0:
        return SuccessResponse(message="already removed")

    return SuccessResponse(message="item removed")


# ✅ CLEAR
@router.delete("/clear", response_model=SuccessResponse[dict])
async def clear_wishlist(current_user_id: str = Depends(get_current_user)):

    await db.wishlist.update_one(
        {"_id": current_user_id},
        {"$set": {"items": []}}
    )

    return SuccessResponse(message="wishlist cleared")


# ✅ MOVE TO CART
@router.post("/move-to-cart", response_model=SuccessResponse[dict])
async def move_to_cart(product_id: str, current_user_id: str = Depends(get_current_user)):

    result = await db.wishlist.update_one(
        {"_id": current_user_id, "items.product_id": product_id},
        {"$pull": {"items": {"product_id": product_id}}}
    )

    if result.modified_count == 0:
        return SuccessResponse(message="not in wishlist")

    await db.carts.update_one(
        {"_id": current_user_id},
        {
            "$addToSet": {
                "items": {
                    "product_id": product_id,
                    "quantity": 1
                }
            }
        },
        upsert=True
    )

    return SuccessResponse(message="moved to cart")