from abc import ABC
from decimal import Decimal
from typing import Union, List
import utils


class PolicyType:

    def is_over_limitation(self):
        raise NotImplementedError()

    def calculate_premium(self):
        raise NotImplementedError()

    @staticmethod
    def _filter_max_rate_cargo_list(cargo_list: List[dict]) -> List[dict]:
        """不超限货物列表中，取费率高的货物列表"""
        rate_list = []
        for _cargo in cargo_list:
            rate_list.append(_cargo['PLATE_RATE'])
        max_plate_rate = max(rate_list)

        max_plate_rate_cargo_list = []
        for _cargo in cargo_list:
            if _cargo['PLATE_RATE'] == max_plate_rate:
                max_plate_rate_cargo_list.append(_cargo)
        return max_plate_rate_cargo_list

    @staticmethod
    def _filter_max_limitation_cargo_list(cargo_list: List[dict]) -> List[dict]:
        """相同费率的货物列表，返回限额大的货物列表"""
        limitation_list = []
        for _cargo in cargo_list:
            limitation_list.append(_cargo['CARGO_VALUE_LIMITATION'])
        max_cargo_limitation = max(limitation_list)

        max_cargo_limitation_list = []
        for _cargo in cargo_list:
            if _cargo['CARGO_VALUE_LIMITATION'] == max_cargo_limitation:
                max_cargo_limitation_list.append(_cargo)
        return max_cargo_limitation_list

    def _calculate_cargo_premium(self, cargo: dict, cargoMoney: Union[float, Decimal], totalMoney: Union[float, None],
                                 weight: float, giftMoney: Union[float, None]) -> dict:
        cargo['GIFT_MONEY'] = giftMoney
        if utils.is_special_cargo(cargo['CARGO_NAME']):
            if not totalMoney:
                cargo['CALCULATE_PREMIUM'] = None
            else:
                fee = weight * cargo['PLATE_UNIT_PREMIUN'] + totalMoney * cargo['PLATE_RATE'] / 100
                premium = max(float(cargo['MIN_PREMIUN']), fee)
                if not giftMoney:
                    cargo['CALCULATE_PREMIUM'] = premium
                else:
                    """
                        1、基准保费 = n*吨位+货主运费*费率
                        2、赠保保费=（赠保货值/整车货值）* 基准保费
                        3、货值实际支付保费 = max(基准保费, 最小保费) - 赠保保费
                    """
                    if giftMoney >= cargoMoney:
                        cargo['CALCULATE_PREMIUM'] = 0.0
                    else:
                        gift = (giftMoney / float(cargoMoney)) * fee
                        actual_premium = premium - gift
                        cargo['CALCULATE_PREMIUM'] = actual_premium
        else:
            fee = cargoMoney * cargo['PLATE_RATE'] / 100
            premium = max(float(cargo['MIN_PREMIUN']), fee)
            if not giftMoney:
                cargo['CALCULATE_PREMIUM'] = premium
                cargo['GIFT_MONEY'] = 0
            else:
                """
                1、赠送保费 = 赠保货值* 费率
                2、基准保费 = 货值 * 费率
                3、实际支付保费 = max(基准保费，最小保费) - 赠送保费
                """
                if giftMoney >= cargoMoney:
                    cargo['CALCULATE_PREMIUM'] = 0.0
                else:
                    gift = giftMoney * cargo['PLATE_RATE'] / 100
                    actual_premium = premium - gift
                    cargo['CALCULATE_PREMIUM'] = actual_premium
        return cargo

    def _calculate_liability_premium(self, cargo: dict, totalMoney: Union[float, None]):
        if not totalMoney:
            cargo['CALCULATE_PREMIUM'] = None
        else:
            fee = totalMoney * cargo['PLATE_RATE'] / 100
            premium = max(float(cargo['MIN_PREMIUN']), fee)
            cargo['CALCULATE_PREMIUM'] = premium
        return cargo


class CargoPolicy(PolicyType, ABC):
    """货运险"""

    def __init__(self, cargo_list: List[str], cargoMoney: Union[float, Decimal], weight: float,
                 totalMoney: Union[float, None], giftMoney: Union[float, None]):
        self.giftMoney = giftMoney
        self.totalMoney = totalMoney
        self.weight = weight
        self.cargoMoney = cargoMoney
        self.cargo_list = cargo_list

    def _filter_normal_cargo(self):
        """剔除超限额货物"""
        normal_cargo_list = []
        for _cargo in self.cargo_list:
            cargo_meta = utils.get_cargo_insurance(_cargo)
            if self.cargoMoney < float(cargo_meta['CARGO_VALUE_LIMITATION']) * 10000.0:
                cargo_meta['CARGO_NAME'] = _cargo
                normal_cargo_list.append(cargo_meta)
        return normal_cargo_list

    def is_over_limitation(self):
        """判断是否超限额,如果超限返回dict，如果不超限，返回list"""
        normal_cargo_list = self._filter_normal_cargo()
        if not normal_cargo_list:
            cargo_meta = utils.get_cargo_insurance(self.cargo_list[0])
            return {'CARGO_VALUE_LIMITATION': float(cargo_meta['CARGO_VALUE_LIMITATION']),
                    'CARGO_VALUE_OVER_LIMIT': '1'}
        else:
            return normal_cargo_list

    def calculate_premium(self) -> dict:
        normal_cargo_list = self.is_over_limitation()
        if isinstance(normal_cargo_list, dict):
            return normal_cargo_list
        max_plate_rate_cargo_list = self._filter_max_rate_cargo_list(normal_cargo_list)
        if len(max_plate_rate_cargo_list) == 1:
            cargo_meta = max_plate_rate_cargo_list[0]
            cargo_policy = self._calculate_cargo_premium(cargo_meta, self.cargoMoney, self.totalMoney, self.weight,
                                                         self.giftMoney)
            return cargo_policy
        max_cargo_limitation_list = self._filter_max_limitation_cargo_list(max_plate_rate_cargo_list)
        cargo_meta = max_cargo_limitation_list[0]
        cargo_policy = self._calculate_cargo_premium(cargo_meta, self.cargoMoney, self.totalMoney, self.weight,
                                                     self.giftMoney)
        return cargo_policy


class LiabilityPolicy(PolicyType, ABC):
    def __init__(self, cargo_list: List[str], cargoMoney: Union[float, Decimal], weight: float,
                 totalMoney: Union[float, None]):
        self.cargo_list = cargo_list
        self.cargoMoney = cargoMoney
        self.weight = weight
        self.totalMoney = totalMoney

    def _filter_normal_cargo(self) -> list:
        # 检查是否有货物超限额
        normal_cargo_list = []
        for _cargo in self.cargo_list:
            cargo_meta = utils.get_liability_insurance(_cargo)
            if not cargo_meta:
                continue
            if self.cargoMoney >= cargo_meta['CARGO_VALUE_LIMITATION'] * 10000:
                return []
            cargo_meta['CARGO_NAME'] = _cargo
            normal_cargo_list.append(cargo_meta)
        return normal_cargo_list

    def is_over_limitation(self):
        """判断是否超限额"""
        normal_cargo_list = self._filter_normal_cargo()
        if not normal_cargo_list:
            return False
        else:
            return normal_cargo_list

    def calculate_premium(self):
        normal_cargo_list = self.is_over_limitation()
        if not normal_cargo_list:
            return False
        max_plate_rate_cargo_list = self._filter_max_rate_cargo_list(normal_cargo_list)
        if len(max_plate_rate_cargo_list) == 1:
            cargo_meta = max_plate_rate_cargo_list[0]
            cargo_policy = self._calculate_liability_premium(cargo_meta, self.totalMoney)
            return cargo_policy
        max_cargo_limitation_list = self._filter_max_limitation_cargo_list(max_plate_rate_cargo_list)
        cargo_meta = max_cargo_limitation_list[0]
        cargo_policy = self._calculate_liability_premium(cargo_meta, self.totalMoney)
        return cargo_policy


def get_insurance(havePolicy: str, cargo_list: list, cargoMoney: float, weight: float, totalMoney: Union[None, int],
                  giftMoney: Union[None, int]):
    _cargo_list = utils.check_cargo_all_special(cargo_list)
    if havePolicy == '1':
        consignor_insurance = CargoPolicy(_cargo_list, cargoMoney, weight, totalMoney, giftMoney)
        return consignor_insurance.calculate_premium()
    else:
        cargo_insurance = CargoPolicy(_cargo_list, cargoMoney, weight, totalMoney, None)
        liability_insurance = LiabilityPolicy(_cargo_list, cargoMoney, weight, totalMoney)
        liability_insurance_over_limitation = liability_insurance.is_over_limitation()
        cargo_insurance_over_limitation = cargo_insurance.is_over_limitation()
        if not liability_insurance_over_limitation:
            return cargo_insurance.calculate_premium()
        elif cargo_insurance_over_limitation.get('cargoValueOverLimit', '0') == '1':
            return liability_insurance.calculate_premium()
        if liability_insurance.calculate_premium().get('CALCULATE_PREMIUM') >= cargo_insurance.calculate_premium().get(
                'CALCULATE_PREMIUM'):
            return cargo_insurance.calculate_premium()


if __name__ == '__main__':
    policy = get_insurance('1', ['无烟煤', '工字钢'], 10000, 10, 1000, None)
    print(policy)
