from fastapi.testclient import TestClient

from src.main import app

# from unittest.mock import patch
# from pytest import raises
# import os

# from src.main import stores


client = TestClient(app)


#To runt pytest: docker-compose exec web pytest . -v
#-v (verbose, to get more info)


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
    response = client.get("/city/55555555")
    assert response.status_code == 404
    assert response.json() == {
  'detail': 'Not Found'
}


def test_sales():    
    response = client.get("/sales")
    assert response.status_code == 200
    assert response.json() == {
  "data": [
    {
      "store": "Den Stora Djurbutiken",
      "timestamp": "2022-01-25T13:52:34",
      "sale_id": "0188146f-5360-408b-a7c5-3414077ceb59"
    },
    {
      "store": "Djuristen",
      "timestamp": "2022-01-26T15:24:45",
      "sale_id": "726ac398-209d-49df-ab6a-682b7af8abfb"
    },
    {
      "store": "Den Lilla Djurbutiken",
      "timestamp": "2022-02-07T09:00:56",
      "sale_id": "602fbf9d-2b4a-4de2-b108-3be3afa372ae"
    },
    {
      "store": "Den Stora Djurbutiken",
      "timestamp": "2022-02-27T12:32:46",
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
    "timestamp": "2022-01-25T13:52:34",
    "sale_id": "0188146f-5360-408b-a7c5-3414077ceb59",
    "Products": [
      {
        "Name": "Hundmat",
        "Qty": 3
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

# class MockResponse:
#     reason = "Mock reason"

#     def __init__(self, data, status_code):
#         self.data = data
#         self.status_code = status_code

#     def json(self):
#         return self.data  


# def mock_requests_get(*args):
#     if args[0].endswith("1"):
#         return MockResponse([{"data": "store"}], 200)
#     else:
#         return MockResponse([], 200)


# def mock_requests_get_err(*args):
#     return MockResponse(None, 404)


# @patch("response.get", side_effect=mock_requests_get)
# def test_get_stores(mock_get):
#   data = stores()
#   assert data == {
#   "data": [
#     {
#       "name": "Djurjouren",
#       "address": "Upplandsgatan 99, 12345 Stockholm"
#     },
#     {
#       "name": "Djuristen",
#       "address": "Skånegatan 420, 54321 Falun"
#     },
#     {
#       "name": "Den Lilla Djurbutiken",
#       "address": "Nätverksgatan 22, 55555 Hudiksvall"
#     },
#     {
#       "name": "Den Stora Djurbutiken",
#       "address": "Routergatan 443, 54545 Hudiksvall"
#     },
#     {
#       "name": "Noahs Djur & Båtaffär",
#       "address": "Stallmansgatan 666, 96427 Gävle"
#     }
#   ]
# }
