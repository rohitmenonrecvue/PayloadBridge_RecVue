from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_invoke_order_creation_valid_payload():
    response = client.post("/invoke_order_creation", json={
        "order_id": "12345",
        "customer_id": "67890",
        "items": [
            {
                "item_id": "item1",
                "quantity": 2
            },
            {
                "item_id": "item2",
                "quantity": 1
            }
        ]
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Order creation invoked successfully."}

def test_invoke_order_creation_missing_fields():
    response = client.post("/invoke_order_creation", json={
        "order_id": "12345"
    })
    assert response.status_code == 422  # Unprocessable Entity
    assert "detail" in response.json()

def test_invoke_order_creation_authentication_error():
    response = client.post("/invoke_order_creation", json={
        "order_id": "12345",
        "customer_id": "67890",
        "items": [
            {
                "item_id": "item1",
                "quantity": 2
            }
        ]
    }, headers={"Authorization": "InvalidToken"})
    assert response.status_code == 401  # Unauthorized
    assert "detail" in response.json()