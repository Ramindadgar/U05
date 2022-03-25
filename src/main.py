from collections import namedtuple

from fastapi import FastAPI, HTTPException, Query, status

from typing import List, Optional


import psycopg2
import psycopg2.extras

import uuid
# from src import api

"""
Welcome to breaking bad endpoints.
When testing these endpoints we have two different databases.

One in a docker-compose container and one public "physical" database.

If you are going to run tests with pytest against the docker-compose databse you'll have to do this:

1. in tests ==> test_main.py change the import "from src.main import app" to "from ..src.main import app"
2. In src/main.py comment the public db connection and make sure the local db conneciton is uncomment.
3. start docker-compose up -d ==> docker-compose exec web pytest . -v

When running tests against the public database
1. comment away the local databse-connection below and
2. In tests ==> test_main.py make sure the app-import looks like this: "from src.main import app"
"""


app = FastAPI()

conn = psycopg2.connect(
    "postgresql://postgres:DjExUSMcwWpzXziT@doe21-db.grinton.dev:5432/u05")

# conn = psycopg2.connect("postgresql://test-breakingbad:testpass@db:5432/bbdb")


@app.on_event("shutdown")
def shutdown():
    conn.close()  # pragma: no cover


@app.get("/")
def root():
    return("WELCOME TO BREAKING BAD")  # pragma: no cover


@app.get("/stores")
async def stores():
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT name, store_addresses.address, store_addresses.zip, store_addresses.city FROM stores JOIN store_addresses on store = stores.id")
        stores = cur.fetchall()
        stores = [{"name": s["name"],
                   "address": f"{s['address']}, {s['zip']} {s['city']}"} for s in stores]

        return {"data": stores}


@app.get("/stores/{name}")
async def read_item(name: str):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT stores.name, store_addresses.address, store_addresses.zip, store_addresses.city FROM stores JOIN store_addresses on store = stores.id WHERE name=(%s)", (name,))
        data = cur.fetchone()

        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No stores was found")
        else:
            data = {
                "name": data["name"], "address": f"{data['address']}, {data['zip']} {data['city']}"}

        return {"data": data}


@app.get("/city")
async def get_city(zip=None):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        if zip:
            cur.execute(
                "SELECT city FROM store_addresses WHERE zip = (%s);", (zip,))
        else:
            cur.execute("SELECT DISTINCT city FROM store_addresses;")
        data = cur.fetchall()

        if len(data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No city was found")

        data = [d["city"] for d in data]
        return {"data": data}


@app.get("/sales")
async def sales():
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT name, to_char(sales.time, 'YYYYMMDDThh24:MI:SS') as time, sales.id FROM stores JOIN sales on store = stores.id")
        sales = cur.fetchall()
        sales = [{"store": s["name"], "timestamp": s['time'],
                  "sale_id": s['id']} for s in sales]

        return {"data": sales}

# github actions
# Kolla med aws om cert libgen (https://libgen.is)


@app.get("/sales/{sale_id}")
async def get_sale(sale_id: str):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:

        valid_uuid = is_valid_uuid(sale_id)
        if valid_uuid is False:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid entry")

        cur.execute("SELECT id FROM sales")
        id = cur.fetchall()
        sale_UUID = [item for t in id for item in t]
        if sale_id in sale_UUID:
            # query = """SELECT stores.name, to_char(sales.time::date, 'yyyymmddThh:mm:ss'), sales.id FROM sales JOIN stores on stores.id = sales.store WHERE sales.id = {sale_id};"""
            cur.execute(
                "SELECT stores.name, to_char(sales.time, 'YYYYMMDDThh24:MI:SS') as time, sales.id FROM sales JOIN stores on stores.id = sales.store WHERE sales.id = (%s)", (sale_id,))
            sales = cur.fetchone()
            cur.execute("SELECT sold_products.quantity, products.name FROM sold_products JOIN products ON products.id = sold_products.product WHERE sold_products.sale = (%s)", (sale_id,))
            product = cur.fetchall()
            p = [{"name": p['name'], "qty": p['quantity']} for p in product]
            result = {"store": sales["name"], "timestamp": sales['time'],
                      "sale_id": sales['id'], "products": p}
            return {"data": result}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="ID does not exist")


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


# QueryResultIncome is a named tuple used to ease the parsing of
# list-of-lists data format returned by cursor.fetchall into dictionaries
# ready to be returned as JSON.
QueryResultIncome = namedtuple("QueryResultIncome",
                               ("store_name", "product_name", "price",
                                "quantity", "sale_time", "discount"))


@app.get("/income")
def get_income(store: Optional[List[str]] = Query(None),
               product: Optional[List[str]] = Query(None),
               from_=Query(None, alias="from"), to_=Query(None, alias="to")):
    """GET /income

    Returns data in the usual format {"data": ·list-of-dicts}. Each
    dictionary contains all info about a transaction, including price and
    discount percent.

    It accepts the following query parameters:
        - store: (can be given more than once) UUID to filter results by store
        - product: (can be given more than once) UUID to filter results by
          product
        - from: filter out all transactions before the given datestamp/timestamp
        - to: filter out all transactions after the given datestamp/timestamp

    If any invalid UUID is given (either in store or product), 422 -
    Unprocessable Entity will be returned
    """
    stores_clause, products_clause, from_clause, to_clause = "", "", "", ""
    parameters = []
    if store:
        try:
            for iterator in store:
                uuid.UUID(iterator)
        except ValueError as err:
            raise HTTPException(status_code=422,
                                detail="Invalid UUID given for store!") from err
        stores_clause = "WHERE stores.id::text = ANY(%s)"
        parameters.append(store)
    if product:
        try:
            for iterator in product:
                uuid.UUID(iterator)
        except ValueError as err:
            raise HTTPException(
                status_code=422,
                detail="Invalid UUID given for product!") from err
        products_clause = "WHERE products.id::text = ANY(%s)"
        if parameters:
            products_clause = products_clause.replace("WHERE", "AND")
        parameters.append(product)
    if from_:
        from_clause = "WHERE sales.time >= %s"
        if parameters:
            from_clause = from_clause.replace("WHERE", "AND")
        parameters.append(from_)
    if to_:
        to_clause = "WHERE sales.time <= %s"
        if parameters:
            to_clause = to_clause.replace("WHERE", "AND")
        parameters.append(to_)
    query = """SELECT stores.name, products.name, prices.price,
               sold_products.quantity, to_char(sales.time, 'YYYYMMDDThh24:MI:SS'), discounts.discount_percent
               FROM sold_products
               JOIN products on sold_products.product = products.id
               JOIN sales ON sold_products.sale = sales.id
               JOIN stores ON sales.store = stores.id
               JOIN prices ON products.id = prices.product
               LEFT JOIN discounts ON products.id = discounts.product
               {stores} {products} {from_} {to_}
               ORDER BY sales.time;"""
    query = query.format(stores=stores_clause, products=products_clause,
                         from_=from_clause, to_=to_clause)
    try:
        with conn.cursor() as cur:
            cur.execute(query, parameters)
            result = cur.fetchall()
            print("Hej det här kommer från try-blocket efter fetchall")
    except psycopg2.errors.Error:
        print("Hej här är ett meddelande från error")
        conn.rollback()
        raise HTTPException(status_code=422, detail="Invalid datetime format!")
    # except psycopg2.errors.DatetimeFieldOverflow:
    #     print("hej från datetime.field-OVERFLOW!!!!!!!!!!!")
    entries = [QueryResultIncome(*r)._asdict() for r in result]
    print(entries)
    return {"data": entries}


# WHERE stores.id = 'dd4cf820-f946-4f38-8492-ca5dfeed0d74' OR products.id = 'a37c34ae-0895-484a-8b2a-355aea3b6c44' OR sales.time >= '2022-01-25 13:52:34' OR sales.time <= '2022-02-27 12:32:46'
# QueryResultInventory is a named tuple used to ease the parsing of
# list-of-lists data format returned by cursor.fetchall into dictionaries
# ready to be returned as JSON.
QueryResultInventory = namedtuple("QueryResultInventory", ("product_name",
                                                           "adjusted_quantity",
                                                           "store_name"))


@app.get("/inventory")
def get_inventory(store=None, product=None):
    """GET /inventory

    Returns data in the usual format {"data": ·list-of-dicts}. Each
    dictionary contains all info about *current* inventory (inventory -
    sales) showing inventory status per product and store.

    It accepts the following query parameters:
        - store: UUID to filter results by store
        - product: UUID to filter results by product

    If any invalid UUID is given (either in store or product), 422 -
    Unprocessable Entity will be returned

    """
    store_clause, product_clause = "", ""
    parameters = []
    if store:
        try:
            uuid.UUID(store)
        except ValueError as err:
            raise HTTPException(status_code=422,
                                detail="Invalid UUID for store!") from err
        store_clause = "WHERE stores.id = %s"
        parameters.append(store)
    if product:
        try:
            uuid.UUID(product)
        except ValueError as err:
            raise HTTPException(status_code=422,
                                detail="Invalid UUID for product!") from err
        product_clause = "WHERE products.id = %s"
        if parameters:
            product_clause = product_clause.replace("WHERE", "AND")
        parameters.append(product)
    query = """SELECT products.name,
               SUM(inventory.quantity) - SUM(sold_products.quantity),
               stores.name
               FROM inventory
               JOIN products ON products.id = inventory.product
               JOIN stores ON stores.id = inventory.store
               JOIN sold_products ON sold_products.product = products.id
               {store} {product}
               GROUP BY stores.name, products.name;
    """
    query = query.format(store=store_clause, product=product_clause)
    print(store)
    print(product)
    print(query)
    with conn.cursor() as cur:
        cur.execute(query, parameters)
        result = cur.fetchall()
    entries = [QueryResultInventory(*r)._asdict() for r in result]
    return sorted(entries, key=lambda x: (x["store_name"], x["product_name"]))
