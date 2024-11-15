from datetime import timedelta
from telethon import events
from telegram_bot import utils
from capture import capture
import asyncio
from telegram_bot.config import config

async def setup_handlers(client):
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
            await event.reply(utils.commandsTemplate(response), parse_mode='md')

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
            message = f"**Time-lapse duration set to {timedelta(seconds=time_value)}.**"
            await event.reply(utils.commandsTemplate(message), parse_mode='md')

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
            message = f"**Recorded duration set to {timedelta(seconds=time_value)}.**"
            await event.reply(utils.commandsTemplate(message))

    @client.on(events.NewMessage(pattern='(?i)^capture$'))
    async def capture_handler(event: events.NewMessage.Event):
        if event.chat_id == config['admin_chat_id']:
            if not config['ongoing_capture']:
                config['ongoing_capture'] = True
                await event.reply(utils.commandsTemplate('**Starting new time-lapse capture...**')) 
                if config['auto_capture']:
                    await capture.capture_timelapse_periodically(event)
                else:
                    await capture.capture_timelapse(event)
                config['ongoing_capture'] = False
            else:
                await event.reply(utils.commandsTemplate('**There is ongoing time-lapse capture (`cancel` previos operation first)**'))     

    @client.on(events.NewMessage(pattern='(?i)^cancel$'))
    async def cancel_handler(event: events.NewMessage.Event):
        if event.chat_id == config['admin_chat_id']:
            if config['ongoing_capture']:
                config['is_cancel_requested'] = True 
                await event.reply(utils.commandsTemplate("**Cancellation requested for ongoing operations...**"))
            else:
                await event.reply(utils.commandsTemplate("**There is nothing to cancel...**"))