from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
import logging

logger = logging.getLogger("auth-service")

if not Config.MONGO_URI:
    logger.critical("MONGO_URI missing. Ensure backend/.env or environment sets MONGO_URI.")
    raise RuntimeError("MONGO_URI is required for MongoDB connection.")

client = AsyncIOMotorClient(
    Config.MONGO_URI,
    minPoolSize=10,
    maxPoolSize=100,
    maxIdleTimeMS=60000,
    waitQueueTimeoutMS=5000,
    serverSelectionTimeoutMS=5000, # Fail faster if server is down
    connectTimeoutMS=10000
)

db = client["ecommerce"]

async def verify_mongodb_connection():
    try:
        # The ping command is cheap and does not require auth.
        await client.admin.command('ping')
        logger.info("MongoDB connection verified successfully")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return False
