import os

BOT_TOKEN = os.getenv('BOT_TOKEN')
TELEGRAM_API_URL = "https://api.telegram.org/bot"
MESSAGE_TYPES = ['booking', 'reminder', 'cancellation', 'reschedule']