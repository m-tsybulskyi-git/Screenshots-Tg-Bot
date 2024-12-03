import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telegram_bot import config, handlers
from utils import files
import builtins
import datetime

load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_ID = os.getenv('ADMIN_ID')
AUTH_METHOD = "bot_token"

original_print = builtins.print

def custom_print(*args, **kwargs):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    original_print(f"[{current_time}]", *args, **kwargs)

async def init(client: TelegramClient): 
    if(AUTH_METHOD == "phone"):
        await client.start(phone=PHONE_NUMBER) 
    elif(AUTH_METHOD == "bot_token"): 
        await client.start(bot_token=BOT_TOKEN) 

    await config.init(client, ADMIN_USERNAME, ADMIN_ID)
    files.init()
    await handlers.setup_handlers(client)
    builtins.print = custom_print
    
async def main():
    client = TelegramClient('bot_session', API_ID, API_HASH)
    await init(client)
    print("Bot started...")
    while True:
        try:
            print("Trying to connect...")
            await client.connect()
            if not client.is_connected():
                print("Failed to connect. Retrying in 5 seconds...")
                await asyncio.sleep(5)
            else:
                print("Connected!")
                await client.run_until_disconnected()
        except KeyboardInterrupt:
            exit
        except Exception:
            print("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == '__main__':
    import asyncio
    try: 
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Application was exited...")