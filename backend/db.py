from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

client = AsyncIOMotorClient(
    Config.MONGO_URI,
    minPoolSize=10,
    maxPoolSize=100,
    maxIdleTimeMS=60000,
    waitQueueTimeoutMS=5000
)
db = client["ecommerce"]