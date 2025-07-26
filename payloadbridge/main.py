from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from payloadbridge.models.order_line import OrderPayload
from payloadbridge.services.auth_utils import get_okta_headers
from payloadbridge.core.config import REC_VUE_BASE_URL
import httpx
import logging

app = FastAPI()
logger = logging.getLogger("payloadbridge")
logging.basicConfig(level=logging.INFO)

@app.post("/invoke_order_creation")
async def invoke_order_creation(request: Request):
    try:
        body = await request.json()
        headers = request.headers
        access_token = headers.get("access_token")
        host_name = headers.get("hostName")
        if not access_token or not host_name:
            logger.error("Missing access_token or hostName header")
            raise HTTPException(status_code=400, detail="Missing access_token or hostName header")

        # Validate payload
        try:
            order = OrderPayload(**body)
        except Exception as e:
            logger.error(f"Validation error: {e}")
            raise HTTPException(status_code=422, detail=str(e))

        # Get Okta/RecVue headers
        try:
            okta_headers = await get_okta_headers(access_token, host_name)
        except HTTPException as e:
            logger.error(f"Auth error: {e.detail}")
            raise

        # Forward payload to RecVue
        tenant = okta_headers["tenantIdentifier"]
        recvue_url = f"https://{tenant}.recvue.com/api/v2.0/order/orderlines"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(recvue_url, json=body, headers=okta_headers, timeout=30)
                logger.info(f"RecVue response: {resp.status_code}")
            except Exception as e:
                logger.error(f"Downstream error: {e}")
                raise HTTPException(status_code=500, detail="Failed to reach RecVue API")

        return JSONResponse(status_code=resp.status_code, content=resp.json())
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
