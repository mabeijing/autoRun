import config


class InsuranceBuyType:
    def __init__(self, cargo=None, cargoMoney=None, carrierMoney=None, giftMoney=None, buyType=None):
        self.cargo = cargo
        self.cargoMoney = cargoMoney
        self.carrierMoney = carrierMoney
        self.giftMoney = giftMoney
        self.buyType = buyType

    @staticmethod
    def _check_special_cargo(cargo_name):
        """根据config写入"""
        if cargo_name in config.SPECIAL_CARGO:
            return True
        else:
            return False

    def _check_over_limitation_cargo(self, cargo_name):
        insurance = query_insurance_info(cargo_name)
        if insurance.Limitation <= self.cargoMoney:
            return False
        else:
            return True

    @staticmethod
    def _check_max_limitation_cargo(cargo_list):
        max_cargo_list = []
        max_limitation = max([cargo.limitation for cargo in cargo_list])
        for cargo in cargo_list:
            if cargo.limitation == max_limitation:
                max_cargo_list.append(cargo)
        return max_cargo_list

    @staticmethod
    def _check_max_rate_cargo(cargo_list):
        max_cargo_list = []
        max_rate = max([cargo.rate for cargo in cargo_list])
        for cargo in cargo_list:
            if cargo.limitation == max_rate:
                max_cargo_list.append(cargo)
        return max_cargo_list

    def transport_insurance(self):
        """转嫁保险"""
        pass

    def carrier_insurance(self):
        """承运人保险"""
        pass

    def consignor_insurance(self):
        """自主保险"""
        # 再次根据cargo货物保险配置信息
        # 判断是否超限额
        # 计算对应的保费
        insurance = {}
        if len(self.cargo) > 1:
            """删除正常货物里面的特殊货物"""
            flag_list = [InsuranceBuyType._check_special_cargo(c) for c in self.cargo]
            if len(set(flag_list)) > 1:
                for cargo in self.cargo:
                    if InsuranceBuyType._check_special_cargo(cargo):
                        self.cargo.pop(cargo)
        if len(self.cargo) > 1:
            """删除超限额货物列表"""
            for cargo in self.cargo:
                if self._check_over_limitation_cargo(cargo):
                    self.cargo.pop(cargo)

        if len(self.cargo) > 1:
            """筛选最大费率货物列表"""
            self.cargo = InsuranceBuyType._check_max_rate_cargo(self.cargo)

        if len(self.cargo) > 1:
            """筛选最大限额的货物列表"""
            self.cargo = InsuranceBuyType._check_max_limitation_cargo(self.cargo)

        if len(self.cargo) > 1:
            """所有条件都一致，取第一个货物"""
            self.cargo = self.cargo[0]
            
        if len(self.cargo) == 1:
            policy = _get_policy_info(self.cargo)
        insurance['overLimitation'] = False
        insurance['cargoName'] = self.cargo.get('BASE_NAME')
        insurance['policyMoney'] = self.cargoMoney * policy.cargo_insurance.rate



    def no_insurance(self):
        """不买保险"""
        pass

    def __call__(self, *args, **kwargs):
        if self.buyType == 1:
            return self.consignor_insurance()
        if self.buyType == 2:
            return self.transport_insurance()
        if self.buyType == 0:
            return self.no_insurance()
        if self.buyType == 4:
            return self.carrier_insurance()
        pass


class InsuranceType:
    def __init__(self):
        pass

    def cargo_insurance(self):
        """货运险"""
        pass

    def liability_insurance(self):
        """责任险"""
        pass
