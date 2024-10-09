from app.services.whatsapp import WhatsAppService
from app.services.messages import MessageService
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebhookHandler:
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        self.message_service = MessageService()

    async def handle(self, payload):
        message = (
            payload.entry[0]
            .get("changes", [{}])[0]
            .get("value", {})
            .get("messages", [{}])[0]
        )
        business_phone_number_id = (
            payload.entry[0]
            .get("changes", [{}])[0]
            .get("value", {})
            .get("metadata", {})
            .get("phone_number_id")
        )

        if message.get("type") == "text":
            response = self.message_service.create_response(
                message["type"], message["text"]
            )
            logging.info(f"Created response: {response}")

            await self.whatsapp_service.send_message(
                business_phone_number_id, message["from"], response, message["id"]
            )
            logging.info(f"Sent response: {message['id']}")

            await self.whatsapp_service.mark_as_read(
                business_phone_number_id, message["id"]
            )
            logging.info(f"Message marked as read: {message['id']}")
