from fastapi import FastAPI, HTTPException, status
import psycopg2
import psycopg2.extras
from pyparsing import empty

app = FastAPI()


conn = psycopg2.connect("postgresql://test-breakingbad:testpass@db:5432/bbdb")
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No stores was found") # pg_dump -h dev.kjeld.io -U bb -d breakingbad | less > pipe to folder
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
