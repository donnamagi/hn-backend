import httpx
import os


class WhatsAppService:
    def __init__(self):
        self.graph_api_token = os.getenv("WHATSAPP_TOKEN")

    async def send_message(self, phone_number_id, to, message_body, message_id):
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://graph.facebook.com/v18.0/{phone_number_id}/messages",
                headers={"Authorization": f"Bearer {self.graph_api_token}"},
                json={
                    "messaging_product": "whatsapp",
                    "to": to,
                    "text": {"body": message_body},
                    "context": {"message_id": message_id},
                },
            )

    async def mark_as_read(self, phone_number_id, message_id):
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://graph.facebook.com/v18.0/{phone_number_id}/messages",
                headers={"Authorization": f"Bearer {self.graph_api_token}"},
                json={
                    "messaging_product": "whatsapp",
                    "status": "read",
                    "message_id": message_id,
                },
            )
