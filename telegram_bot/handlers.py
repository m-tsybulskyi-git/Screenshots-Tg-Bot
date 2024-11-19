from datetime import timedelta
from telethon import events
from telegram_bot import utils
from utils import files as file_utils
from capture import capture, processing
from telegram_bot.config import config
import asyncio

async def setup_handlers(client):

    @client.on(events.CallbackQuery(pattern='(?i)^auto_capture$'))
    async def toggle_capture_handler(event):
        if event.chat_id == config['admin_chat_id']:
            config['auto_capture'] = not config['auto_capture']
            response = f"**Timelapse capture at each timeline is now {"ON" if config['auto_capture'] else "OFF"}.**"
            await event.reply(response, buttons=utils.generalButtons())

    @client.on(events.NewMessage(pattern=r'(?i)auto_capture (on|off)'))
    async def toggle_capture_handler(event: events.NewMessage.Event):
        if event.chat_id == config['admin_chat_id']:
            setting = event.pattern_match.group(1).lower()
            if setting == 'on':
                config['auto_capture'] = True
                response = "**Timelapse capture at each timeline is now ON.**"
            elif setting == 'off':
                config['auto_capture'] = False
                response = "**Timelapse capture at each timeline is now OFF.**"
            await event.reply(response, buttons=utils.generalButtons())

    @client.on(events.NewMessage(pattern=r'(?i)duration (\d+)(?: (seconds?|minutes?|hours?))?'))
    async def duration_handler(event: events.NewMessage.Event):
        if event.chat_id == config['admin_chat_id']:
            time_unit = event.pattern_match.group(2)
            time_value = int(event.pattern_match.group(1)) 
            if time_unit != None:
                if 'minutes' in time_unit:
                    time_value = time_value * 60 # convert to seconds
                elif 'hours' in time_unit:
                    time_value = time_value * 60 * 60
            config['duration'] = time_value
            response = f"**Time-lapse duration set to {timedelta(seconds=time_value)}.**"
            await event.reply(response, buttons=utils.generalButtons())

    @client.on(events.NewMessage(pattern=r'(?i)timeline (\d+)(?: (seconds?|minutes?|hours?))?'))
    async def timeline_handler(event: events.NewMessage.Event):
        if event.chat_id == config['admin_chat_id']:
            time_unit = event.pattern_match.group(2)
            time_value = int(event.pattern_match.group(1)) 
            if time_unit != None:
                if 'minutes' in time_unit:
                    time_value = time_value * 60
                elif 'hours' in time_unit:
                    time_value = time_value * 60 * 60
            config['timeline'] = time_value  
            response = f"**Recorded duration set to {timedelta(seconds=time_value)}.**"
            await event.reply(response, buttons=utils.generalButtons())

    @client.on(events.CallbackQuery(pattern='(?i)^capture$'))
    @client.on(events.NewMessage(pattern='(?i)^capture$'))
    async def capture_handler(event):
        if event.chat_id == config['admin_chat_id']:
            if not config['ongoing_capture']:
                config['ongoing_capture'] = True
                if config['auto_capture']:
                    await capture.capture_timelapse_periodically(event)
                else:
                    await capture.capture_timelapse(event)
                config['ongoing_capture'] = False
            else:
                await event.reply('**There is ongoing time-lapse capture (`cancel` previos operation first)**', buttons=utils.generalButtons())     

    @client.on(events.CallbackQuery(pattern='(?i)^cancel$'))
    @client.on(events.NewMessage(pattern='(?i)^cancel$'))
    async def cancel_handler(event):
        if event.chat_id == config['admin_chat_id']:
            if config['ongoing_capture']:
                config['is_cancel_requested'] = True 
                await event.reply("**Cancellation requested for ongoing operations...**", buttons=utils.generalButtons())
            else:
                await event.reply("**There is nothing to cancel...**", buttons=utils.generalButtons())

    @client.on(events.NewMessage(pattern='(?i)^/config$'))
    async def config_handler(event):
        if event.chat_id == config['admin_chat_id']:
            config_message = f""" 
**Configuration**

`duration` X `seconds`/`minutes`/`hours` - sets video duration (set to {timedelta(seconds=config['duration'])})
`timeline` X `seconds`/`minutes`/`hours` - sets timelaps duration (set to {timedelta(seconds=config['timeline'])})
`auto_capture` (`on`/`off`) - to capture timelaps each timeline (set to {"ON" if config['auto_capture'] else "OFF"})

`capture` - to capture timelaps
`cancel` - to cancel timelaps
"""      
            await event.reply(config_message, buttons=utils.generalButtons())
      
    @client.on(events.NewMessage(pattern='(?i)^/screen$'))
    async def screenshot_handler(event):
        if event.chat_id == config['admin_chat_id']:
            path = await capture.take_screenshot()
            await event.reply(file=path, buttons=utils.screenButtons())
            file_utils.remove_tmp()

    @client.on(events.CallbackQuery(pattern='(?i)^refresh$'))
    async def screen_refresh_handler(event: events.CallbackQuery.Event):
        if event.chat_id == config['admin_chat_id']:
            path = await capture.take_screenshot()
            try:
                await event.edit(file=path, buttons=utils.screenButtons())
            finally:
                file_utils.remove_tmp()
    
    @client.on(events.NewMessage(func=lambda e: e.media is not None))
    async def click_on_screen_handler(event):
        if event.chat_id == config['admin_chat_id'] and event.photo:
            saved_file_path = await event.download_media(file=file_utils.tmp_path("user_photo.png"))
            processing.click_on_color_spot(saved_file_path)
            await asyncio.sleep(0.1)
            path = await capture.take_screenshot()
            await event.reply(file=path, buttons=utils.screenButtons())
            
            file_utils.remove_tmp()

    @client.on(events.NewMessage(pattern='(?i)^/start$'))
    async def config_handler(event):
        if event.chat_id == config['admin_chat_id']:   
            await event.reply("**Bot started...**", buttons=utils.generalButtons())
      