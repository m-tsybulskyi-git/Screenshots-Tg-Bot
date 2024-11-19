from telegram_bot.config import config
from telethon import Button
from datetime import datetime

def generalButtons():
    lines = list()
    if not config['is_cancel_requested']:
        if config['ongoing_capture']: 
            lines.append(Button.inline("Cancel", b"cancel"))
        else:
            lines.append(Button.inline("Start", b"capture"))
    lines.append(Button.inline(f"Auto {"🔘" if config['auto_capture'] else "⚪️"}", b"auto_capture"))
    return [lines]

def screenButtons():
    lines = list()
    refreshed_at = datetime.now().strftime("%H:%M:%S")
    lines.append(Button.inline(f"Refresh ({refreshed_at})", b"refresh"))
    return [lines]
