class Scenario():
    x: int = -1
    y: int = -1
    delay: int = 60 * 60 
    duration: int = None
    ongoing_scenario: bool = False

class Capture():
    duration: int = 60
    timeline: int = 60 * 60 * 3
    frame_rate: int = 30
    auto_capture: bool = True
    is_cancel_requested: bool = False
    ongoing_capture: bool = False

class General():
    admin_chat_id: str = None

capture_config: Capture = Capture()
scenario_config: Scenario = Scenario()
general_config: General = General()

async def init(client, admin_username, admin_id):
    admin_id_actual = admin_id
    if not admin_id_actual: 
        admin_id_actual  = await get_admin_chat_id(admin_username, client)
    if not admin_id_actual: 
        exit
    general_config.admin_chat_id = admin_id_actual

async def get_admin_chat_id(username, client):
    try:
        user = await client.get_entity(username)
        return user.id
    except ValueError:
        print("Failed to retrieve user with username:", username)
        return None