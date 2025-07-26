import httpx
from fastapi import HTTPException
from app.core.config import settings
from typing import Dict

async def get_okta_headers(access_token: str, host_name: str) -> Dict[str, str]:
    url = f"{settings.AUTHORIZE_URL_BASE}/api/v2.0/authorize"
    headers = {
        "access_token": access_token,
        "hostName": host_name
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, timeout=15)
        if resp.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid access_token")
        if resp.status_code == 403:
            raise HTTPException(status_code=403, detail="Forbidden: Access denied")
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Auth service error")
        data = resp.json()
        # Only return minimal required headers
        required = ["x-forwarded-user", "tenantIdentifier", "hostName"]
        missing = [k for k in required if k not in data]
        if missing:
            raise HTTPException(status_code=500, detail=f"Missing headers in auth response: {missing}")
        return {
            "x-forwarded-user": data["x-forwarded-user"],
            "tenantIdentifier": data["tenantIdentifier"],
            "hostName": data["hostName"],
            "Authorization": f"Bearer {access_token}"
        }
