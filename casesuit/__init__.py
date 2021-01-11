import random
from dbUtils import rds
from insurance import get_insurance


class CaseSuit:
    """
    测试套：根据Stage组装提供的数据，写对应的发布场景
    """

    def __init__(self, cargo: dict, oil: dict, receipt: dict, common: dict, designate: dict, session_id):
        self.session_id = session_id
        self._oil = oil
        self._cargo = cargo
        self._receipt = receipt
        self._common = common
        self._designate = designate
        self.blockMoney = float(0)

    def _order_publish_type(self, mode: str = 'publish'):
        if mode == 'publish':
            publish_param = {
                "operation": "publish",
                "orderId": ""
            }
        elif mode == 'republish':
            publish_param = {
                "operation": "republish",
                "orderId": "102012241652234951",
                "oldGiftMoney": "",
            }
        elif mode == 'editpublish':
            publish_param = {
                "operation": "editpublish",
                "orderId": "102012241652234951",
                "oldGiftMoney": "",
            }
        else:
            raise ValueError('mode参数只能在[publish, republish, editpublish]')
        publish_param.update(self._cargo)
        publish_param.update(self._oil)
        publish_param.update(self._common)
        publish_param.update(self._designate)
        publish_param.update(self._receipt)
        return publish_param

    def snatch_order_consignor_insurance(self, mode: str = 'publish', freight_type: int = 1, user_quote: float = None,
                                         user_cargoMoney: float = None):
        """
        :param freight_type:
        :param mode:
        :param user_quote:
        :param user_cargoMoney:
        :return:
        普通货-抢单-自主保险：保险在发布节点确认。创建stage时将保险写入redis
        """
        publish_param = self._order_publish_type(mode)

        _cargoMoney = random.randint(5000, 15000)
        _quote = round(random.triangular(100, 200, 100), 3)
        _cargoCategory = self._cargo.get('cargoCategory', None)[0]

        if _cargoCategory == '1':
            _orderWeight = self._cargo.get('orderWeight', None)
            if _orderWeight:
                total_weight = float(sum(_orderWeight))
            else:
                raise ValueError("未获取到货物的计量")
        elif _cargoCategory == '2':
            _orderVolume = self._cargo.get('orderVolume', None)
            if _orderVolume:
                total_weight = float(sum(_orderVolume))
            else:
                raise ValueError('未获取到货物的计量')
        else:
            raise ValueError('未获取到货物的cargoCategory')
        cargoMoney = _cargoMoney if not user_cargoMoney else user_cargoMoney

        quote = _quote if not user_quote else user_quote
        if freight_type == 1:
            _allMoney = round(quote * total_weight, 3)
        elif freight_type == 2:
            _allMoney = quote
        else:
            raise ValueError('freight_type只能时1或者2')

        _insurance_param = {
            "havePolicy": "1",
            "cargo_list": self._cargo.get('orderName'),
            "cargoMoney": cargoMoney,
            "weight": total_weight,
            "totalMoney": str(_allMoney / 1.06382978),
            "giftMoney": float(self._common.get('giftMoney'))
        }
        insurance = get_insurance(**_insurance_param)

        order_type = {
            "orderModel": "0",
            "freightType": str(freight_type),
            "chooseRadio": "1",
            "havePolicy": "1",
            "orderMark": "",
            "cargoMoney": str(cargoMoney),
            "weight": str(total_weight),
            "quote": str(quote),
            "consignorNoTaxMoney": str(quote / 1.06382978),
            "allMoney": str(_allMoney),
            "cargoValueLimitation": float(insurance.get('CARGO_VALUE_LIMITATION')),
            "cargoValueOverLimit": insurance.get('CARGO_VALUE_OVER_LIMIT', '0'),
            "blockMoney": str(self.blockMoney),
            "prompt": "普通货-抢单-单价-自主保险"
        }
        publish_param.update(order_type)
        rds.hset(self.session_id, 'insurance', str(insurance))
        rds.hset(self.session_id, 'publish_param', str(publish_param))
        return publish_param

    def bidding_order_consignor_insurance(self, mode: str = 'publish', freight_type: int = 1,
                                          user_cargoMoney: float = None):
        """
        :param freight_type:
        :param mode:
        :param user_cargoMoney:
        :return:
        普通货-竞价-自主保险：保险根据货物类型确认。创建stage时将保险写入redis
        """
        publish_param = self._order_publish_type(mode)
        _cargoMoney = random.randint(5000, 15000)

        _cargoCategory = self._cargo.get('cargoCategory', None)[0]
        if _cargoCategory == '1':
            _orderWeight = self._cargo.get('orderWeight', None)
            if _orderWeight:
                total_weight = float(sum(_orderWeight))
            else:
                raise ValueError("未获取到货物的计量")
        elif _cargoCategory == '2':
            _orderVolume = self._cargo.get('orderVolume', None)
            if _orderVolume:
                total_weight = float(sum(_orderVolume))
            else:
                raise ValueError('未获取到货物的计量')
        else:
            raise ValueError('未获取到货物的cargoCategory')
        cargoMoney = _cargoMoney if not user_cargoMoney else user_cargoMoney

        _insurance_param = {
            "havePolicy": "1",
            "cargo_list": self._cargo.get('orderName'),
            "cargoMoney": cargoMoney,
            "weight": total_weight,
            "totalMoney": "",
            "giftMoney": float(self._common.get('giftMoney'))
        }
        insurance = get_insurance(**_insurance_param)

        order_type = {
            "orderModel": "1",
            "freightType": str(freight_type),
            "chooseRadio": "1",
            "havePolicy": "1",
            "orderMark": "",
            "cargoMoney": str(cargoMoney),
            "weight": str(total_weight),
            "quote": "",
            "consignorNoTaxMoney": "",
            "allMoney": "",
            "cargoValueLimitation": float(insurance.get('CARGO_VALUE_LIMITATION')),
            "cargoValueOverLimit": insurance.get('CARGO_VALUE_OVER_LIMIT', '0'),
            "blockMoney": "300.001",
            "prompt": "普通货-抢单-包车价-自主保险"
        }
        publish_param.update(order_type)
        rds.hset(self.session_id, 'insurance', str(insurance))
        rds.hset(self.session_id, 'publish_param', str(publish_param))
        return publish_param
