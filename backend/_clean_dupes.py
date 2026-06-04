import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
async def clean():
    db = AsyncIOMotorClient(os.getenv('MONGO_URI')).ecommerce
    # remove stray auto-created entry
    await db.content_controller.delete_one({"_id": "CONT231E67CE"})
    print("Removed stray new_1780028939566 entry")
    # remove duplicate top_rated (keep CONT9D18646E which has proper title "Top Rated")
    await db.content_controller.delete_one({"_id": "CONT3C7FFDB2"})
    print("Removed duplicate top_rated (wrong title)")
    # remove duplicate top_selling (keep CONT0266C2EC which has proper title "Top Selling")
    await db.content_controller.delete_one({"_id": "CONT8EC4A935"})
    print("Removed duplicate top_selling (wrong title)")
    print("Done cleaning duplicates")
asyncio.run(clean())
