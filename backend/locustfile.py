from locust import HttpUser, task, between
import random
import string
import uuid

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def random_phone():
    return ''.join(random.choices(string.digits, k=10))

class EcommerceUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """
        Setup: Signup and Signin to get token
        """
        self.email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.password = "Password123!"
        self.phone = random_phone()
        self.name = f"User_{random_string(5)}"

        # 1. Signup - Endpoint: POST /auth/signup
        self.client.post("/auth/signup", json={
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "password": self.password
        })

        # 2. Signin - Endpoint: POST /auth/signin
        signin_res = self.client.post("/auth/signin", json={
            "identifier": self.email,
            "password": self.password
        })

        if signin_res.status_code == 200:
            data = signin_res.json()["data"]
            self.token = data["access_token"]
            self.user_id = data["user_id"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

        # Local data stores for this user session
        self.category_ids = []
        self.subcategory_ids = []
        self.product_ids = []
        self.order_ids = []
        self.payment_ids = []
        self.review_ids = []
        self.return_ids = []
        self.address_indices = []

    # -------------------------
    # 🔐 AUTH & PROFILE
    # -------------------------
    @task(1)
    def auth_flow(self):
        if not self.token: return

        # Profile Update - Endpoint: POST /auth/profile/{user_id}
        self.client.post(f"/auth/profile/{self.user_id}", json={
            "name": f"{self.name}_updated",
            "phone": self.phone,
            "email": self.email,
            "address": "123 Updated St"
        }, headers=self.headers, name="/auth/profile/[id]")

        # Forgot Password - Endpoint: POST /auth/forgot-password
        self.client.post("/auth/forgot-password", json={"email": self.email})

        # Reset Password - Endpoint: POST /auth/reset-password
        self.client.post("/auth/reset-password", json={
            "email": self.email,
            "otp": "123456",
            "new_password": "NewPassword123!"
        })

    # -------------------------
    # 📁 CATEGORY & SUBCATEGORY
    # -------------------------
    @task(2)
    def category_lifecycle(self):
        if not self.token: return
        # Create - Endpoint: POST /category/create
        res = self.client.post("/category/create", json={
            "category_name": f"Cat_{random_string(5)}"
        }, headers=self.headers)
        if res.status_code == 201:
            cat_id = res.json()["data"]["_id"]
            self.category_ids.append(cat_id)

            # Get - Endpoint: GET /category/{category_id}
            self.client.get(f"/category/{cat_id}", headers=self.headers, name="/category/[id]")

            # Update - Endpoint: PUT /category/update/{category_id}
            self.client.put(f"/category/update/{cat_id}", json={
                "category_name": f"Cat_{random_string(5)}_upd"
            }, headers=self.headers, name="/category/update/[id]")

            # List All - Endpoint: GET /category/all
            self.client.get("/category/all", headers=self.headers)

    @task(2)
    def subcategory_lifecycle(self):
        if not self.token or not self.category_ids: return
        cat_id = random.choice(self.category_ids)

        # Create - Endpoint: POST /subcategory/create
        res = self.client.post("/subcategory/create", json={
            "subcategory_name": f"Sub_{random_string(5)}",
            "category_id": cat_id
        }, headers=self.headers)

        if res.status_code == 201:
            subcat_id = res.json()["data"]["_id"]
            self.subcategory_ids.append(subcat_id)

            # Get - Endpoint: GET /subcategory/{subcategory_id}
            self.client.get(f"/subcategory/{subcat_id}", headers=self.headers, name="/subcategory/[id]")

            # Update - Endpoint: PUT /subcategory/update/{subcategory_id}
            self.client.put(f"/subcategory/update/{subcat_id}", json={
                "subcategory_name": f"Sub_{random_string(5)}_upd",
                "category_id": cat_id
            }, headers=self.headers, name="/subcategory/update/[id]")

            # List All - Endpoint: GET /subcategory/all
            self.client.get("/subcategory/all", headers=self.headers)

    # -------------------------
    # 📦 PRODUCT
    # -------------------------
    @task(5)
    def product_lifecycle(self):
        if not self.token or not self.category_ids or not self.subcategory_ids: return
        cat_id = random.choice(self.category_ids)
        subcat_id = random.choice(self.subcategory_ids)

        # Create - Endpoint: POST /product/create
        res = self.client.post("/product/create", json={
            "product_name": f"Prod_{random_string(5)}",
            "description": "Load test product description",
            "price": float(random.randint(10, 1000)),
            "category_id": cat_id,
            "subcategory_id": subcat_id,
            "variants": [
                {"sku": f"SKU_{random_string(3)}", "size": "M", "color": "Red", "stock_quantity": 100}
            ]
        }, headers=self.headers)

        if res.status_code == 201:
            prod_id = res.json()["data"]["_id"]
            self.product_ids.append(prod_id)

            # Get - Endpoint: GET /product/{product_id}
            self.client.get(f"/product/{prod_id}", headers=self.headers, name="/product/[id]")

            # Update - Endpoint: PUT /product/update/{product_id}
            self.client.put(f"/product/update/{prod_id}", json={
                "price": float(random.randint(10, 1000))
            }, headers=self.headers, name="/product/update/[id]")

            # Get All - Endpoint: GET /product/all
            self.client.get("/product/all", headers=self.headers)

    # -------------------------
    # 🛒 CART & WISHLIST
    # -------------------------
    @task(5)
    def cart_operations(self):
        if not self.token or not self.product_ids: return
        prod_id = random.choice(self.product_ids)

        # Bulk Add - Endpoint: POST /cart/bulk-add
        self.client.post("/cart/bulk-add", json={
            "user_id": self.user_id,
            "product_ids": [prod_id]
        }, headers=self.headers)

        # Get Cart - Endpoint: GET /cart/
        self.client.get("/cart/", headers=self.headers)

        # Update Quantity - Endpoint: PUT /cart/update/{product_id}
        self.client.put(f"/cart/update/{prod_id}?quantity={random.randint(1, 5)}", headers=self.headers, name="/cart/update/[id]")

        # Remove item - Endpoint: DELETE /cart/remove/{product_id}
        if random.random() < 0.3:
            self.client.delete(f"/cart/remove/{prod_id}", headers=self.headers, name="/cart/remove/[id]")

    @task(2)
    def cart_checkout_task(self):
        if not self.token: return
        # Checkout - Endpoint: POST /cart/checkout
        if self.product_ids:
            self.client.post("/cart/bulk-add", json={
                "user_id": self.user_id,
                "product_ids": [random.choice(self.product_ids)]
            }, headers=self.headers)

            self.client.post("/cart/checkout", headers=self.headers)

    @task(3)
    def wishlist_operations(self):
        if not self.token or not self.product_ids: return
        prod_id = random.choice(self.product_ids)

        # Bulk Add - Endpoint: POST /wishlist/bulk-add
        self.client.post("/wishlist/bulk-add", json={
            "user_id": self.user_id,
            "product_ids": [prod_id]
        }, headers=self.headers)

        # Get Wishlist - Endpoint: GET /wishlist/{user_id}
        self.client.get(f"/wishlist/{self.user_id}", headers=self.headers, name="/wishlist/[id]")

        # Remove item - Endpoint: DELETE /wishlist/remove/{user_id}/{product_id}
        if random.random() < 0.2:
            self.client.delete(f"/wishlist/remove/{self.user_id}/{prod_id}", headers=self.headers, name="/wishlist/remove/[user]/[prod]")

        # Move to cart - Endpoint: POST /wishlist/move-to-cart
        self.client.post(f"/wishlist/move-to-cart?user_id={self.user_id}&product_id={prod_id}", headers=self.headers, name="/wishlist/move-to-cart")

        # Clear - Endpoint: DELETE /wishlist/clear/{user_id}
        if random.random() < 0.1:
            self.client.delete(f"/wishlist/clear/{self.user_id}", headers=self.headers, name="/wishlist/clear/[id]")

    # -------------------------
    # 📍 ADDRESS
    # -------------------------
    @task(2)
    def address_lifecycle(self):
        if not self.token: return
        # Add - Endpoint: POST /address/add
        res = self.client.post("/address/add", json={
            "street": f"{random.randint(1, 999)} Maple St",
            "city": "Sample City",
            "state": "Sample State",
            "country": "Sample Country",
            "zipcode": "123456"
        }, headers=self.headers)

        if res.status_code == 201:
            self.address_indices.append(len(self.address_indices))
            idx = self.address_indices[-1]

            # Get All - Endpoint: GET /address/all
            self.client.get("/address/all", headers=self.headers)

            # Update - Endpoint: PUT /address/update/{index}
            self.client.put(f"/address/update/{idx}", json={
                "street": f"{random.randint(1, 999)} Updated St",
                "city": "Updated City",
                "state": "Updated State",
                "country": "Updated Country",
                "zipcode": "654321"
            }, headers=self.headers, name="/address/update/[idx]")

    # -------------------------
    # 📝 REVIEWS
    # -------------------------
    @task(2)
    def review_lifecycle(self):
        if not self.token or not self.product_ids: return
        prod_id = random.choice(self.product_ids)

        # Create - Endpoint: POST /review/create
        res = self.client.post("/review/create", json={
            "user_id": self.user_id,
            "product_id": prod_id,
            "rating": float(random.randint(1, 5)),
            "comment": "Great product!",
            "order_item": {"product_id": prod_id},
            "verified_purchase": True
        }, headers=self.headers)

        if res.status_code == 201:
            rev_id = res.json()["data"]["_id"]
            self.review_ids.append(rev_id)

            # Get product reviews - Endpoint: GET /review/product/{product_id}
            self.client.get(f"/review/product/{prod_id}", headers=self.headers, name="/review/product/[id]")

    # -------------------------
    # 💳 ORDER & PAYMENT & RETURN
    # -------------------------
    @task(2)
    def order_flow(self):
        if not self.token or not self.product_ids: return

        prod_id = random.choice(self.product_ids)

        # Create Order - Endpoint: POST /order/create
        res = self.client.post("/order/create", json={
            "user_id": self.user_id,
            "address": {
                "street": "123 Order St",
                "city": "Order City",
                "zipcode": "111222"
            }
        }, headers=self.headers)

        if res.status_code == 201:
            order_id = res.json()["data"]["_id"]
            self.order_ids.append(order_id)

            # Get Order - Endpoint: GET /order/{order_id}
            self.client.get(f"/order/{order_id}", headers=self.headers, name="/order/[id]")

            # Create Payment - Endpoint: POST /payment/create
            pay_res = self.client.post("/payment/create", json={
                "order_id": order_id,
                "amount_paid": 500.0,
                "payment_method": "UPI",
                "transaction_id": f"TXN_{random_string(10)}"
            }, headers=self.headers)

            if pay_res.status_code == 201:
                pay_id = pay_res.json()["data"]["_id"]
                self.payment_ids.append(pay_id)
                # Get Payment - Endpoint: GET /payment/{payment_id}
                self.client.get(f"/payment/{pay_id}", headers=self.headers, name="/payment/[id]")

                # Update Order Status - Endpoint: PATCH /order/status/{order_id}
                self.client.patch(f"/order/status/{order_id}", json={"status": "DELIVERED"}, headers=self.headers, name="/order/status/[id]")

                # Create Return - Endpoint: POST /return/create
                ret_res = self.client.post("/return/create", json={
                    "order_id": order_id,
                    "user_id": self.user_id,
                    "order_item": {"product_id": prod_id},
                    "return_quantity": 1,
                    "return_reason": "Not as expected"
                }, headers=self.headers)

                if ret_res.status_code == 201:
                    ret_id = ret_res.json()["data"]["_id"]
                    self.return_ids.append(ret_id)

                    # Update Return Status - Endpoint: PATCH /return/status/{return_id}
                    self.client.patch(f"/return/status/{ret_id}", json={"status": "APPROVED"}, headers=self.headers, name="/return/status/[id]")

    # -------------------------
    # 🗑 CLEANUP (DELETES)
    # -------------------------
    @task(1)
    def cleanup_resources(self):
        """
        Carefully delete resources created during the session
        """
        if not self.token: return

        # Delete Review - Endpoint: DELETE /review/delete/{review_id}
        if self.review_ids:
            rev_id = self.review_ids.pop()
            self.client.delete(f"/review/delete/{rev_id}", headers=self.headers, name="/review/delete/[id]")

        # Delete Address - Endpoint: DELETE /address/delete/{index}
        if self.address_indices:
            idx = self.address_indices.pop()
            self.client.delete(f"/address/delete/{idx}", headers=self.headers, name="/address/delete/[idx]")

        # Delete Product - Endpoint: DELETE /product/delete/{product_id}
        if self.product_ids:
            prod_id = self.product_ids.pop()
            self.client.delete(f"/product/delete/{prod_id}", headers=self.headers, name="/product/delete/[id]")

        # Delete Subcategory - Endpoint: DELETE /subcategory/delete/{subcategory_id}
        if self.subcategory_ids:
            subcat_id = self.subcategory_ids.pop()
            self.client.delete(f"/subcategory/delete/{subcat_id}", headers=self.headers, name="/subcategory/delete/[id]")

        # Delete Category - Endpoint: DELETE /category/delete/{category_id}
        if self.category_ids:
            cat_id = self.category_ids.pop()
            self.client.delete(f"/category/delete/{cat_id}", headers=self.headers, name="/category/delete/[id]")
