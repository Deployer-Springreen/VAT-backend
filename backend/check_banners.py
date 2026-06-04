import asyncio
from db import db
from utils.json_helper import mongo_dumps

async def check_banners():
    banners = await db.banners.find({}).to_list(100)
    print(f"Total banners: {len(banners)}")
    for b in banners:
        print(f"- {b.get('title')}: {b.get('status')} ({b.get('image_url')})")

if __name__ == "__main__":
    asyncio.run(check_banners())
