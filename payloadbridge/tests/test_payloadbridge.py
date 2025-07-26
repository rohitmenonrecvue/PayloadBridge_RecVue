import uuid
import httpx
from app.main import app
import pytest
from fastapi.testclient import TestClient
import respx
from httpx import Response

client = TestClient(app)

def test_missing_headers():
    response = client.post("/invoke_order_creation", json={})
    assert response.status_code == 400
    assert "access_token" in response.text

def test_evergreen_end_date_conflict():
    payload = {
        "orderNumber": "ORD-2024-001",
        "orderType": "Standard Order",
        "orderCategory": "New",
        "businessUnit": "US1 Business Unit",
        "hdrEffectiveStartDate": "2024-01-01",
        "hdrEvergreenFlag": "Y",
        "hdrEffectiveEndDate": "2024-12-31",
        "hdrBillToCustAccountNum": "CUST-12345",
        "orderLines": [
            {
                "lineNumber": "1",
                "lineType": "Recurring",
                "lineEffectiveStartDate": "2024-01-01",
                "lineEvergreenFlag": "Y",
                "lineEffectiveEndDate": "2024-12-31"
            }
        ]
    }
    headers = {"access_token": "dummy", "hostName": "dummyhost"}
    response = client.post("/invoke_order_creation", json=payload, headers=headers)
    assert response.status_code == 422
    assert "lineEffectiveEndDate should not be set if lineEvergreenFlag is Y" in response.text

@respx.mock
def test_recvue_500():
    payload = {
        "orderNumber": "ORD-2024-001",
        "orderType": "Standard Order",
        "orderCategory": "New",
        "businessUnit": "US1 Business Unit",
        "hdrEffectiveStartDate": "2024-01-01",
        "hdrEffectiveEndDate": "2024-12-31",
        "hdrBillToCustAccountNum": "CUST-12345",
        "orderLines": [
            {
                "lineNumber": "1",
                "lineType": "Recurring",
                "lineEffectiveStartDate": "2024-01-01",
                "lineEffectiveEndDate": "2024-12-31"
            }
        ]
    }
    headers = {"access_token": "dummy", "hostName": "dummyhost"}
    respx.get("https://dummyhost/api/v2.0/authorize").respond(200, json={"x-forwarded-user": "user", "tenantIdentifier": "tenant", "hostName": "dummyhost"})
    respx.post("https://tenant.recvue.com/api/v2.0/order/orderlines").respond(500, json={"error": "Internal Server Error"})
    response = client.post("/invoke_order_creation", json=payload, headers=headers)
    assert response.status_code == 500 or response.status_code == 502

@respx.mock
def test_recvue_timeout():
    payload = {
        "orderNumber": "ORD-2024-001",
        "orderType": "Standard Order",
        "orderCategory": "New",
        "businessUnit": "US1 Business Unit",
        "hdrEffectiveStartDate": "2024-01-01",
        "hdrEffectiveEndDate": "2024-12-31",
        "hdrBillToCustAccountNum": "CUST-12345",
        "orderLines": [
            {
                "lineNumber": "1",
                "lineType": "Recurring",
                "lineEffectiveStartDate": "2024-01-01",
                "lineEffectiveEndDate": "2024-12-31"
            }
        ]
    }
    headers = {"access_token": "dummy", "hostName": "dummyhost"}
    respx.get("https://dummyhost/api/v2.0/authorize").respond(200, json={"x-forwarded-user": "user", "tenantIdentifier": "tenant", "hostName": "dummyhost"})
    respx.post("https://tenant.recvue.com/api/v2.0/order/orderlines").mock(side_effect=httpx.TimeoutException("Timeout"))
    response = client.post("/invoke_order_creation", json=payload, headers=headers)
    assert response.status_code == 502

@respx.mock
def test_recvue_malformed_response():
    payload = {
        "orderNumber": "ORD-2024-001",
        "orderType": "Standard Order",
        "orderCategory": "New",
        "businessUnit": "US1 Business Unit",
        "hdrEffectiveStartDate": "2024-01-01",
        "hdrEffectiveEndDate": "2024-12-31",
        "hdrBillToCustAccountNum": "CUST-12345",
        "orderLines": [
            {
                "lineNumber": "1",
                "lineType": "Recurring",
                "lineEffectiveStartDate": "2024-01-01",
                "lineEffectiveEndDate": "2024-12-31"
            }
        ]
    }
    headers = {"access_token": "dummy", "hostName": "dummyhost"}
    respx.get("https://dummyhost/api/v2.0/authorize").respond(200, json={"x-forwarded-user": "user", "tenantIdentifier": "tenant", "hostName": "dummyhost"})
    respx.post("https://tenant.recvue.com/api/v2.0/order/orderlines").respond(200, text="<html>not json</html>")
    response = client.post("/invoke_order_creation", json=payload, headers=headers)
    assert response.status_code == 200
    assert "RecVue returned non-JSON response" in response.text
import pytest
from fastapi.testclient import TestClient
from payloadbridge.main import app
import respx
from httpx import Response

client = TestClient(app)

@pytest.fixture
def valid_headers():
    return {
        "access_token": "dummy_token",
        "hostName": "dummyhost.recvue.com"
    }

@pytest.fixture
def valid_payload():
    return {
        "orderNumber": "ORD-2024-001",
        "orderType": "Standard Order",
        "orderCategory": "New",
        "businessUnit": "US1 Business Unit",
        "hdrEffectiveStartDate": "2024-01-01",
        "hdrEffectiveEndDate": "2024-12-31",
        "hdrBillToCustAccountNum": "CUST-12345",
        "hdrEvergreenFlag": "N",
        "orderLines": [
            {
                "lineNumber": "1",
                "lineType": "Recurring",
                "lineEffectiveStartDate": "2024-01-01",
                "lineEffectiveEndDate": "2024-12-31"
            }
        ]
    }

@respx.mock
def test_valid_payload(valid_headers, valid_payload):
    respx.get("https://dummyhost.recvue.com/api/v2.0/authorize").respond(
        200, json={
            "x-forwarded-user": "user1",
            "tenantIdentifier": "tenant1",
            "hostName": "dummyhost.recvue.com"
        }
    )
    respx.post("https://tenant1.recvue.com/api/v2.0/order/orderlines").respond(
        200, json={"statusCode": "SUCCESS", "message": "Order created successfully", "id": "12345"}
    )
    response = client.post("/invoke_order_creation", json=valid_payload, headers=valid_headers)
    assert response.status_code == 200
    assert response.json()["statusCode"] == "SUCCESS"

@respx.mock
def test_missing_field(valid_headers, valid_payload):
    del valid_payload["orderType"]
    response = client.post("/invoke_order_creation", json=valid_payload, headers=valid_headers)
    assert response.status_code == 422
    assert "Order type is required" in response.text

@respx.mock
def test_bad_auth(valid_headers, valid_payload):
    respx.get("https://dummyhost.recvue.com/api/v2.0/authorize").respond(401)
    response = client.post("/invoke_order_creation", json=valid_payload, headers=valid_headers)
    assert response.status_code == 401
