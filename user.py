import utils
from dbUtils import rds
from component import Owner, Carrier, Admin


class User:
    """
    实例化不同角色的工厂类，用于Session实例化方法
    """

    def __init__(self, session_id, account):
        self.session_id = session_id
        self._account = account

    @property
    def owner_create(self):
        consignor = utils.get_user_by_serial_number(self._account)
        consignor_user_id = consignor.get('USER_ID')
        rds.hset(self.session_id, 'consignor_user_id', consignor_user_id)
        return Owner(self.session_id, self._account, consignor_user_id)

    @property
    def carrier_create(self):
        carrier = utils.get_user_by_serial_number(self._account)
        carrier_user_id = carrier.get('USER_ID')
        rds.hset(self.session_id, 'carrier_user_id', carrier_user_id)
        return Carrier(self.session_id, carrier_user_id, self._account)

    @property
    def admin_create(self):
        return Admin(self.session_id, self._account)
