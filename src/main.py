from fastapi import FastAPI, HTTPException, status

import psycopg2
import psycopg2.extras

app = FastAPI()


# conn = psycopg2.connect("postgresql://test-breakingbad:testpass@db:5432/bbdb")
conn = psycopg2.connect("postgresql://postgres:DjExUSMcwWpzXziT@doe21-db.grinton.dev:5432/u05")
# conn = psycopg2.connect("postgresql://postgres:testpass@db:5432/bbdb")
# cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


@app.on_event("shutdown")
def shutdown():
    conn.close()


@app.get("/")
def root():
    return("WELCOME TO BRAKING BAD")


# Test codes:
# lt = [('Geeks', 2), ('For', 4), ('geek', '6')]

# # using list comprehension
# out = [item for t in lt for item in t]

# "SELECT name, string_agg(address || '' || zip || '' ||city, '')  FROM stores JOIN store_addresses on store = stores.id group by name"
# Docker image prune

# Imports for schema.py:
# from typing import Optional
# from typing import List
# from . import schema


@app.get("/stores")
async def stores():
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT name, store_addresses.address, store_addresses.zip, store_addresses.city FROM stores JOIN store_addresses on store = stores.id")
        stores = cur.fetchall()
        stores = [{"name": s["name"], "address": f"{s['address']}, {s['zip']} {s['city']}"} for s in stores]

        return {"data": stores}


@app.get("/stores/{name}")
async def read_item(name: str):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT stores.name, store_addresses.address, store_addresses.zip, store_addresses.city FROM stores JOIN store_addresses on store = stores.id WHERE name=(%s)", (name,))
        data = cur.fetchone()

        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No stores was found") #pg_dump -h dev.kjeld.io -U bb -d breakingbad | less > pipe to folder
        else:
            data = {"name": data["name"], "address": f"{data['address']}, {data['zip']} {data['city']}"}

        return {"data": data}


@app.get("/city")
async def get_city(zip=None):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        if zip:
            cur.execute("SELECT city FROM store_addresses WHERE zip = (%s);", (zip,))
        else:
            cur.execute("SELECT DISTINCT city FROM store_addresses;")
        data = cur.fetchall()

        if len(data) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No city was found")

        data = [d["city"] for d in data]
        return {"data": data}


@app.get("/sales")
async def sales():
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT name, sales.time, sales.id FROM stores JOIN sales on store = stores.id")
        sales = cur.fetchall()
        sales = [{"store": s["name"], "timestamp": s['time'], "sale_id": s['id']} for s in sales]

        return {"data": sales}


@app.get("/sales/{sale_id}")
async def sales(sale_id: str):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT stores.name, sales.time, sales.id, sold_products.quantity, products.name FROM sales JOIN stores on stores.id = sales.store WHERE id = (%s) JOIN sold_products on sold_products.sale = sales.id JOIN products on products.id = sold_products.product", (sale_id,))
        sales = cur.fetchall()
        sales = [{"store": s["name"], "timestamp": s['time'], "sale_id": s['id'], "Products": f"{s['name']}, {s['qty']}"} for s in sales]
        # stores = [{"name": s["name"], "address": f"{s['address']}, {s['zip']} {s['city']}"} for s in stores]

        return {"data": sales}
