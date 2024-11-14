import os
import time
import numpy as np
import cv2
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telethon import TelegramClient, events
from mss import mss
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
from fastprogress import progress_bar

load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

ADMIN_USERNAME = '@dev44level'

TMP_DIR = 'tmp/'
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

config = {
    'admin_chat_id': None, 
    'duration': 60,
    'timeline': 60*15, 
    'frame_rate': 30, # frames per second
    'auto_capture': False,
}

def commandsTemplate(message=''):
    return f"""{message}

`duration` X `seconds`/`minutes`/`hours` - sets video duration (set to {timedelta(seconds=config['duration'])})
`timeline` X `seconds`/`minutes`/`hours` - sets timelaps duration (set to {timedelta(seconds=config['timeline'])})
`auto_capture` (`on`/`off`) - to capture timelaps each timeline (set to {config['auto_capture']})

`capture` - to capture timelaps
"""

client = TelegramClient('bot_session', API_ID, API_HASH)

async def get_admin_chat_id(username):
    try:
        user = await client.get_entity(username)
        return user.id
    except ValueError:
        print("Failed to retrieve user with username:", username)
        return None
    
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
        await event.reply(commandsTemplate(response), parse_mode='md')

@client.on(events.NewMessage(pattern=r'(?i)duration (\d+)(?: (minutes?|hours?))?'))
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
        await event.reply(commandsTemplate(message), parse_mode='md')

@client.on(events.NewMessage(pattern=r'(?i)timeline (\d+)(?: (minutes?|hours?))?'))
async def timeline_handler(event: events.NewMessage.Event):
    if event.chat_id == config['admin_chat_id']:
        time_unit = event.pattern_match.group(2)
        time_value = int(event.pattern_match.group(1)) 
        if time_unit != None:
            if 'minutes' in time_unit:
                time_value = time_value * 60 # convert to seconds
            elif 'hours' in time_unit:
                time_value = time_value * 60 * 60
        config['timeline'] = time_value  
        message = f"**Recorded duration set to {timedelta(seconds=time_value)}.**"
        await event.reply(commandsTemplate(message), parse_mode='md')

@client.on(events.NewMessage)
async def capture_handler(event: events.NewMessage.Event):
    if event.chat_id == config['admin_chat_id'] and event.text.lower() == 'capture':
        await event.reply(commandsTemplate('**Starting new time-lapse capture...**')) 
        if 'auto_capture_task' in globals():
            auto_capture_task.cancel()
        if config['auto_capture']:
            auto_capture_task = asyncio.create_task(capture_timelapse_periodically())
        else:
            await capture_timelapse()
        

async def capture_timelapse_periodically():
    try:
        while config['auto_capture']: 
            await capture_timelapse()
    except asyncio.CancelledError:
        print("Timelapse capture task was cancelled.")

async def capture_timelapse(): 
    screenshots = take_screenshots_in_memory(config['timeline'], config['duration'])
    video_path = create_timelapse_video_from_memory(screenshots)
    await client.send_file(file=video_path, entity=ADMIN_USERNAME, caption='**Here is your time-lapse video**', parse_mode='md')
    remove_tmp()

def take_screenshots_in_memory(timeline, duration):
    print("Screenshots creation started...")
    screenshots = []

    total_frames = duration * config['frame_rate']
    interval = timeline / total_frames

    with mss() as sct:
        monitor = sct.monitors[1]
        for i in progress_bar(range(1, total_frames), display=1):
            now = datetime.now()
                
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            screenshots.append(img)
                
            while (datetime.now() - now).total_seconds() < interval:
                time.sleep(0.001) 
            i += 1
    return screenshots

def remove_tmp(): 
    files = os.listdir(TMP_DIR)
    for file in files:
        file_path = os.path.join(TMP_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

def create_timelapse_video_from_memory(frames):
    print("Vides creation started...")
    timelapse_tmp_path = tmp_path('timelapse_tmp.mp4')
    height, width, _ = frames[0].shape
    out = cv2.VideoWriter(timelapse_tmp_path, cv2.VideoWriter_fourcc(*'mp4v'), config['frame_rate'], (width, height))

    for frame in progress_bar(frames, display=1):
        out.write(frame)

    out.release()

    video_clip = VideoFileClip(timelapse_tmp_path)

    duration_in_ms = len(frames) / config['frame_rate'] * 1000
    audio_path = tmp_path('silent_audio.mp3')
    silent_audio = AudioSegment.silent(duration=duration_in_ms, frame_rate=44100)
    silent_audio.export(audio_path, format="mp3")
    audio_clip = AudioFileClip(audio_path)
    
    # Set the audio of the video clip as the silent audio file
    final_clip = video_clip.set_audio(audio_clip)
    final_output_path = tmp_path('timelapse.mp4')
    final_clip.write_videofile(final_output_path, codec='libx264')

    print(f"Video saved as {final_output_path}")
    return final_output_path

def tmp_path(path): 
    return TMP_DIR + path

async def main():
    await client.start(phone=PHONE_NUMBER)
    config['admin_chat_id'] = await get_admin_chat_id(ADMIN_USERNAME)
    if config['admin_chat_id'] == None: 
        exit
    print("Bot started...")
    await client.send_message(message=commandsTemplate('**Bot Commands:**'), entity=ADMIN_USERNAME, parse_mode='md')
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())