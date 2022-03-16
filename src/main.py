from fastapi import FastAPI, HTTPException, status

import uuid

import psycopg2
import psycopg2.extras

app = FastAPI()

conn = psycopg2.connect("postgresql://postgres:DjExUSMcwWpzXziT@doe21-db.grinton.dev:5432/u05")

# conn = psycopg2.connect("postgresql://test-breakingbad:testpass@db:5432/bbdb")
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
# pg_dump -h dev.kjeld.io -U bb -d breakingbad | less > pipe to folder
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No stores was found")
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
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:

        valid_uuid = is_valid_uuid(sale_id)
        if valid_uuid == False:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid entry")

        cur.execute("SELECT id FROM sales")
        id = cur.fetchall()
        sale_UUID = [item for t in id for item in t]
        if sale_id in sale_UUID:
            cur.execute("SELECT stores.name, sales.time, sales.id FROM sales JOIN stores on stores.id = sales.store WHERE sales.id = (%s)", (sale_id,))
            sales = cur.fetchone()
            cur.execute("SELECT sold_products.quantity, products.name FROM sold_products JOIN products ON products.id = sold_products.product WHERE sold_products.sale = (%s)", (sale_id,))
            product = cur.fetchone()
            p = {"Name": product['name'], "Qty": product['quantity']}
            result = {"store": sales["name"], "timestamp": sales['time'], "sale_id": sales['id'], "Products": [p]} 
            return {"data": result}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID does not exist")


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False