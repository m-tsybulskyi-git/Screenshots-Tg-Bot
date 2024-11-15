config = {
    'admin_username': '@dev44level',
    'admin_chat_id': None, 
    'duration': 1,
    'timeline': 5, 
    'frame_rate': 30, # frames per second
    'auto_capture': False,
    'is_cancel_requested': False,
    'ongoing_capture': False
}

async def init(client):
    config['admin_chat_id'] = await get_admin_chat_id(config['admin_username'], client)
    if config['admin_chat_id'] == None: 
        exit

async def get_admin_chat_id(username, client):
    try:
        user = await client.get_entity(username)
        return user.id
    except ValueError:
        print("Failed to retrieve user with username:", username)
        return None