from telegram_bot.config import capture_config, scenario_config
from telethon import Button
from datetime import datetime

def generalButtons():
    lines = list()
    if not capture_config.is_cancel_requested:
        if capture_config.ongoing_capture: 
            lines.append(Button.inline("Cancel", b"cancel"))
        else:
            lines.append(Button.inline("Start", b"capture"))
    lines.append(Button.inline(f"Auto Capture {"🔘" if capture_config.auto_capture else "⚪️"}", b"auto_capture"))
    return [lines]

def screenButtons():
    lines = list()
    refreshed_at = datetime.now().strftime("%H:%M:%S")
    lines.append(Button.inline(f"Refresh ({refreshed_at})", b"refresh"))
    lines.append(Button.inline(f"Auto Click {"🔘" if scenario_config.ongoing_scenario else "⚪️"}", b"auto_click"))
    return [lines]
