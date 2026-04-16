from locust import HttpUser, task, between
import random


class EcommerceUser(HttpUser):
    wait_time = between(1, 2)

    token = None
    user_id = None

    def on_start(self):
        if not EcommerceUser.token:
            res = self.client.post("/auth/signin", json={
                "identifier": "7904504081",
                "password": "Charan@13"
            })

            if res.status_code != 200:
                print("Login failed:", res.text)
                return

            data = res.json()

            EcommerceUser.token = data["data"]["access_token"]
            EcommerceUser.user_id = data["data"]["user_id"]

        self.token = EcommerceUser.token
        self.user_id = EcommerceUser.user_id

        self.headers = {
            "Authorization": f"Bearer {self.token}"
        }

        self.products = ["PRD000001", "PRD000005"]

    # -------------------------
    # 🛍 PRODUCTS
    # -------------------------
    @task(2)
    def get_products(self):
        self.client.get("/product/all")

    # -------------------------
    # 🛒 CART
    # -------------------------
    @task(3)
    def add_to_cart(self):
        pid = random.choice(self.products)

        self.client.post(
            "/cart/bulk-add",
            json={
                "user_id": self.user_id,
                "product_ids": [pid]
            },
            headers=self.headers
        )

    @task(2)
    def get_cart(self):
        # ✅ FIXED ENDPOINT
        self.client.get(
            "/cart",
            headers=self.headers
        )

    @task(1)
    def remove_from_cart(self):
        pid = random.choice(self.products)

        self.client.delete(
            f"/cart/remove/{pid}",
            headers=self.headers
        )

    # -------------------------
    # ❤️ WISHLIST
    # -------------------------
    @task(3)
    def add_to_wishlist(self):
        pid = random.choice(self.products)

        self.client.post(
            "/wishlist/bulk-add",
            json={
                "user_id": self.user_id,
                "product_ids": [pid]
            },
            headers=self.headers
        )

    @task(2)
    def get_wishlist(self):
        self.client.get(
            f"/wishlist/{self.user_id}",
            headers=self.headers
        )

    @task(1)
    def remove_from_wishlist(self):
        pid = random.choice(self.products)

        self.client.delete(
            f"/wishlist/remove/{self.user_id}/{pid}",
            headers=self.headers
        )

    # -------------------------
    # 🔄 MOVE TO CART
    # -------------------------
    @task(2)
    def move_to_cart(self):
        self.client.post(
            "/wishlist/move-to-cart",
            json={
                "user_id": self.user_id,
                "product_id": "PRD000001"
            },
            headers=self.headers
        )


from locust import HttpUser, task, between
import random


class ProductUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.product_ids = []

    # ✅ CREATE PRODUCT
    @task(2)
    def create_product(self):
        payload = {
            "product_name": f"coffee_{random.randint(1,10000)}",
            "description": "test product",
            "price": random.randint(100, 500),
            "category_id": "001",
            "brand_id": "001"
        }

        res = self.client.post("/product/create", json=payload)

        if res.status_code == 200:
            pid = res.json().get("_id")
            if pid:
                self.product_ids.append(pid)

    # ✅ GET ALL PRODUCTS
    @task(3)
    def get_all_products(self):
        self.client.get("/product/all")

    # ✅ GET SINGLE PRODUCT
    @task(3)
    def get_single_product(self):
        if not self.product_ids:
            return

        pid = random.choice(self.product_ids)

        self.client.get(f"/product/{pid}")

    # ✅ UPDATE PRODUCT
    @task(2)
    def update_product(self):
        if not self.product_ids:
            return

        pid = random.choice(self.product_ids)

        payload = {
            "price": random.randint(200, 600)
        }

        self.client.put(f"/product/update/{pid}", json=payload)

    # ✅ DELETE PRODUCT
    @task(1)
    def delete_product(self):
        if not self.product_ids:
            return

        pid = self.product_ids.pop()

        self.client.delete(f"/product/delete/{pid}")