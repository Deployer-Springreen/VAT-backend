from db import db
from fastapi import HTTPException


# ✅ MOVE ITEM TO CART (ATOMIC + SAFE)
async def move_item_to_cart(user_id: str, product_id: str):

    # 1️⃣ ATOMIC REMOVE FROM WISHLIST
    result = await db.wishlist.update_one(
        {
            "_id": user_id,
            "items.product_id": product_id
        },
        {
            "$pull": {
                "items": {"product_id": product_id}
            }
        }
    )

    # 👉 if nothing removed → already moved / not present
    if result.modified_count == 0:
        return "item already moved or not present"

    # 2️⃣ UPDATE CART (increment if exists)
    result = await db.carts.update_one(
        {
            "_id": user_id,
            "items.product_id": product_id
        },
        {
            "$inc": {"items.$.quantity": 1}
        }
    )

    # 3️⃣ IF ITEM NOT IN CART → ADD IT
    if result.matched_count == 0:
        await db.carts.update_one(
            {"_id": user_id},
            {
                "$addToSet": {   # ✅ prevents duplicates
                    "items": {
                        "product_id": product_id,
                        "quantity": 1
                    }
                }
            },
            upsert=True
        )

    return "moved to cart"


# ✅ BULK ADD TO WISHLIST (ATOMIC + NO DUPLICATES)
async def bulk_add_wishlist(user_id: str, product_ids: list):

    if not product_ids:
        raise HTTPException(status_code=400, detail="No products provided")

    # 🔥 fetch valid products using _id
    products = await db.products.find(
        {"_id": {"$in": product_ids}}
    ).to_list(length=len(product_ids))

    if not products:
        raise HTTPException(status_code=404, detail="No valid products found")

    # prepare items
    items = [
        {
            "product_id": str(p["_id"]),
            "product_name": p.get("product_name"),
            "price": p.get("price", 0)
        }
        for p in products
    ]

    # ✅ ATOMIC UPSERT + NO DUPLICATES
    await db.wishlist.update_one(
        {"_id": user_id},   # 🔥 use _id only
        {
            "$addToSet": {
                "items": {"$each": items}
            }
        },
        upsert=True
    )

    return "wishlist updated"