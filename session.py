import uuid
from user import User
from stage import Stage
import config


class Session:
    """
    核心对象，所有的功能都必须在这注册
    """

    def __init__(self):
        self.session_id = str(uuid.uuid1())
        self.admin = User(self.session_id, config.ADMIN_ACCOUNT, ).admin_create
        self.owner = User(self.session_id, config.OWNER_PHONE).owner_create
        self.carrier = User(self.session_id, config.CARRIER_PHONE).carrier_create
        self.stage = Stage(self.session_id, self.owner)
