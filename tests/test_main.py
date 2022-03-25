from types import SimpleNamespace

from fastapi.testclient import TestClient

from src.main import app

# from unittest.mock import patch
# from pytest import raises
# import os

# from src.main import stores


client = TestClient(app)


# To runt pytest: docker-compose exec web pytest . -v
# -v (verbose, to get more info)


def test_stores():
    response = client.get("/stores")
    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "name": "Djurjouren",
                "address": "Upplandsgatan 99, 12345 Stockholm"
            },
            {
                "name": "Djuristen",
                "address": "Skånegatan 420, 54321 Falun"
            },
            {
                "name": "Den Lilla Djurbutiken",
                "address": "Nätverksgatan 22, 55555 Hudiksvall"
            },
            {
                "name": "Den Stora Djurbutiken",
                "address": "Routergatan 443, 54545 Hudiksvall"
            },
            {
                "name": "Noahs Djur & Båtaffär",
                "address": "Stallmansgatan 666, 96427 Gävle"
            }
        ]
    }


def test_store_address():
    response = client.get("/stores/Djuristen")
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "name": "Djuristen",
            "address": "Skånegatan 420, 54321 Falun"
        }
    }


def test_store_address_non_existing():
    response = client.get("/stores/InfernoOnline")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "No stores was found"
    }


def test_city_name():
    response = client.get("/city")
    assert response.status_code == 200
    assert response.json() == {
        "data": [
            "Gävle",
            "Falun",
            "Stockholm",
            "Hudiksvall"
        ]
    }


def test_get_one_city():
    response = client.get("/city?zip=12345")
    assert response.status_code == 200
    assert response.json() == {
        "data": [
            "Stockholm"
        ]
    }


def test_city_name_non_existing():
    response = client.get("/city?zip=5555555")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "No city was found"
    }


def test_sales():
    response = client.get("/sales")
    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "store": "Den Stora Djurbutiken",
                "timestamp": "20220125T13:52:34",
                "sale_id": "0188146f-5360-408b-a7c5-3414077ceb59"
            },
            {
                "store": "Djuristen",
                "timestamp": "20220126T15:24:45",
                "sale_id": "726ac398-209d-49df-ab6a-682b7af8abfb"
            },
            {
                "store": "Den Lilla Djurbutiken",
                "timestamp": "20220207T09:00:56",
                "sale_id": "602fbf9d-2b4a-4de2-b108-3be3afa372ae"
            },
            {
                "store": "Den Stora Djurbutiken",
                "timestamp": "20220227T12:32:46",
                "sale_id": "51071ca1-0179-4e67-8258-89e34b205a1e"
            }
        ]
    }


def test_specific_sale():
    response = client.get("/sales/0188146f-5360-408b-a7c5-3414077ceb59")
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "store": "Den Stora Djurbutiken",
            "timestamp": "20220125T13:52:34",
            "sale_id": "0188146f-5360-408b-a7c5-3414077ceb59",
            "products": [
                {
                    "name": "Hundmat",
                    "qty": 3
                },
                {
                    "name": "Sömnpiller och energidryck för djur",
                    "qty": 12
                }
            ]
        }
    }


def test_specific_sale_not_valid_entry():
    response = client.get("/sales/d546dfs6d54sdf65s4df6s5d4f654e")
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Invalid entry"
    }


def test_specific_sale_not_exist():
    response = client.get("/sales/0188146f-5360-408b-a7c5-3414077ceb80")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "ID does not exist"
    }


def test_get_income():
    response = client.get(
        "/income?store=676df1a1-f1d1-4ac5-9ee3-c58dfe820927&product=6c944a17-7606-42f4-a045-df459f6a8c6e&from=2022-01-25 13:52:34&to=2022-01-25 13:52:34")
    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "store_name": "Den Stora Djurbutiken",
                "product_name": "Sömnpiller och energidryck för djur",
                "price": 9.95,
                "quantity": 12,
                "sale_time": "20220125T13:52:34",
                "discount": 9
            }
        ]
    }


def test_get_income_invalid_uuid_store():
    response = client.get(
        "/income?store=14535416845413541645321&product=6c944a17-7606-42f4-a045-df459f6a8c6e&from=2022-01-25 13:52:34&to=2022-01-25 13:52:34")
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Invalid UUID given for store!"
    }


def test_get_income_invalid_uuid_product():
    response = client.get(
        "/income?store=676df1a1-f1d1-4ac5-9ee3-c58dfe820927&product=14535416845413541645321&from=2022-01-25 13:52:34&to=2022-01-25 13:52:34")
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Invalid UUID given for product!"
    }


def test_get_income_invalid_datetime_format():
    response = client.get(
        "/income?store=676df1a1-f1d1-4ac5-9ee3-c58dfe820927&product=6c944a17-7606-42f4-a045-df459f6a8c6e&from=1648216813&to=1912-08-23T11:59:34")
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Invalid datetime format!"
    }
