import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

PRODUCT_MAP = {
    "recently_added": ["PRD000001", "PRD000002", "PRD000003"],
    "top_rated":      ["PRD000004", "PRD000005", "PRD000006"],
    "top_selling":    ["PRD000007", "PRD000008", "PRD000009"],
    "deals_of_day":   ["PRD000010", "PRD000001", "PRD000002"],
}

async def fix_home_sections():
    basedir = os.path.dirname(__file__)
    load_dotenv(os.path.join(basedir, ".env"))
    uri = os.getenv('MONGO_URI')
    if not uri:
        print("MONGO_URI not found in .env")
        return

    client = AsyncIOMotorClient(uri)
    db = client.ecommerce

    updated = 0

    # Case 1: string content_value (old format)
    cursor = db.content_controller.find({
        "section_name": "home_sections",
        "content_value": {"$type": "string"}
    })
    async for item in cursor:
        title = item["content_value"]
        products = PRODUCT_MAP.get(item["content_key"], ["PRD000001", "PRD000002", "PRD000003"])
        new_value = {"title": title, "products": products}
        await db.content_controller.update_one(
            {"_id": item["_id"]},
            {"$set": {"content_value": new_value}}
        )
        print(f"Fixed string->object: {item['content_key']} -> {len(products)} products")
        updated += 1

    # Case 2: object content_value with empty/missing products
    cursor2 = db.content_controller.find({
        "section_name": "home_sections",
        "content_value": {"$type": "object"}
    })
    async for item in cursor2:
        cv = item.get("content_value", {})
        products = cv.get("products") if isinstance(cv, dict) else None
        if not products or (isinstance(products, list) and len(products) == 0):
            new_products = PRODUCT_MAP.get(item["content_key"], ["PRD000001", "PRD000002", "PRD000003"])
            new_value = {"title": cv.get("title", item["content_key"]), "products": new_products}
            await db.content_controller.update_one(
                {"_id": item["_id"]},
                {"$set": {"content_value": new_value}}
            )
            print(f"Fixed empty products: {item['content_key']} -> {len(new_products)} products")
            updated += 1

    if updated == 0:
        print("All home sections already have products assigned.")
    else:
        print(f"\nFixed {updated} home section(s)")
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_home_sections())
