import numpy as np
import cv2
from datetime import datetime
from mss import mss
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
from fastprogress import progress_bar
from utils import files as util
from telegram_bot.utils import generalButtons
import asyncio

from telegram_bot.config import config 

async def take_screenshots_in_memory(timeline, duration):

    print("Screenshots creation started...")
    screenshots = []

    total_frames = duration * config['frame_rate']
    interval = timeline / total_frames
  
    with mss() as screen:
        monitor = screen.monitors[1]
        for _ in progress_bar(range(0, total_frames), display=1):
            
            if config['is_cancel_requested']:
                config['is_cancel_requested'] = False
                break

            now = datetime.now()
                    
            screenshot = screen.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            screenshots.append(img)
                    
            while (datetime.now() - now).total_seconds() < interval:
                await asyncio.sleep(0.001) 

    return screenshots

async def take_screenshot():
    with mss() as screen:
        monitor = screen.monitors[1]
        screenshot = screen.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        file_name = datetime.now().strftime('screenshot_%d-%m-%Y__%H_%M.png')
        path = util.tmp_path(file_name)
        cv2.imwrite(path, img)
        return path

def create_timelapse_video_from_memory(screenshots):
    print("Vides creation started...")
    timelapse_tmp_path = util.tmp_path('timelapse_tmp.mp4')
    if screenshots[0] is None:
        raise Exception
    height, width, _ = screenshots[0].shape
    out = cv2.VideoWriter(timelapse_tmp_path, cv2.VideoWriter_fourcc(*'mp4v'), config['frame_rate'], (width, height))

    for frame in progress_bar(screenshots, display=1):
        out.write(frame)

    out.release()

    video_clip = VideoFileClip(timelapse_tmp_path)

    duration_in_ms = len(screenshots) / config['frame_rate'] * 1000
    audio_path = util.tmp_path('silent_audio.mp3')
    silent_audio = AudioSegment.silent(duration=duration_in_ms, frame_rate=44100)
    silent_audio.export(audio_path, format="mp3")
    audio_clip = AudioFileClip(audio_path)
    
    final_clip = video_clip.set_audio(audio_clip)
    final_output_path = util.tmp_path('timelapse.mp4')
    final_clip.write_videofile(final_output_path, codec='libx264')

    print(f"Video saved as {final_output_path}")
    return final_output_path

async def capture_timelapse_periodically(event): 
    while config['auto_capture']: 
        await capture_timelapse(event)

async def capture_timelapse(event): 
    await event.reply('**Starting new time-lapse capture...**', buttons=generalButtons()) 
    screenshots = await take_screenshots_in_memory(config['timeline'], config['duration'])
    video_path = create_timelapse_video_from_memory(screenshots)
    await event.reply(file=video_path)
    await util.remove_tmp()
