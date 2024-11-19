config = {
    'admin_chat_id': None, 
    'duration': 60,
    'timeline': 60 * 60 * 6, #hours
    'frame_rate': 30, # frames per second
    'auto_capture': True,
    'is_cancel_requested': False,
    'ongoing_capture': False
}

async def init(client, admin_username):
    config['admin_chat_id'] = await get_admin_chat_id(admin_username, client)
    if config['admin_chat_id'] == None: 
        exit

async def get_admin_chat_id(username, client):
    try:
        user = await client.get_entity(username)
        return user.id
    except ValueError:
        print("Failed to retrieve user with username:", username)
        return None