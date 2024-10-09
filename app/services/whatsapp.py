import httpx
import os
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_whatsapp_request(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            async with httpx.AsyncClient() as client:
                response = await func(self, client, *args, **kwargs)
                response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error occurred: {e.response.status_code} {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    return wrapper


class WhatsAppService:
    def __init__(self):
        self.graph_api_token = os.getenv("WHATSAPP_TOKEN")
        self.base_url = "https://graph.facebook.com/v21.0"

    @handle_whatsapp_request
    async def send_message(self, client, phone_number_id, to, message_body, message_id):
        return await client.post(
            f"{self.base_url}/{phone_number_id}/messages",
            headers={"Authorization": f"Bearer {self.graph_api_token}"},
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "text": {"body": message_body},
                "context": {"message_id": message_id},
            },
        )

    @handle_whatsapp_request
    async def mark_as_read(self, client, phone_number_id, message_id):
        return await client.post(
            f"{self.base_url}/{phone_number_id}/messages",
            headers={"Authorization": f"Bearer {self.graph_api_token}"},
            json={
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id,
            },
        )
