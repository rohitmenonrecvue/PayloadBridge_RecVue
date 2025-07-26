from typing import Any, Dict
import httpx
from app.core.config import settings

async def get_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.RECVUE_API_TOKEN}",
        "Content-Type": "application/json"
    }

async def forward_payload(payload: Dict[str, Any]) -> Any:
    url = f"{settings.RECVUE_API_BASE_URL}/invoke_order_creation"
    headers = await get_headers()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()