from typing import Dict, Any
import httpx
import re


class MessageService:
    def __init__(self):
        self

    def process_text_message(self, message: str) -> str:
        """
        Process incoming text messages and generate a response.
        """

        def is_valid_url(url: str) -> bool:
            url_pattern = re.compile(
                r"(?:(?:https?|ftp):\/\/)?(?:www\.)?(?:[\w]+\.)+[\w]+(?:\/[\w.\/?%&=]*)?",
                re.IGNORECASE,
            )
            # check if starts with http:// or https://
            https_pattern = re.compile(r"^(?:http|ftp)s?://", re.IGNORECASE)
            return (
                url_pattern.match(url) is not None,
                https_pattern.match(url) is not None,
            )

        is_valid, is_https = is_valid_url(message)
        if is_valid:
            try:
                response = (
                    httpx.get(message) if is_https else httpx.get(f"https://{message}")
                )
                response.raise_for_status()
                return f"You sent a valid URL: {message}"
            except httpx.HTTPError:
                return (
                    f"The URL you sent ({message}) is valid, but I couldn't access it."
                )

        return f"You said: {message}"

    def process_audio_message(self, audio_url: str) -> str:
        """
        Process incoming audio messages and generate a response.
        """
        # audio processing logic

        return "I've received your audio message, but I'm not able to process it yet."

    def create_response(self, message_type: str, content: Dict[str, Any]) -> str:
        """
        Create a response based on the type of message received.
        """
        if message_type == "text":
            return self.process_text_message(content["body"])
        # elif message_type == "audio":
        #     return self.process_audio_message(content["url"])
        else:
            return "I'm sorry, I can't process this type of message yet."
