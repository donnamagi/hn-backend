from fastapi import APIRouter, Response, Request, HTTPException
from fastapi.responses import PlainTextResponse
from app.handlers.webhooks import WebhookHandler
from pydantic import BaseModel
from typing import List, Dict, Any

import os
import logging

router = APIRouter(prefix="/webhook", tags=["webhook"])

WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")
GRAPH_API_TOKEN = os.getenv("WHATSAPP_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebhookPayload(BaseModel):
    object: str
    entry: List[Dict[str, Any]]


@router.post("")
async def webhook(payload: WebhookPayload):
    logger.info(f"Incoming webhook message: {payload.model_dump()}")

    handler = WebhookHandler()
    await handler.handle(payload)

    return Response(status_code=200)


@router.get("")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        logger.info("Webhook verified successfully!")
        return PlainTextResponse(content=challenge)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")
