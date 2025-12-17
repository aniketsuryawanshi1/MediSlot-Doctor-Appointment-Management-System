import os
import warnings

# FIXED: Added validation for BOT_TOKEN
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    warnings.warn(
        "BOT_TOKEN not set in environment variables. "
        "Telegram notifications will fail. "
        "Please set BOT_TOKEN in your .env file.",
        RuntimeWarning
    )

TELEGRAM_API_URL = "https://api.telegram.org/bot"
MESSAGE_TYPES = ['booking', 'reminder', 'cancellation', 'reschedule']