from db import db
from fastapi import HTTPException
from datetime import datetime


# ✅ CALCULATE SUMMARY (no change needed)
async def calculate_summary(cart):
    subtotal = sum(item["price"] * item.get("quantity", 1) for item in cart.get("items", []))
    discount = 0

    if cart.get("coupon"):
        coupon = cart["coupon"]
        if coupon.get("type") == "percent":
            discount = subtotal * (coupon.get("discount", 0) / 100)
        else:
            discount = coupon.get("discount", 0)

    shipping = 0 if subtotal > 100 else 10
    total = subtotal - discount + shipping

    return {
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "shipping": shipping,
        "total": round(total, 2)
    }


# ✅ BULK ADD TO CART (ATOMIC + NO DUPLICATES)
async def bulk_add_items(user_id: str, product_ids: list):
    if not product_ids:
        raise HTTPException(status_code=400, detail="No products provided")

    # ✅ fetch valid products
    products = await db.products.find(
        {"_id": {"$in": product_ids}}
    ).to_list(length=len(product_ids))

    if not products:
        raise HTTPException(status_code=404, detail="No valid products found")

    # ✅ prepare items
    items = [
        {
            "product_id": str(p["_id"]),
            "product_name": p.get("product_name"),
            "price": p.get("price", 0),
            "quantity": 1
        }
        for p in products
    ]

    # 🔥 ATOMIC UPSERT (no find_one)
    await db.carts.update_one(
        {"_id": user_id},   # ✅ FIX (no user_id field)
        {
            "$addToSet": {
                "items": {"$each": items}
            }
        },
        upsert=True
    )

    return "items added to cart"


# ✅ UPDATE QUANTITY (ATOMIC)
async def update_cart_quantity(user_id: str, product_id: str, quantity: int):

    if quantity < 1:
        # remove item if quantity = 0
        await db.carts.update_one(
            {"_id": user_id},
            {"$pull": {"items": {"product_id": product_id}}}
        )
        return "item removed"

    result = await db.carts.update_one(
        {
            "_id": user_id,
            "items.product_id": product_id
        },
        {
            "$set": {"items.$.quantity": quantity}
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return "quantity updated"


# ✅ REMOVE ITEM (ATOMIC)
async def remove_item_from_cart(user_id: str, product_id: str):

    result = await db.carts.update_one(
        {"_id": user_id},
        {"$pull": {"items": {"product_id": product_id}}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return "item removed"


# ✅ CHECKOUT (SAFE)
async def checkout_cart(user_id: str):

    cart = await db.carts.find_one({"_id": user_id})

    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")

    summary = await calculate_summary(cart)

    order = {
        "_id": f"ORD{datetime.utcnow().timestamp()}",
        "user_id": user_id,
        "items": cart["items"],
        "total_amount": summary["total"],
        "status": "PENDING",
        "created_at": datetime.utcnow()
    }

    result = await db.orders.insert_one(order)

    # ✅ clear cart atomically
    await db.carts.update_one(
        {"_id": user_id},
        {"$set": {"items": [], "coupon": None}}
    )

    return str(result.inserted_id)