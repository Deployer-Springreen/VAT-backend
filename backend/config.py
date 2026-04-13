from dotenv import load_dotenv
import os
load_dotenv()
class Config:
    MONGO_URI=os.getenv("MONGO_URI")
    JWT_SECRET=os.getenv("JWT_SECRET", "super-secret-key-for-dev-only")
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=60
    