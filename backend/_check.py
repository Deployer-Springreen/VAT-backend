import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
async def chk():
    db = AsyncIOMotorClient(os.getenv('MONGO_URI')).ecommerce
    cursor = db.content_controller.find({'section_name': 'home_sections'}).sort('display_order', 1)
    async for c in cursor:
        cv = c.get('content_value', {})
        key = c.get('content_key','')
        tid = c['_id']
        if isinstance(cv, dict):
            prods = cv.get('products', [])
            print(f"{tid} | {key} | order={c.get('display_order')} | title={cv.get('title','')} | products_cnt={len(prods) if prods else 0}")
        else:
            print(f"{tid} | {key} | order={c.get('display_order')} | string={cv}")
    print('---')
    pipeline = [{"$match": {"section_name": "home_sections"}}, {"$group": {"_id": "$content_key", "count": {"$sum": 1}, "ids": {"$push": "$_id"}}}, {"$match": {"count": {"$gt": 1}}}]
    async for d in db.content_controller.aggregate(pipeline):
        print(f"DUPLICATE: {d['_id']} appears {d['count']} times -> ids: {d['ids']}")
asyncio.run(chk())
