import os
import time

TMP_DIR = 'tmp/'

def init():
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

def remove_tmp(): 
    files = os.listdir(TMP_DIR)
    
    for file in files:
        file_path = os.path.join(TMP_DIR, file)
        if os.path.isfile(file_path):
            try: 
                os.remove(file_path)
            except WindowsError:
                time.sleep(0.01) 
            else: 
                break   

def tmp_path(path): 
    return TMP_DIR + path