"""Here are unit tests for the GET /inventory endpoint. You should be able to
run the tests as they are, or with minimal edits once the endpoint is
integrated into your codebase.

The logic in the tests is correct. If a test fails, there is a bug in the
endpoint. So ***you should not*** change the logic in the test, but in the
endpoint to make the tests pass.
"""

from types import SimpleNamespace

from fastapi.testclient import TestClient

from src.main import app

all_inventories = [
    [
        "Hundmat",
        27,
        "Den Lilla Djurbutiken"
    ],
    [
        "Kattmat",
        387,
        "Den Lilla Djurbutiken"
    ],
    [
        "Hundmat",
        140,
        "Den Stora Djurbutiken"
    ],
    [
        "Kattklonare",
        68,
        "Den Stora Djurbutiken"
    ],
    [
        "Kattmat",
        643,
        "Den Stora Djurbutiken"
    ],
    [
        "Sömnpiller och energidryck för djur",
        61,
        "Den Stora Djurbutiken"
    ],
    [
        "Elefantkoppel",
        27,
        "Djuristen"
    ],
]

return_data = [
  {
    "product_name": "Hundmat",
    "adjusted_quantity": 27,
    "store_name": "Den Lilla Djurbutiken"
  },
  {
    "product_name": "Kattmat",
    "adjusted_quantity": 387,
    "store_name": "Den Lilla Djurbutiken"
  },
  {
    "product_name": "Hundmat",
    "adjusted_quantity": 140,
    "store_name": "Den Stora Djurbutiken"
  },
  {
    "product_name": "Kattklonare",
    "adjusted_quantity": 68,
    "store_name": "Den Stora Djurbutiken"
  },
  {
    "product_name": "Kattmat",
    "adjusted_quantity": 643,
    "store_name": "Den Stora Djurbutiken"
  },
  {
    "product_name": "Sömnpiller och energidryck för djur",
    "adjusted_quantity": 61,
    "store_name": "Den Stora Djurbutiken"
  },
  {
    "product_name": "Elefantkoppel",
    "adjusted_quantity": 27,
    "store_name": "Djuristen"
  }
]

def db_mock(data):
    """This function returns a database mocking object, that will be used
    instead of the actual db connection.
    """
    database = SimpleNamespace()
    database.cursor = CursorMock(data)
    return database

class CursorMock:
    """This class mocks a db cursor. It does not build upon unittest.mock but
    it is instead built from an empty class, patching manually all needed
    methods.
    """
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __call__(self):
        return self

    @staticmethod
    def execute(*args):
        """This mocks cursor.execute. It returns args even though the return
        value of cursor.execute() is never used. This is to avoid the
        following linting error:

        W0613: Unused argument 'args' (unused-argument)
        """
        return args

    def fetchall(self):
        """This mocks cursor.fetchall.
        """
        return self.data


def test_get_inventory():
    """This unit test checks a call to GET /inventory without any query
    parameters.
    """
    app.db = db_mock(all_inventories)
    client = TestClient(app)
    response = client.get("/inventory")
    assert response.status_code == 200
    assert response.json() == return_data


def test_get_inventory_store():
    """This unit test checks a call to GET /inventory?store=UUID
    """
    data = list(filter(lambda x: x[-1] == "Den Stora Djurbutiken",
                       all_inventories))
    app.db = db_mock(data)
    client = TestClient(app)
    response = client.get("/inventory",
                          params={
                              "store": "676df1a1-f1d1-4ac5-9ee3-c58dfe820927"})
    assert response.status_code == 200
    assert response.json() == list(filter(
        lambda x: x["store_name"] == "Den Stora Djurbutiken", return_data))

def test_get_inventory_product():
    """This unit test checks a call to GET /inventory?product=UUID
    """
    data = list(filter(lambda x: x[0] == "Hundmat", all_inventories))
    app.db = db_mock(data)
    client = TestClient(app)
    response = client.get("/inventory",
                          params={
                              "product": "a37c34ae-0895-484a-8b2a-355aea3b6c44"
                          })
    assert response.status_code == 200
    assert response.json() == list(filter(
        lambda x: x["product_name"] == "Hundmat", return_data))


def test_get_inventory_store_and_product():
    """This unit test checks a call to GET /inventory?store=UUID&product=UUID
    """
    data = list(filter(
        lambda x: x[0] == "Hundmat" and x[-1] == "Den Stora Djurbutiken",
        all_inventories))
    app.db = db_mock(data)
    client = TestClient(app)
    response = client.get("/inventory", params={
        "product": "a37c34ae-0895-484a-8b2a-355aea3b6c44",
        "store": "676df1a1-f1d1-4ac5-9ee3-c58dfe820927"
    })
    assert response.status_code == 200
    assert response.json() == list(
        filter(
            lambda x: x["store_name"] == "Den Stora Djurbutiken" and
                      x["product_name"] == "Hundmat", return_data))


def test_get_inventory_erroneous_store():
    """This unit test checks for a call to GET /inventory?store=Erroneous-UUID
    """
    app.db = db_mock(None)
    client = TestClient(app)
    response = client.get("/inventory",
                          params={"store": "this is not a valid UUID!"})
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid UUID for store!"}


def test_get_inventory_erroneous_product():
    """This unit test checks for a call to GET /inventory?product=Erroneous-UUID
    """
    app.db = db_mock(None)
    client = TestClient(app)
    response = client.get("/inventory",
                          params={"product": "this is not a valid UUID!"})
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid UUID for product!"}
