from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import os
import httpx
from pathlib import Path

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


# https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages


# https://developers.facebook.com/docs/whatsapp/cloud-api/messages/audio-messages
@router.post("/send")
async def send_whatsapp_message(
    media_id: Optional[str] = None, receiver_phone_number: Optional[str] = None
):

    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
    WHATSAPP_API_URL = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"

    if not WHATSAPP_TOKEN:
        raise HTTPException(
            status_code=500, detail="WHATSAPP_TOKEN environment variable is not set"
        )

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": receiver_phone_number,
        "type": "audio",
        "audio": {"id": media_id},
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                WHATSAPP_API_URL, json=payload, headers=headers
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"WhatsApp API error: {e.response.text}",
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

    return response.json()


# https://developers.facebook.com/docs/whatsapp/cloud-api/reference/media#upload-media
@router.post("/upload-media")
async def upload_media(
    file_name: str, type: str = "audio/mpeg", messaging_product: str = "whatsapp"
):
    file_path = Path("tmp") / file_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    with open(file_path, "rb") as f:
        file_content = f.read()
        file_name = file_path.name

    WHATSAPP_API_URL = (
        f"https://graph.facebook.com/v21.0/{os.getenv('PHONE_NUMBER_ID')}/media"
    )
    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

    if not WHATSAPP_TOKEN:
        raise HTTPException(
            status_code=500, detail="WHATSAPP_TOKEN environment variable is not set"
        )

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    }

    form_data = {
        "file": (file_name, file_content, type),
        "type": (None, type),
        "messaging_product": (None, messaging_product),
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                WHATSAPP_API_URL, files=form_data, headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"WhatsApp API error: {e.response.text}",
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


# New Pydantic model for the webhook payload
class WebhookPayload(BaseModel):
    object: str
    entry: List[Dict[str, Any]]
