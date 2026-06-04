import asyncio
from db import db
from datetime import datetime
import uuid

async def seed_promo_cards():
    print("Seeding Promo Cards...")
    
    # Clear existing promo cards
    await db.promo_cards.delete_many({})
    
    promo_cards = [
        {
            "_id": f"PRM{uuid.uuid4().hex[:8].upper()}",
            "title": "Exotic Tropical Fruits",
            "subtitle": "Fresh from Tropics",
            "badge_text": "New Arrival",
            "badge_link": "#",
            "button_text": "Shop Now",
            "button_link": "shop-grid-top-filter.html",
            "image_url": "assets/images/banner/01.jpg",
            "order": 1,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": f"PRM{uuid.uuid4().hex[:8].upper()}",
            "title": "Bakery Specials",
            "subtitle": "Handmade with Love",
            "badge_text": "Best Seller",
            "badge_link": "#",
            "button_text": "Explore",
            "button_link": "shop-grid-top-filter.html",
            "image_url": "assets/images/banner/02.jpg",
            "order": 2,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": f"PRM{uuid.uuid4().hex[:8].upper()}",
            "title": "Dairy Delights",
            "subtitle": "Pure & Organic",
            "badge_text": "20% OFF",
            "badge_link": "#",
            "button_text": "Order Now",
            "button_link": "shop-grid-top-filter.html",
            "image_url": "assets/images/banner/03.jpg",
            "order": 3,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": f"PRM{uuid.uuid4().hex[:8].upper()}",
            "title": "Seafood Feast",
            "subtitle": "Catch of the Day",
            "badge_text": "Limited Time",
            "badge_link": "#",
            "button_text": "Shop Now",
            "button_link": "shop-grid-top-filter.html",
            "image_url": "assets/images/banner/04.jpg",
            "order": 4,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": f"PRM{uuid.uuid4().hex[:8].upper()}",
            "title": "Strawberry Water Drinks",
            "subtitle": "Flavors Awesome",
            "badge_text": "Weekend Discount",
            "badge_link": "#",
            "button_text": "Shop Now",
            "button_link": "shop-grid-top-filter.html",
            "image_url": "assets/images/banner/05.jpg",
            "order": 5,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": f"PRM{uuid.uuid4().hex[:8].upper()}",
            "title": "Fresh Organic Vegetables",
            "subtitle": "Direct from Farm",
            "badge_text": "10% OFF",
            "badge_link": "#",
            "button_text": "Go to Shop",
            "button_link": "shop-grid-top-filter.html",
            "image_url": "assets/images/banner/06.jpg",
            "order": 6,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": f"PRM{uuid.uuid4().hex[:8].upper()}",
            "title": "Gourmet Snacks",
            "subtitle": "Satisfy Your Cravings",
            "badge_text": "Buy 1 Get 1",
            "badge_link": "#",
            "button_text": "Discover",
            "button_link": "shop-grid-top-filter.html",
            "image_url": "assets/images/banner/07.jpg",
            "order": 7,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": f"PRM{uuid.uuid4().hex[:8].upper()}",
            "title": "Healthy Nuts & Seeds",
            "subtitle": "Protein Packed",
            "badge_text": "Superfood",
            "badge_link": "#",
            "button_text": "Shop Now",
            "button_link": "shop-grid-top-filter.html",
            "image_url": "assets/images/banner/08.png",
            "order": 8,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": f"PRM{uuid.uuid4().hex[:8].upper()}",
            "title": "Fresh Morning Coffee",
            "subtitle": "Brewed to Perfection",
            "badge_text": "Morning Special",
            "badge_link": "#",
            "button_text": "Buy Now",
            "button_link": "shop-grid-top-filter.html",
            "image_url": "assets/images/banner/09.jpg",
            "order": 9,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    if promo_cards:
        await db.promo_cards.insert_many(promo_cards)
        print(f"Successfully seeded {len(promo_cards)} promo cards.")
    else:
        print("No promo cards to seed.")

if __name__ == "__main__":
    asyncio.run(seed_promo_cards())
