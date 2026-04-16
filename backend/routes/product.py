from fastapi import APIRouter, HTTPException
from database.product import ProductCreate, ProductUpdate
from services.product_id_generator import generate_product_id
from db import db

router = APIRouter(prefix="/product", tags=["product"])


# ✅ CREATE PRODUCT
@router.post("/create")
async def create_product(data: ProductCreate):

    product_id = await generate_product_id(db)

    product = data.dict()
    product["_id"] = product_id   # ✅ use _id only

    await db.products.insert_one(product)

    return {
        "msg": "product created",
        "_id": product_id
    }


# ✅ GET ALL PRODUCTS
@router.get("/all")
async def get_all_products():

    products = await db.products.find().to_list(100)

    for p in products:
        p["_id"] = str(p["_id"])

    return products


# ✅ GET SINGLE PRODUCT
@router.get("/{product_id}")
async def get_product(product_id: str):

    product = await db.products.find_one({"_id": product_id})   # ✅ FIX

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product["_id"] = str(product["_id"])
    return product


# ✅ UPDATE PRODUCT
@router.put("/update/{product_id}")
async def update_product(product_id: str, data: ProductUpdate):

    update_data = {k: v for k, v in data.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    result = await db.products.update_one(
        {"_id": product_id},   # ✅ FIX
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"msg": "product updated"}


# ✅ DELETE PRODUCT
@router.delete("/delete/{product_id}")
async def delete_product(product_id: str):

    result = await db.products.delete_one({"_id": product_id})   # ✅ FIX

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"msg": "product deleted"}