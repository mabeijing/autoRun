import json
import random
from typing import Union
from dbUtils import rds
import utils
import config


class CargoType:
    def __init__(self, session_id, consignor_user_id):
        self.session_id = session_id
        self.consignor_user_id = consignor_user_id
        self._cargo_list = utils.get_consignor_cargo_list(consignor_user_id)

    def _get_cargo_status_by_name(self, cargo_name: str) -> dict:
        for _cargo in self._cargo_list:
            if cargo_name == _cargo.get('BASE_NAME'):
                return _cargo
        else:
            raise ValueError('货物没有这个货物')

    @staticmethod
    def _insurance_calculate(cargo_list: list):
        insurance_calculate = {}
        insurance = {}
        for _cargo in cargo_list:
            insurance['cargo_insurance'] = utils.get_cargo_insurance(_cargo)
            insurance[
                'transport_insurance'] = utils.get_liability_insurance(_cargo)
            insurance_calculate[_cargo] = insurance
        return insurance_calculate

    def random_common_cargo(self, user_cargo: list = None, user_weight: list = None):
        # 随机正常货物
        _user_cargo_list = ['矿渣粉', '无烟煤'] if not user_cargo else user_cargo
        cargo_select = random.choice(_user_cargo_list)
        _cargo_select_list = [cargo_select]
        _cargo = self._get_cargo_status_by_name(cargo_select)
        if _cargo['STATE'] != '1':
            raise ValueError('货物未审核通过')
        cargo_list = [_cargo]
        insurance = self._insurance_calculate(_cargo_select_list)
        if not insurance[cargo_select]['cargo_insurance']:
            raise ValueError('货物为不保货物')
        if not insurance[cargo_select]['transport_insurance']:
            raise ValueError('货物为单一险种货物')
        cargo_info = utils.cargo_publish_info(cargo_list, user_weight)
        rds.hset(self.session_id, 'cargo', json.dumps(cargo_info, ensure_ascii=False))
        return cargo_info

    def special_cargo_with_insurance(self, user_cargo: list = None, user_weight: list = None):
        # 随机正常货物
        _user_cargo_list = ['工字钢'] if not user_cargo else user_cargo
        cargo_select = random.choice(_user_cargo_list)
        _cargo_select_list = [cargo_select]
        _cargo = self._get_cargo_status_by_name(cargo_select)
        if _cargo['STATE'] != '1':
            raise ValueError('货物未审核通过')
        cargo_list = [_cargo]
        insurance = self._insurance_calculate(_cargo_select_list)
        if not insurance[cargo_select]['cargo_insurance']:
            raise ValueError('货物为不保货物')
        if not insurance[cargo_select]['transport_insurance']:
            raise ValueError('货物为单一险种货物')
        cargo_info = utils.cargo_publish_info(cargo_list, user_weight)
        rds.hset(self.session_id, 'cargo', json.dumps(cargo_info, ensure_ascii=False))
        return cargo_info

    def special_cargo_no_insurance(self, user_cargo=None, user_weight=None):
        # 不保货物
        cargo_list = ['锑锭'] if not user_cargo else user_cargo
        _cargo = random.choice(cargo_list)
        print(_cargo)
        cargo_info = self._get_cargo_status_by_name(_cargo)
        if cargo_info['STATE'] != '1':
            raise ValueError('货物未审核通过')
        cargo_insurance = utils.get_cargo_insurance(_cargo)
        if cargo_insurance:
            raise ValueError('该货物非不保货物')
        cargo_insurance_info_dict = self._handle_category_insurance(
            cargo_insurance)
        cargo_info.update(cargo_insurance_info_dict)
        return cargo_info

    def special_cargo_single_type(self):
        # 单险种货物。只有货运险
        cargo_list = ['笔记本电脑']
        _cargo = random.choice(cargo_list)
        print(_cargo)
        cargo_info = self._get_cargo_status_by_name(_cargo)
        if cargo_info['STATE'] != '1':
            raise ValueError('货物未审核通过')
        cargo_insurance = utils.get_cargo_insurance(_cargo)
        if len(cargo_insurance) != 1:
            raise ValueError('该货物非单货运险货物。')
        if cargo_insurance[0]['INSURANCE_TYPE'] != 1:
            raise ValueError('该货物保险属性错误')
        cargo_insurance_info_dict = self._handle_category_insurance(
            cargo_insurance)
        cargo_info.update(cargo_insurance_info_dict)
        return cargo_info

    def special_cargo_in_examine(self, user_cargo=None):
        # 审核中货物
        cargo_list = ['银矿石'] if not user_cargo else user_cargo
        _cargo = random.choice(cargo_list)
        print(_cargo)
        cargo_info = self._get_cargo_status_by_name(_cargo)
        if cargo_info['STATE'] != '3':
            raise ValueError('货物状态不是审核中')
        cargo_insurance = utils.get_cargo_insurance(_cargo)
        if cargo_insurance != '货物审核中':
            raise ValueError('审核中货物不应该有保险信息')
        cargo_insurance_info_dict = self._handle_category_insurance(
            cargo_insurance)
        cargo_info.update(cargo_insurance_info_dict)
        return cargo_info

    def special_cargo_over_limitation(self, user_cargo=None):
        # 超限额保险货物
        cargo_list = ['化妆品'] if not user_cargo else user_cargo
        _cargo = random.choice(cargo_list)
        print(_cargo)
        cargo_info = self._get_cargo_status_by_name(_cargo)
        if cargo_info['STATE'] != '1':
            raise ValueError('货物未审核通过')
        cargo_insurance = utils.get_cargo_insurance(_cargo)
        if len(cargo_insurance) != 2:
            raise ValueError('货物支持保险数量错误')
        for item in cargo_insurance:
            if item['COMPANY_ID'] != 7:
                insurance_type = '货运险' if item[
                                              'INSURANCE_TYPE'] == 1 else '责任险'
                msg = cargo + '的' + insurance_type + '不是<中国平安保险股份有限公司>'
                raise ValueError(msg)
        cargo_insurance_info_dict = {'cargo_insurance_info': cargo_insurance}
        cargo_info.update(cargo_insurance_info_dict)
        return cargo_info

    def multi_cargo(self, user_cargo=None, user_weight=None):
        # 多货物随机组合
        _user_cargo_list = ['矿渣粉', '无烟煤', '笔记本电脑'] if not user_cargo else user_cargo
        _cargo_list = random.sample(_user_cargo_list, config.MULTI_CARGO_NUMBER)
        cargo_list = []
        for c in _cargo_list:
            _cargo = self._get_cargo_status_by_name(c)
            cargo_list.append(_cargo)
        cargo_info = utils.cargo_publish_info(cargo_list, user_weight)
        rds.hset(self.session_id, 'cargo', json.dumps(cargo_info, ensure_ascii=False))
        return cargo_info


if __name__ == '__main__':
    from decimal import Decimal
    cargo = CargoType('12345', '1344259924674217981')
    # data = _cargo.check_consignor_cargo()
    print(cargo.random_common_cargo())
    # print(cargo.special_cargo_single_type())
    # print(cargo.special_cargo_in_examine())
    # print(cargo.special_cargo_over_limitation())
    # print(cargo.special_cargo_no_insurance())
    # print(cargo._query_cargo_insurance_info('矿渣粉'))
    # print(cargo._check_insurance_company_config_correct())
    # print(data)
    # print(cargo.multi_cargo())
    r = rds.hget('e754c9f0-4bf3-11eb-9087-acde48001122', 'insurance')
    print(type(r))
    print(r)