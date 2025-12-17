import requests
from ..utils.constants import BOT_TOKEN, TELEGRAM_API_URL  # Fixed relative import
from ..utils.helpers import format_message   # Also fixed if needed
from common.exceptions import NotificationFailureError  # Added

class TelegramService:
    """Service for Telegram bot interactions (GOF: Strategy for message sending)."""
    def send_message(self, chat_id, text):
        url = f"{TELEGRAM_API_URL}{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise NotificationFailureError("Failed to send Telegram message")  # Modified
        return response.json()

    def handle_webhook(self, data):
        # Process incoming webhook data (e.g., user messages)
        chat_id = data.get('message', {}).get('chat', {}).get('id')
        text = data.get('message', {}).get('text')
        # Logic to respond or link user
        return {"status": "ok"}