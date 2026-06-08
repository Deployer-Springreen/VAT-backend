import hmac
import hashlib
import json
import urllib.request
import os
from datetime import datetime
from pymongo import MongoClient

# Load environment variables
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(basedir, ".env")
env_vars = {}
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            if "=" in line:
                parts = line.strip().split("=", 1)
                if len(parts) == 2:
                    env_vars[parts[0]] = parts[1]

mongo_uri = env_vars.get("MONGO_URI", "mongodb://localhost:27017")
webhook_secret = env_vars.get("RAZORPAY_WEBHOOK_SECRET", "")

print(f"Loaded MONGO_URI and Webhook Secret (ends with ...{webhook_secret[-4:] if webhook_secret else 'None'}).")

# 1. Connect to MongoDB Atlas
client = MongoClient(mongo_uri)
db = client.get_default_database() # Auto-detects the 'ecommerce' DB from URI

order_id = "TEST_WEBHOOK_ORDER_123"
user_id = "TEST_WEBHOOK_USER_123"

# Create/Reset test order
db.orders.delete_one({"_id": order_id})
db.orders.insert_one({
    "_id": order_id,
    "user_id": user_id,
    "total_amount": 250.00,
    "status": "PENDING",
    "created_at": datetime.utcnow()
})

# Create test cart
db.carts.delete_one({"_id": user_id})
db.carts.insert_one({
    "_id": user_id,
    "items": [{"product_id": "test_product", "quantity": 1}],
    "coupon": None
})

print(f"Created test order '{order_id}' (PENDING) and populated test cart.")

# 2. Simulate Razorpay Webhook Payload
payload = {
    "entity": "event",
    "account_id": "acc_webhook_test",
    "event": "order.paid",
    "contains": ["order", "payment"],
    "payload": {
        "order": {
            "entity": {
                "id": "order_mock123",
                "notes": {
                    "order_id": order_id,
                    "user_id": user_id
                }
            }
        },
        "payment": {
            "entity": {
                "id": "pay_mock123",
                "notes": {
                    "order_id": order_id,
                    "user_id": user_id
                }
            }
        }
    }
}

req_data = json.dumps(payload).encode("utf-8")
headers = {"Content-Type": "application/json"}

# Compute HMAC signature if webhook secret is configured
if webhook_secret:
    signature = hmac.new(
        webhook_secret.encode('utf-8'),
        req_data,
        hashlib.sha256
    ).hexdigest()
    headers["X-Razorpay-Signature"] = signature
    print("Computed HMAC signature successfully.")
else:
    print("WARNING: Webhook secret not configured in .env, signature verification will be bypassed.")

# Send webhook request to local running server
try:
    req = urllib.request.Request(
        "http://localhost:8000/payment/webhook",
        data=req_data,
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req) as res:
        print("Server Webhook response status:", res.status)
        print("Server Webhook response body:", res.read().decode())
        
    # Check if order is confirmed and cart is empty
    updated_order = db.orders.find_one({"_id": order_id})
    updated_cart = db.carts.find_one({"_id": user_id})
    
    print("Updated order status in DB:", updated_order.get("status") if updated_order else "Not Found")
    print("Updated cart items in DB:", updated_cart.get("items") if updated_cart else "Not Found")
    
    if updated_order and updated_order.get("status") == "CONFIRMED" and updated_cart and len(updated_cart.get("items")) == 0:
        print("\n✅ SUCCESS: Webhook tested successfully with signature verification!")
    else:
        print("\n❌ FAILED: Status or cart not updated.")
        
    # Cleanup test documents
    db.orders.delete_one({"_id": order_id})
    db.carts.delete_one({"_id": user_id})
    print("Cleaned up test DB documents.")
except Exception as e:
    print("Error during test execution:", e)
