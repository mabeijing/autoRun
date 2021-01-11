import json
import random
from dbUtils import rds
import config


class CargoOrder:
    """
    货物属性类，实现类货物运单属性
    """

    def __init__(self, session_id):
        """
        :param session_id: 全局唯一session标识符
        """
        self.session = session_id
        self._cargo = json.loads(rds.hget(self.session, 'cargo'))
        self._cargoCategory = random.choice(['0', '1'])
        if len(self._cargo.get('orderName')) > 1:
            self._orderWeight = [round(random.triangular(5, 20, 10), 3) for _ in
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
        extra_info = {'selectOrderPacking': ['无' for _ in range(n)],
                      'orderPacking': ['130' for _ in range(n)],
                      'cargoVersion': ['规格型号' for _ in range(n)],
                      'warehouseName': ['仓库名称' for _ in range(n)],
                      'warehouseLocation': ['仓库位置' for _ in range(n)],
                      'unitFreight': ['' for _ in range(n)],
                      'orderLong': ['7' for _ in range(n)],
                      'orderWidth': ['2' for _ in range(n)],
                      'orderHigh': ['4' for _ in range(n)]}
        return extra_info

    @property
    def cargoCategory(self):
        n = self._len()
        return [self._cargoCategory for _ in range(n)]

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
