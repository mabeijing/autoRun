import json
import utils
import logging

logger = logging.getLogger(__name__)


class Oil:
    """
    1、不支持油品 无参数
    2、可选油品
    oilCalculateType
        1：比例油。
        2：固额油(需要货主配置项开通支持固额油品)
            oilFixedCredit 100
            gasFixedCredit 100
            selectOilPercent = oilPercentSelect
            selectGasPercent = gasPercentSelect
    haveSupportSdOilCard 发布是否选择油品
        0：否
        oilPercentSelect 30(货主配置项)
        selectOilPercent ""
        gasPercentSelect 请选择(货主配置项缺省值) 如果配置，则显示值
        selectGasPercent ""
        oilFixedCredit ""
        gasFixedCredit ""
        1：是
        selectOilPercent 修改值。缺省货主配置项
        selectOilPercent 修改值。缺省货主配置项
        gasPercentSelect 修改值，缺省货值配置项，货值配置项缺省显示请选择
        selectGasPercent 修改值，缺省货值配置项，货值配置项缺省显示请选择
        oilFixedCredit ""
        gasFixedCredit ""

    3、强制油
        haveSupportSdOilCard 无该字段

    货主配置项
    56  0：不支持油品，1：可选油品， 2：强制油品默认比例35%
    98  固额油品
        {"fixedQuotaSwitching":"1","fixedQuotaMoney":"100"}
        {"fixedQuotaSwitching":"0","fixedQuotaMoney":""}
    57  油品比例
    128 气品比例

    测试默认[不支持油品。不支持固额油品。油品比例30，气品比例10]
    """

    def __init__(self, session_id, consignor_user_id):
        self.user_id = consignor_user_id
        self.session_id = session_id
        self.oil_info = {}
        self._oil_type = []

    def __support_fixed_oil(self, fixed_oil_flag: bool = False):
        """是否选择固额油品"""
        if fixed_oil_flag:
            self._oil_type.append('选择固额油')
            # 修改货主配置项，未实现
            _config_data = utils.get_consignor_config(self.user_id, 98).get('VALUE')
            fixed_oil_info = json.loads(_config_data)
            if not fixed_oil_info:
                raise ValueError('货主配置项不支持固额油品')
            elif fixed_oil_info.get('fixedQuotaSwitching', '') == '1':
                self.oil_info['oilCalculateType'] = '2'
                self.oil_info['oilFixedCredit'] = fixed_oil_info.get('fixedQuotaMoney')
                self.oil_info['gasFixedCredit'] = self.oil_info['oilFixedCredit']
            else:
                self._oil_type.append('选择比例油')
                self.oil_info['oilCalculateType'] = '1'
                self.oil_info['oilFixedCredit'] = ''
                self.oil_info['gasFixedCredit'] = ''
        else:
            self._oil_type.append('选择比例油')
            self.oil_info['oilCalculateType'] = '1'
            self.oil_info['oilFixedCredit'] = ''
            self.oil_info['gasFixedCredit'] = ''

    def _choose_oil_type(self, support_oil: bool, support_fixed_oil: bool, oil_ratio, gas_ratio):
        # 读取货值配置项，56，57，98，128。油品配置
        _oil = utils.get_consignor_config(self.user_id, 56)
        sys_oil_ratio_optional = utils.get_sys_dict(566).get('VALUE')  # 系统可选油品比例
        sys_oil_ratio_force = utils.get_sys_dict(567).get('VALUE')  # 系统强制油品比例
        _oil_ratio = utils.get_consignor_config(self.user_id, 57).get('VALUE')
        _gas_ratio = utils.get_consignor_config(self.user_id, 128).get('VALUE')
        oil_ratio = oil_ratio if oil_ratio else _oil_ratio
        gas_ratio = gas_ratio if gas_ratio else _gas_ratio

        if _oil.get('VALUE', '') == '0':
            self._oil_type.append('不支持油品')
        elif _oil.get('VALUE', '') == '1':
            self._oil_type.append('可选油品')
            self.oil_info['oilPercentSelect'] = oil_ratio if oil_ratio else sys_oil_ratio_optional
            self.oil_info['gasPercentSelect'] = gas_ratio if gas_ratio else '请选择'
            if support_oil:
                self._oil_type.append('发布支持油品')
                self.oil_info['haveSupportSdOilCard'] = '1'
                self.oil_info['selectOilPercent'] = self.oil_info['oilPercentSelect']
                self.oil_info['selectGasPercent'] = self.oil_info['gasPercentSelect']
                self.__support_fixed_oil(support_fixed_oil)
            else:
                self._oil_type.append('发布不支持油品')
                self.oil_info['haveSupportSdOilCard'] = '0'
                # self.oil_info['oilCalculateType'] = ''
                self.oil_info['selectOilPercent'] = ''
                self.oil_info['selectGasPercent'] = ''
                self.oil_info['oilFixedCredit'] = ''
                self.oil_info['gasFixedCredit'] = ''

        elif _oil.get('VALUE', '') == '2':
            self._oil_type.append('强制油品')
            self.oil_info['oilPercentSelect'] = oil_ratio if oil_ratio else sys_oil_ratio_force
            self.oil_info['gasPercentSelect'] = gas_ratio if gas_ratio else '请选择'
            self.oil_info['selectOilPercent'] = self.oil_info['oilPercentSelect']
            self.oil_info['selectGasPercent'] = self.oil_info['gasPercentSelect']
            self.__support_fixed_oil(support_fixed_oil)
        else:
            raise ValueError('错误参数')

    def __call__(self, support_oil=False, support_fixed_oil=False, oil_ratio=None, gas_ratio=None):
        self._choose_oil_type(support_oil, support_fixed_oil, oil_ratio, gas_ratio)
        return self.oil_info


if __name__ == '__main__':
    oil = Oil(session_id='123', consignor_user_id=1344259924674217981)

    print(oil(support_oil=True, gas_ratio=22))
    print(oil._oil_type)
