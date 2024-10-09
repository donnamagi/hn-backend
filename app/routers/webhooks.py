from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx
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

    message = (
        payload.entry[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("messages", [{}])[0]
    )

    if message.get("type") == "text":
        business_phone_number_id = (
            payload.entry[0]
            .get("changes", [{}])[0]
            .get("value", {})
            .get("metadata", {})
            .get("phone_number_id")
        )

        async with httpx.AsyncClient() as client:
            # Send reply message
            await client.post(
                f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages",
                headers={"Authorization": f"Bearer {GRAPH_API_TOKEN}"},
                json={
                    "messaging_product": "whatsapp",
                    "to": message["from"],
                    "text": {"body": f"got it: {message['text']['body']}"},
                    "context": {"message_id": message["id"]},
                },
            )

            # Mark message as read
            await client.post(
                f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages",
                headers={"Authorization": f"Bearer {GRAPH_API_TOKEN}"},
                json={
                    "messaging_product": "whatsapp",
                    "status": "read",
                    "message_id": message["id"],
                },
            )

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
