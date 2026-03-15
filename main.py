from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# ----------------------------
# Product list
# ----------------------------

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 99, "category": "Stationery", "in_stock": False},
    {"id": 4, "name": "USB Cable", "price": 199, "category": "Electronics", "in_stock": True},
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
]


# ----------------------------
# Pydantic Model
# ----------------------------

class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: Optional[bool] = True


# ----------------------------
# Helper function
# ----------------------------

def find_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return None


# ----------------------------
# Q1 - Get all products
# ----------------------------

@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


# ----------------------------
# Q2 - Get by category
# ----------------------------

@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):

    result = [p for p in products if p["category"] == category_name]

    if not result:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": result,
        "total": len(result)
    }


# ----------------------------
# Q3 - Get in-stock products
# ----------------------------

@app.get("/products/instock")
def get_instock():

    available = [p for p in products if p["in_stock"]]

    return {
        "in_stock_products": available,
        "count": len(available)
    }


# ----------------------------
# Q4 - Store summary
# ----------------------------

@app.get("/store/summary")
def store_summary():

    in_stock_count = len([p for p in products if p["in_stock"]])
    out_stock_count = len(products) - in_stock_count

    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": categories
    }


# ----------------------------
# Q5 - Search product
# ----------------------------

@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not results:
        return {"message": "No products matched your search"}

    return {
        "keyword": keyword,
        "results": results,
        "total_matches": len(results)
    }


# ----------------------------
# BONUS - Deals
# ----------------------------

@app.get("/products/deals")
def get_deals():

    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }


# ----------------------------
# Filter products
# ----------------------------

@app.get("/products/filter")
def filter_products(
    min_price: int = Query(None),
    max_price: int = Query(None),
    category: str = Query(None)
):

    result = products

    if category:
        result = [p for p in result if p["category"] == category]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    return result


# ----------------------------
# POST - Add product
# ----------------------------

@app.post("/products")
def add_product(data: NewProduct, response: Response):

    for p in products:
        if p["name"].lower() == data.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Product already exists"}

    next_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": next_id,
        "name": data.name,
        "price": data.price,
        "category": data.category,
        "in_stock": data.in_stock
    }

    products.append(new_product)

    response.status_code = status.HTTP_201_CREATED

    return {"message": "Product added", "product": new_product}


# ----------------------------
# PUT - Update product
# ----------------------------

@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    price: Optional[int] = None,
    in_stock: Optional[bool] = None,
    response: Response = None
):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return {"message": "Product updated", "product": product}


# ----------------------------
# DELETE product
# ----------------------------

@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)

    return {"message": f"Product '{product['name']}' deleted"}


# ----------------------------
# Audit endpoint
# ----------------------------

@app.get("/products/audit")
def product_audit():

    in_stock_list = [p for p in products if p["in_stock"]]
    out_stock_list = [p for p in products if not p["in_stock"]]

    stock_value = sum(p["price"] * 10 for p in in_stock_list)

    priciest = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": stock_value,
        "most_expensive": {
            "name": priciest["name"],
            "price": priciest["price"]
        }
    }
from fastapi import HTTPException

cart = []
orders = []


def find_product(product_id):
    for p in products:
        if p["id"] == product_id:
            return p
    return None


@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    product = find_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * product["price"]
            return {"message": "Cart updated", "cart_item": item}

    new_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": quantity * product["price"]
    }

    cart.append(new_item)

    return {"message": "Added to cart", "cart_item": new_item}


@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": total
    }


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "Item removed"}

    raise HTTPException(status_code=404, detail="Item not in cart")


@app.post("/cart/checkout")
def checkout(customer_name: str, delivery_address: str):

    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0

    for item in cart:
        order = {
            "customer_name": customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        }
        orders.append(order)
        total += item["subtotal"]

    cart.clear()

    return {
        "message": "Order placed",
        "orders_placed": orders,
        "grand_total": total
    }


@app.get("/orders")
def get_orders():
    return {"orders": orders, "total_orders": len(orders)}