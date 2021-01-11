import utils
from dbUtils import rds


class Designate:
    """
    config_type = 6  1：支持真指定 0不支持
    config_type= 35 1：支持指定预防，0不支持
    config_type=145 1：支持假指定，0不支持
    """

    def __init__(self, session_id, user_id):
        self.session_id = session_id
        self.consignor_user_id = user_id
        self._real_designate_flag = utils.get_consignor_config(self.consignor_user_id, '6')
        self._advanced_designate_flag = utils.get_consignor_config(self.consignor_user_id, '35')
        self._fake_designate_flag = utils.get_consignor_config(self.consignor_user_id, '145')
        self.designate_info = {
            "designCarrier": "0",
            "isAdvance": "",
            "appointCarrierMobiles": "",
            "appointCarrierUserIds": "",
            "appointCarrierNames": "",
            "appointCarrierUserTypes": "",
            "appointCarrierIfExists": "",
            "appointStaffMobiles": "",
            "appointStaffUserIds": "",
            "appointStaffNames": "",
            "appointStaffUserTypes": "",
            "appointStaffIfExists": "",
            "settleNumber": ""
        }

    # 是否指定
    def __call__(self, designCarrier: bool = False, carrier_list: list = None):
        if str(self._real_designate_flag) == '1':
            self.designate_info['designCarrier'] = "1" if designCarrier else "0"
        if designCarrier:
            if str(self._advanced_designate_flag) == '1':
                self.designate_info['advanceRatioSelect'] = "50"

        if not carrier_list:
            rds.hset(self.session_id, 'designate', str(self.designate_info))
            return self.designate_info
        else:
            _carrier_mobile_list = []
            _carrier_userid_list = []
            _carrier_name_list = []
            _carrier_user_type_list = []
            _carrier_exist_list = []
            for u in carrier_list:
                user = utils.get_user_by_serial_number(u)
                _carrier_mobile_list.append(user.get('CONTACTER_PHONE'))
                _carrier_userid_list.append(str(user.get('USER_ID')))
                _carrier_name_list.append(user.get('CONTACTER'))
                _carrier_user_type_list.append(user.get('USER_TYPE'))
                _carrier_exist_list.append('0')
            self.designate_info['appointCarrierMobiles'] = ','.join(_carrier_mobile_list)
            self.designate_info['appointCarrierUserIds'] = ','.join(_carrier_userid_list)
            self.designate_info['appointCarrierNames'] = ','.join(_carrier_name_list)
            self.designate_info['appointCarrierUserTypes'] = ','.join(_carrier_user_type_list)
            self.designate_info['appointCarrierIfExists'] = '.'.join(_carrier_exist_list)
            rds.hset(self.session_id, 'designate', str(self.designate_info))
            return self.designate_info


if __name__ == "__main__":
    designate = Designate('123', '1344259924674217981')
    r = designate(designCarrier=True, carrier_list=['17926663112'])
    print(r)
