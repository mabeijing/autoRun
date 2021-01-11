import json
import random
from DBUtils import redis_connect
import config

conn = redis_connect


class CargoOrder:
    """
    货物属性类，实现类货物运单属性
    """

    def __init__(self, session_id):
        """
        :param session_id: 全局唯一session标识符
        """
        self.session = session_id
        self._cargo = json.loads(conn.hget(self.session, 'cargo'))
        self._cargoCategory = random.choice(['0', '1'])
        if len(self._cargo.get('orderName')) > 1:
            self._orderWeight = [round(random.triangular(5, 20, 10), 3) for i in
                                 range(config.GLOBAL_MULTI_CARGO_NUMBER)]
        else:
            self._orderWeight = [round(random.triangular(5, 20, 10), 3)]

    def _len(self) -> int:
        """获取运单货物总数"""
        cargo_name = self._cargo.get('orderName')
        if not cargo_name:
            raise RuntimeError('请优先设置cargoType')
        return len(cargo_name)

    @property
    def extra_cargo_info(self):
        n = self._len()
        extra_info = {}
        extra_info['selectOrderPacking'] = ['无' for i in range(n)]
        extra_info['orderPacking'] = ['130' for i in range(n)]
        extra_info['cargoVersion'] = ['规格型号' for i in range(n)]
        extra_info['warehouseName'] = ['仓库名称' for i in range(n)]
        extra_info['warehouseLocation'] = ['仓库位置' for i in range(n)]
        extra_info['unitFreight'] = ['' for i in range(n)]
        extra_info['orderLong'] = ['7' for i in range(n)]
        extra_info['orderWidth'] = ['2' for i in range(n)]
        extra_info['orderHigh'] = ['4' for i in range(n)]
        return extra_info

    @property
    def cargoCategory(self):
        n = self._len()
        return [self._cargoCategory for i in range(n)]

    @cargoCategory.setter
    def cargoCategory(self, new_cargoCategory: int):
        if new_cargoCategory not in [0, 1]:
            raise ValueError('cargoCategory只能是0或者1整数')
        self._cargoCategory = new_cargoCategory

    @property
    def orderWeight(self):
        return self._orderWeight

    @orderWeight.setter
    def orderWeight(self, new_orderWeight: list):
        self._orderWeight = new_orderWeight

    def __call__(self):
        extra_info = self.extra_cargo_info
        cargo_info = {
            "orderName": [self._cargo.get('BASE_NAME')],
            "orderNameId": [self._cargo.get('ID')],
            "auditFlag": [self._cargo.get('STATE')],
            "cargoCategory": self.cargoCategory,
            "orderWeight": self.orderWeight,
            "orderVolume": self.orderWeight,
        }

        cargo_info.update(extra_info)
        return cargo_info
