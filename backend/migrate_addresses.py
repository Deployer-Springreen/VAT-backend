import asyncio
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def migrate_addresses():
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["ecommerce"]

    print("Starting address migration...")

    cursor = db.users.find({"addresses": {"$exists": True, "$not": {"$size": 0}}})

    async for user in cursor:
        user_id = user["_id"]
        addresses = user.get("addresses", [])
        modified = False

        for addr in addresses:
            if "address_id" not in addr:
                addr["address_id"] = str(uuid.uuid4())
                modified = True

        if modified:
            await db.users.update_one(
                {"_id": user_id},
                {"$set": {"addresses": addresses}}
            )
            print(f"Updated addresses for user: {user_id}")

    print("Migration complete.")

if __name__ == "__main__":
    asyncio.run(migrate_addresses())
