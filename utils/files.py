import os
import asyncio

TMP_DIR = 'tmp/'

def init():
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

async def remove_tmp(): 
    await asyncio.sleep(5)
    files = os.listdir(TMP_DIR)
    for file in files:
        file_path = os.path.join(TMP_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

def tmp_path(path): 
    return TMP_DIR + path