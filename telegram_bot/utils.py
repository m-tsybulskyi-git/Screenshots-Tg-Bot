from datetime import timedelta
from telegram_bot.config import config

async def send_message_to_admin(message, client): 
    await client.send_message(message=commandsTemplate(message), entity=config['admin_username'])

async def send_file_to_admin(video_path, caption, client): 
    await client.send_file(caption=commandsTemplate(caption), entity=config['admin_username'], file=video_path)

def commandsTemplate(message):
    return f"""{message}

`duration` X `seconds`/`minutes`/`hours` - sets video duration (set to {timedelta(seconds=config['duration'])})
`timeline` X `seconds`/`minutes`/`hours` - sets timelaps duration (set to {timedelta(seconds=config['timeline'])})
`auto_capture` (`on`/`off`) - to capture timelaps each timeline (set to {config['auto_capture']})

`capture` - to capture timelaps
`cancel` - to cancel timelaps
"""