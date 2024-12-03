from datetime import timedelta
from telethon import events
from telegram_bot import utils
from utils import files as file_utils
from actions import capture, processing
from telegram_bot.config import general_config, capture_config, scenario_config
import asyncio
from utils.logging import timeit

async def setup_handlers(client):

    @client.on(events.CallbackQuery(pattern='(?i)^auto_capture$'))
    async def toggle_capture_handler(event):
        print("Toggle autocapture (callback)")
        if event.chat_id == general_config.admin_chat_id:
            capture_config.auto_capture = not capture_config.auto_capture
            response = f"**Timelapse capture at each timeline is now {"ON" if capture_config.auto_capture else "OFF"}.**"
            await event.reply(response, buttons=utils.generalButtons())

    @client.on(events.NewMessage(pattern=r'(?i)auto_capture (on|off)'))
    async def toggle_capture_handler(event: events.NewMessage.Event):
        print("Toggle autocapture (message)")
        if event.chat_id == general_config.admin_chat_id:
            setting = event.pattern_match.group(1).lower()
            if setting == 'on':
                capture_config.auto_capture = True
                response = "**Timelapse capture at each timeline is now ON.**"
            elif setting == 'off':
                capture_config.auto_capture = False
                response = "**Timelapse capture at each timeline is now OFF.**"
            await event.reply(response, buttons=utils.generalButtons())

    @client.on(events.NewMessage(pattern=r'(?i)duration (\d+)(?: (seconds?|minutes?|hours?))?'))
    async def duration_handler(event: events.NewMessage.Event):
        print("Change timelaps duration (message)")
        if event.chat_id == general_config.admin_chat_id:
            time_unit = event.pattern_match.group(2)
            time_value = int(event.pattern_match.group(1)) 
            if time_unit != None:
                if 'minutes' in time_unit:
                    time_value = time_value * 60 # convert to seconds
                elif 'hours' in time_unit:
                    time_value = time_value * 60 * 60
            capture_config.duration = time_value
            response = f"**Time-lapse duration set to {timedelta(seconds=time_value)}.**"
            await event.reply(response, buttons=utils.generalButtons())

    @client.on(events.NewMessage(pattern=r'(?i)timeline (\d+)(?: (seconds?|minutes?|hours?))?'))
    async def timeline_handler(event: events.NewMessage.Event):
        print("Change timelaps timeline (message)")
        if event.chat_id == general_config.admin_chat_id:
            time_unit = event.pattern_match.group(2)
            time_value = int(event.pattern_match.group(1)) 
            if time_unit != None:
                if 'minutes' in time_unit:
                    time_value = time_value * 60
                elif 'hours' in time_unit:
                    time_value = time_value * 60 * 60
            capture_config.timeline = time_value  
            response = f"**Recorded duration set to {timedelta(seconds=time_value)}.**"
            await event.reply(response, buttons=utils.generalButtons())

    @client.on(events.NewMessage(pattern=r'(?i)delay (\d+)(?: (seconds?|minutes?|hours?))?'))
    async def scenario_delay_handler(event: events.NewMessage.Event):
        print("Change scenario delay (message)")
        if event.chat_id == general_config.admin_chat_id:
            time_unit = event.pattern_match.group(2)
            time_value = int(event.pattern_match.group(1)) 
            if time_unit != None:
                if 'minutes' in time_unit:
                    time_value = time_value * 60
                elif 'hours' in time_unit:
                    time_value = time_value * 60 * 60
            scenario_config.delay = time_value  
            response = f"**Autoclick delay set to {timedelta(seconds=time_value)}.**"
            await event.reply(response)

    @client.on(events.NewMessage(pattern=r'(?i)autoclick (on|off)'))
    async def toggle_autoclick_handler(event: events.NewMessage.Event):
        print("Toggle autoclick (message)")
        if event.chat_id == general_config.admin_chat_id:
            setting = event.pattern_match.group(1).lower()
            if setting == 'on':
                scenario_config.ongoing_scenario = True
                response = "**Autoclick is now ON.**"
            elif setting == 'off':
                scenario_config.ongoing_scenario = False
                response = "**Autoclick is now OFF.**"
            await event.reply(response)
            await run_scenario(event)

    @client.on(events.CallbackQuery(pattern='(?i)^auto_click$'))
    async def toggle_autoclick_handler(event):
        print("Toggle autoclick (callback)")
        if event.chat_id == general_config.admin_chat_id:
            scenario_config.ongoing_scenario = not scenario_config.ongoing_scenario
            if scenario_config.ongoing_scenario:
                await run_scenario(event)
            else: 
                await update_screen(event)
            file_utils.remove_tmp()

    @client.on(events.NewMessage(pattern='(?i)^/config$'))
    async def config_handler(event):
        print("Config (command)")
        if event.chat_id == general_config.admin_chat_id:
            config_message = f""" 
**Configuration**

**Capture**
`duration` X `seconds`/`minutes`/`hours` - sets video duration (set to {timedelta(seconds=capture_config.duration)})
`timeline` X `seconds`/`minutes`/`hours` - sets timelaps duration (set to {timedelta(seconds=capture_config.timeline)})
`auto_capture` (`on`/`off`) - to capture timelaps each timeline (set to {"ON" if capture_config.auto_capture else "OFF"})

**Autoclick**
`delay` X `seconds`/`minutes`/`hours` - repeat dalay in seconds (set to {timedelta(seconds=scenario_config.delay)})
`autoclick (`on`/`off`)` - to click last saved location repetivly based on repeat delay (set to {"ON" if scenario_config.ongoing_scenario else "OFF"})

`capture` - to capture timelaps
`cancel` - to cancel timelaps
`cancel_scenario` - to cancel scenarion
"""      
            await event.reply(config_message, buttons=utils.generalButtons())
      
    @client.on(events.CallbackQuery(pattern='(?i)^capture$'))
    @client.on(events.NewMessage(pattern='(?i)^capture$'))
    async def capture_handler(event):
        if event.chat_id == general_config.admin_chat_id:
            if not capture_config.ongoing_capture:
                capture_config.ongoing_capture = True
                if capture_config.auto_capture:
                    print("Timelaps started (periodicly)")
                    await capture.capture_timelapse_periodically(event)
                else:
                    print("Timelaps started")
                    await capture.capture_timelapse(event)
                capture_config.ongoing_capture = False
            else:
                print("Timelaps can not be started")
                await event.reply('**There is ongoing time-lapse capture (`cancel` previos operation first)**', buttons=utils.generalButtons())     

    @client.on(events.CallbackQuery(pattern='(?i)^cancel$'))
    @client.on(events.NewMessage(pattern='(?i)^cancel$'))
    async def cancel_handler(event):
        print("Cancel timelaps")
        if event.chat_id == general_config.admin_chat_id:
            if capture_config.ongoing_capture:
                capture_config.is_cancel_requested = True 
                await event.reply("**Cancellation requested for ongoing operations...**", buttons=utils.generalButtons())
            else:
                await event.reply("**There is nothing to cancel...**", buttons=utils.generalButtons())

    @client.on(events.NewMessage(pattern='(?i)^/screen$'))
    async def screenshot_handler(event):
        print("Take screenshot (command)")
        if event.chat_id == general_config.admin_chat_id:
            path = await capture.take_screenshot()
            await event.reply(file=path, buttons=utils.screenButtons())
            file_utils.remove_tmp()

    @client.on(events.CallbackQuery(pattern='(?i)^refresh$'))
    async def screen_refresh_handler(event: events.CallbackQuery.Event):
        print("Refresh screenshot (callback)")
        if event.chat_id == general_config.admin_chat_id:
            await update_screen(event)
    
    @client.on(events.NewMessage(func=lambda e: e.media is not None))
    async def click_on_screen_handler(event):
        print("Image recived from user")
        if event.chat_id == general_config.admin_chat_id and event.photo:
            saved_file_path = await event.download_media(file=file_utils.tmp_path("user_photo.png"))
            processing.click_on_color_spot(saved_file_path)
            await screen(event)
            
            file_utils.remove_tmp()

    @client.on(events.NewMessage(pattern='(?i)^/start$'))
    async def config_handler(event):
        print("Bot was started (command)")
        if event.chat_id == general_config.admin_chat_id:   
            await event.reply("**Bot started...**", buttons=utils.generalButtons())
      
async def run_scenario(event: events.NewMessage.Event):
    if scenario_config.x < 0 or scenario_config.y < 0:
            print("Cords not set")
            scenario_config.ongoing_scenario = False
            await event.reply("**Send image with cords first**")
    while scenario_config.ongoing_scenario:
        await auto_click(event)

@timeit
async def auto_click(event):
    print("Click on screen")
    processing.click_saved()
    print("Take screenshot")
    await update_screen(event)
    print(f"Waiting for {scenario_config.delay} seconds")
    await asyncio.sleep(scenario_config.delay) 

async def screen(event): 
    await asyncio.sleep(0.1)
    path = await capture.take_screenshot()
    await event.reply(file=path, buttons=utils.screenButtons())

async def update_screen(event): 
    await asyncio.sleep(0.1)
    path = await capture.take_screenshot()
    await event.edit(file=path, buttons=utils.screenButtons())
