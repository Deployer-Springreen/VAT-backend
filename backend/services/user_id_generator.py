import uuid

async def generate_user_id(db):
    # Generate a random UUID and take the first 6 characters of its hex representation
    # We use a loop to ensure uniqueness, though with 6 hex chars (16.7M combinations)
    # and a check in the database, it's safer.
    while True:
        uid = uuid.uuid4().hex[:6]
        # Check if this ID already exists in the users collection
        existing = await db.users.find_one({"_id": uid})
        if not existing:
            return uid