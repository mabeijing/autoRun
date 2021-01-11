import logging
from descriptor import (OilAttr, ReceiptAttr, CommonAttr, DesignateAttr)
from cargoType import CargoType
from casesuit import CaseSuit
from dbUtils import rds
from component import Oil, Receipt, Common, Designate

logger = logging.getLogger(__name__)


class Stage:
    """
    核心功能：组装发布数据模块
    fun:create 用来创建测试套
    """

    def __init__(self, session_id, owner):
        self.session_id = session_id
        self._consignor_user_id = owner.consignor_user_id
        self._oil = Oil(self.session_id, self._consignor_user_id)
        self._receipt = Receipt(self.session_id, self._consignor_user_id)
        self._common = Common(self.session_id, self._consignor_user_id)
        self._designate = Designate(self.session_id, self._consignor_user_id)

    oil = OilAttr()
    receipt = ReceiptAttr()
    common = CommonAttr()
    designate = DesignateAttr()

    @property
    def cargo(self):
        return CargoType(self.session_id, self._consignor_user_id)

    @property
    def create_order(self):
        """
        :param: cargo是从conn获取到的。
        :return:
        """
        cargo = rds.hget(self.session_id, 'cargo')
        return CaseSuit(cargo, self.oil, self.receipt, self.common, self.designate, self.session_id)

    @property
    def create_huge_order(self):
        return 1
