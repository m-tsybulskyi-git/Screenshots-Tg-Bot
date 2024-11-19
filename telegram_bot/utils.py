from telegram_bot.config import config
from telethon import Button

async def send_message_to_admin(message, client): 
    await client.send_message(message=message, entity=config['admin_username'], buttons=generalButtons())
    
async def send_file_to_admin(video_path, caption, client): 
    await client.send_file(caption=caption, entity=config['admin_username'], file=video_path, buttons=generalButtons())

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
    lines.append(Button.inline("Refresh", b"refresh"))
    return [lines]
