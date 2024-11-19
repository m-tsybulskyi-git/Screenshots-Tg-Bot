import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telegram_bot import utils, config, handlers
from utils import files

load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
AUTH_METHOD = "bot_token"

async def init(client: TelegramClient): 
    if(AUTH_METHOD == "phone"):
        await client.start(phone=PHONE_NUMBER)
    else: 
        await client.start(bot_token=BOT_TOKEN) 

    await config.init(client, ADMIN_USERNAME)
    files.init()
    await handlers.setup_handlers(client)
    
async def main():
    client = TelegramClient('bot_session', API_ID, API_HASH)
    await init(client)
    print("Bot started...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())