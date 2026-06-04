import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

SERVICE_ITEMS = [
    {
        "section_name": "services",
        "content_key": "best_prices",
        "content_value": {"title": "Best Prices & Offers", "desc": "We prepared special discounts you on grocery products."},
        "display_order": 1,
    },
    {
        "section_name": "services",
        "content_key": "return_policy",
        "content_value": {"title": "100% Return Policy", "desc": "We prepared special discounts you on grocery products."},
        "display_order": 2,
    },
    {
        "section_name": "services",
        "content_key": "support_247",
        "content_value": {"title": "Support 24/7", "desc": "We prepared special discounts you on grocery products."},
        "display_order": 3,
    },
    {
        "section_name": "services",
        "content_key": "great_offer",
        "content_value": {"title": "Great Offer Daily Deal", "desc": "We prepared special discounts you on grocery products."},
        "display_order": 4,
    },
]

async def fix_services():
    basedir = os.path.dirname(__file__)
    load_dotenv(os.path.join(basedir, ".env"))
    uri = os.getenv('MONGO_URI')
    if not uri:
        print("MONGO_URI not found in .env")
        return

    client = AsyncIOMotorClient(uri)
    db = client.ecommerce

    created = 0
    updated = 0
    for item in SERVICE_ITEMS:
        existing = await db.content_controller.find_one({
            "section_name": "services",
            "content_key": item["content_key"],
        })
        if existing:
            if isinstance(existing.get("content_value"), str):
                await db.content_controller.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {"content_value": item["content_value"]}}
                )
                print(f"Updated {item['content_key']}")
                updated += 1
            else:
                print(f"Skipped {item['content_key']} (already has object content_value)")
        else:
            from datetime import datetime
            import uuid
            doc = {**item, "_id": f"CONT{uuid.uuid4().hex[:8].upper()}", "is_active": True, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
            await db.content_controller.insert_one(doc)
            print(f"Created {item['content_key']}")
            created += 1

    print(f"\nCreated: {created}, Updated: {updated}")
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_services())
