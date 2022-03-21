import uuid

from fastapi import FastAPI, HTTPException, status

import psycopg2
import psycopg2.extras


"""
Welcome to breaking bad endpoints.
When testing these endpoints we have two different databases.

One in a docker-compose container and one public "physical" database.

If you are going to run tests with pytest against the docker-compose databse yo'll have to do this:

1. in tests ==> test_main.py change the import "from src.main import app" to "from ..src.main import app"
2. In src/main.py comment the public db connection and make sure the local db conneciton is uncomment.
3. start docker-compose up -d ==> docker-compose exec web pytest . -v

When running tests against the public database 
1. comment away the local databse-connection below and
2. In tests ==> test_main.py make sure the app-import looks like this: "from src.main import app"
"""


app = FastAPI()

conn = psycopg2.connect("postgresql://postgres:DjExUSMcwWpzXziT@doe21-db.grinton.dev:5432/u05")

# conn = psycopg2.connect("postgresql://test-breakingbad:testpass@db:5432/bbdb")


@app.on_event("shutdown")
def shutdown():
    conn.close()


@app.get("/")
def root():
    return("WELCOME TO BRAKING BAD")


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
async def get_sale(sale_id: str):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:

        valid_uuid = is_valid_uuid(sale_id)
        if valid_uuid is False:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid entry")

        cur.execute("SELECT id FROM sales")
        id = cur.fetchall()
        sale_UUID = [item for t in id for item in t]
        if sale_id in sale_UUID:
            cur.execute("SELECT stores.name, sales.time, sales.id FROM sales JOIN stores on stores.id = sales.store WHERE sales.id = (%s)", (sale_id,))
            sales = cur.fetchone()
            cur.execute("SELECT sold_products.quantity, products.name FROM sold_products JOIN products ON products.id = sold_products.product WHERE sold_products.sale = (%s)", (sale_id,))
            product = cur.fetchone()
            p = {"name": product['name'], "qty": product['quantity']}
            result = {"store": sales["name"], "timestamp": sales['time'], "sale_id": sales['id'], "products": [p]}
            return {"data": result}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID does not exist")


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
