router = APIRouter()
logger = logging.getLogger("payloadbridge")

@router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
@router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.models.order_line import OrderPayload
from app.services.auth_utils import get_okta_headers
from app.core.config import settings
import httpx
import logging
import uuid
import re
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger("payloadbridge")
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

@router.post("/invoke_order_creation")
async def invoke_order_creation(request: Request):
    request_id = str(uuid.uuid4())
    tenant = None
    try:
        body = await request.json()
        headers = request.headers

        access_token = headers.get("access_token")
        host_name = headers.get("hostName")
        if not access_token:
            logger.error(f"[{request_id}] Missing access_token header")
            return JSONResponse(status_code=400, content={"error": "Missing access_token header", "request_id": request_id})
        if not host_name:
            logger.error(f"[{request_id}] Missing hostName header")
            return JSONResponse(status_code=400, content={"error": "Missing hostName header", "request_id": request_id})
        # Validate hostName format (simple domain check)
        if not re.match(r"^[a-zA-Z0-9.-]+$", host_name):
            logger.error(f"[{request_id}] Invalid hostName format: {host_name}")
            return JSONResponse(status_code=400, content={"error": "Invalid hostName format", "request_id": request_id})

        # Validate payload
        try:
            order = OrderPayload(**body)
        except Exception as e:
            logger.error(f"[{request_id}] Validation error: {e}")
            return JSONResponse(status_code=422, content={"error": "Invalid input", "details": str(e), "request_id": request_id})

        # Get Okta/RecVue headers
        try:
            okta_headers = await get_okta_headers(access_token, host_name)
        except HTTPException as e:
            logger.error(f"[{request_id}] Auth error: {e.detail}")
            return JSONResponse(status_code=e.status_code, content={"error": "Auth error", "details": e.detail, "request_id": request_id})
        except Exception as e:
            logger.error(f"[{request_id}] Auth error: {e}")
            return JSONResponse(status_code=500, content={"error": "Auth error", "details": str(e), "request_id": request_id})

        tenant = okta_headers.get("tenantIdentifier")

        # Forward payload to RecVue
        recvue_url = f"https://{tenant}.recvue.com/api/v2.0/order/orderlines"
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(recvue_url, json=body, headers=okta_headers, timeout=settings.TIMEOUT)
                    log_msg = f"[{request_id}] RecVue response: {resp.status_code}"
                    if tenant:
                        log_msg += f" tenant={tenant}"
                    logger.info(log_msg)
                    try:
                        content = resp.json()
                    except Exception:
                        content = {"error": "RecVue returned non-JSON response", "raw": resp.text}
                    return JSONResponse(status_code=resp.status_code, content={"recvue": content, "request_id": request_id, "tenant": tenant})
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                log_msg = f"[{request_id}] RecVue API attempt {attempt+1} failed: {e}"
                if tenant:
                    log_msg += f" tenant={tenant}"
                logger.warning(log_msg)
                if attempt == max_retries:
                    if isinstance(e, httpx.HTTPStatusError):
                        return JSONResponse(status_code=e.response.status_code, content={"error": "RecVue error", "details": str(e), "request_id": request_id, "tenant": tenant})
                    else:
                        return JSONResponse(status_code=502, content={"error": "RecVue unreachable", "details": str(e), "request_id": request_id, "tenant": tenant})
            except Exception as e:
                log_msg = f"[{request_id}] Downstream error: {e}"
                if tenant:
                    log_msg += f" tenant={tenant}"
                logger.error(log_msg)
                if attempt == max_retries:
                    return JSONResponse(status_code=500, content={"error": "Failed to reach RecVue API", "details": str(e), "request_id": request_id, "tenant": tenant})
    except Exception as e:
        logger.critical(f"[{request_id}] Unhandled error: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal server error", "details": str(e), "request_id": request_id})