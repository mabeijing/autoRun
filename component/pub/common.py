import datetime
import utils
import logging

logger = logging.getLogger(__name__)


class Common:
    """
    货主基本信息
    结算榜单类型
    是否预挂
    批量发布
    """

    def __init__(self, session_id, user_id):
        self.session_id = session_id
        self.consignor_user_id = user_id
        self.common_info = {}

    def _get_user_info(self):
        user = utils.get_user_by_user_id(user_id=self.consignor_user_id)
        _contactName = user.get('CONTACTER', None)
        _contactPhone = user.get('CONTACTER_PHONE', None)
        self.common_info['contactName'] = _contactName
        self.common_info['contactPhone'] = _contactPhone

    def _batchPublishNum(self, batch_publish: str = "1"):
        self.common_info['batchPublishNum'] = batch_publish

    def _settleBasisType(self, settle_type: str = "2"):
        self.common_info['settleBasisType'] = settle_type

    def _orderPresetPublishFlag(self, preset_publish: bool = False):
        self.common_info['orderPresetPublishFlag'] = "1" if preset_publish else "0"

    def _publish_time(self, preset_publish: bool = False):
        publish_time = utils.generate_publish_time(self.consignor_user_id, pre_pub=preset_publish)
        self.common_info['despatchStartTime'] = publish_time['despatchStartTime']
        self.common_info['despatchEndTime'] = publish_time['despatchEndTime']
        self.common_info['validityPeriod'] = publish_time['validityPeriod']
        self.common_info['receiptStartTime'] = publish_time['receiptStartTime']
        self.common_info['expectPeriod'] = publish_time['expectPeriod']

    def _isPaymentUser(self):
        consignor_type = utils.get_consignor_type(self.consignor_user_id)
        _isPaymentUser = consignor_type.get('BUSINESS_TYPE')
        self.common_info['isPaymentUser'] = '0'

    def _gift_insurance(self):
        gift_insurance = utils.get_consignor_gift_insurance(self.consignor_user_id)
        end_time = gift_insurance.get('GIFT_END_TIME').timestamp()
        now = datetime.datetime.now().replace(microsecond=0).timestamp()
        if end_time - now > 0:
            _giftMoney = gift_insurance.get('GIFT_MONEY') * 10000
        else:
            _giftMoney = 0
        self.common_info['giftMoney'] = str(_giftMoney)

    def _common(self, batch_publish, settle_type, preset_publish):
        self._get_user_info()
        self._batchPublishNum(batch_publish)
        self._settleBasisType(settle_type)
        self._orderPresetPublishFlag(preset_publish)
        self._publish_time(preset_publish)
        self._isPaymentUser()
        self._gift_insurance()
        self.common_info['randomToken'] = "11241842091415270FB1344259924674217981"
        self.common_info['randomCode'] = "0000"
        self.common_info['delistConsultMobile'] = ""
        self.common_info['settleConsultMobile'] = ""
        self.common_info['serviceAgreement'] = "on"
        self.common_info['selfComment'] = ""
        self.common_info['selectVehicleType'] = "不限"
        self.common_info['vehicleTypeId'] = "不限"
        self.common_info['selectCarriageLength'] = "不限"
        self.common_info['carriageLengthId'] = "不限"
        self.common_info['isUrgent'] = "0"
        self.common_info['changePolicyToCarrier'] = "0"
        self.common_info['biddngChildRadio'] = ""
        self.common_info.update(utils.get_deliver_default(self.consignor_user_id))
        self.common_info.update(utils.get_receive_default(self.consignor_user_id))
        self.common_info['deliverBackupMobile'] = ''

    def __call__(self, batch_publish: str = "1", settle_type: str = "2", preset_publish: bool = False):
        self._common(batch_publish, settle_type, preset_publish)
        return self.common_info


if __name__ == '__main__':
    common = Common('12344', '1344259924674217981')
    r = common()
    print(r)
