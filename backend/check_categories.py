import asyncio
from db import db

async def check_categories():
    categories = await db.categories.find({}).to_list(100)
    print(f"Total categories: {len(categories)}")
    for c in categories:
        print(f"- {c.get('category_name')}: {c.get('_id')}")

    products = await db.products.find({}).to_list(100)
    print(f"\nTotal products: {len(products)}")
    category_counts = {}
    for p in products:
        cat_id = p.get('category_id')
        category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
    
    for cat_id, count in category_counts.items():
        print(f"- Category {cat_id}: {count} products")

if __name__ == "__main__":
    asyncio.run(check_categories())
