import json
import random
import pymysql
import datetime
from typing import Union, Dict, List
from dbUtils import mms_db, oms_db, ams_db

"""
0、get_user_by_user_id(user_id) -> 根据用户的user_id 获取会员信息
1、get_user_by_serial_number(serial_number) -> 根据手机号 获取会员信息
2、get_classify_id(cargo_name) -> 根据货物name 返回货物的classify_id
3、get_classify_info_by_classify_id(classify_id) -> 根据货物classify_id 返回货物分类信息
4、get_consignor_cargo_list(user_id) -> 根据货主user_id 返回货主添加的货物列表
5、get_cargo_insurance(cargo_name) -> 根据货物name 返回货物的货运险配置信息
6、get_transport_insurance(cargo_name) -> 根据货物name 返回货物责任险配置信息
7、get_insurance_company_config_correct() -> 货物当前系统所有保险公司信息，前置脚本使用
8、get_receipt_default(consignor_user_id) -> 根据货物user_id 返回货主的回单快递信息
9、get_deliver_default(user_id) -> 根据当前货主的user_id 返回默认发货信息
10、get_receive_default(user_id) -> 根据当前货主的user_id 返回默认收货信息
11、get_pre_order_config(user_id) -> 根据当前货主的user_id 返回货主配置项预挂配置
12、get_consignor_type(user_id) -> 根据当前货主的user_id 返回货主账户主体类型
13、get_consignor_gift_insurance(user_id) -> 根据当前货主的user_id 返回货主赠报信息
14、get_consignor_config(user_id, config_type) -> 根据货主的user_id和config_type，获取货值配置项
15、get_sys_dict(config_type) -> 根据config_type 返回字典表配置
16、generate_publish_time(consignor_user_id, pre_pub) -> 根据货主user_id 返回发布时间
17、is_special_cargo(cargo_name:str) -> 根据货物名字 返回True或者False
18、cargo_publish_info(cargo_list, weight_list) -> 根据需要发布的货物列表，和货物质量 返回货物发布信息
"""


def cargo_publish_info(cargo_list: list, weight_list: list = None) -> dict:
    cargo_meta = {}
    n = len(cargo_list)
    if n == 0:
        raise ValueError("请表传空的cargo_list")
    _category = random.choice(['1', '2'])
    _weight = [round(random.triangular(5, 20, 10), 3) for i in range(n)]
    _other = ['' for i in range(n)]
    _selectOrderPacking = ['无' for i in range(n)]
    _orderPacking = ['130' for i in range(n)]
    _order_name = [_cargo.get('BASE_NAME') for _cargo in cargo_list]
    _orderNameId = [str(_cargo.get('ID')) for _cargo in cargo_list]
    _cargoCategory = [_category for i in range(n)]
    _auditFlag = [_cargo.get('STATE') for _cargo in cargo_list]

    if weight_list and len(weight_list) != n:
        raise ValueError('weight_list元素个数必须等于cargo_list货物个数')
    weight = weight_list if weight_list else _weight
    _orderLong = ['7' for i in range(n)]
    _orderWidth = ['2' for i in range(n)]
    _orderHigh = ['4' for i in range(n)]

    cargo_meta['orderName'] = _order_name
    cargo_meta['orderNameId'] = _orderNameId
    cargo_meta['auditFlag'] = _auditFlag
    cargo_meta['cargoVersion'] = _other
    cargo_meta['cargoCategory'] = _cargoCategory
    cargo_meta['orderVolume'] = weight
    cargo_meta['orderWeight'] = weight
    cargo_meta['warehouseName'] = _other
    cargo_meta['selectOrderPacking'] = _selectOrderPacking
    cargo_meta['orderPacking'] = _orderPacking
    cargo_meta['warehouseLocation'] = _other
    cargo_meta['unitFreight'] = _other
    cargo_meta['orderLong'] = _orderLong
    cargo_meta['orderWidth'] = _orderWidth
    cargo_meta['orderHigh'] = _orderHigh
    return cargo_meta


def check_cargo_all_special(cargo_list: List[str]) -> list:
    """判断货物是否特殊货物，如果部分特殊货物，则剔除。如果全部正常货物或者特殊货物，不处理。"""
    special_cargo = {}
    for cargo in cargo_list:
        if is_special_cargo(cargo):
            special_cargo[cargo] = True
        else:
            special_cargo[cargo] = False
    if len(set(special_cargo.values())) == 1:
        """全部是正常货物或者全部是特殊货物"""
        return cargo_list
    else:
        """剔除部分特殊货物"""
        cut_cargo_list = []
        for key, value in special_cargo.items():
            if not value:
                cut_cargo_list.append(key)
        return cut_cargo_list


def is_special_cargo(cargo_name: str) -> bool:
    cursor = oms_db.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT `VALUE` FROM mms_db.td_s_dict WHERE DICT_CODE = 'SHOW_SPECIAL_RATE';"
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    raw_data = eval(data['VALUE'])
    dict_classify = {}
    if raw_data.get(1, None):
        dict_classify['LAYER1_ID'] = raw_data.get(1)
    if raw_data.get(2, None):
        dict_classify['LAYER2_ID'] = raw_data.get(2)
    if raw_data.get(3, None):
        dict_classify['LAYER3_ID'] = raw_data.get(3)
    classify_id = get_classify_id(cargo_name)
    classify = get_classify_info_by_classify_id(classify_id)
    cargo_classify = {
        'LAYER1_ID': classify['LAYER1_NAME'],
        'LAYER2_ID': classify['LAYER2_NAME'],
        'LAYER3_ID': classify['LAYER3_NAME']
    }
    for key, value in dict_classify.items():
        if cargo_classify.get(key) in value:
            return True
    return False


def generate_publish_time(consignor_user_id, pre_pub=False, delta_days=15):
    """
    :param consignor_user_id: 货主user_id
    :param pre_pub: 是否预挂，默认不预挂
    :param delta_days: 开始装货到结束装货，默认15天
    :return:
    开始装货时间 = 当前时间 + 预挂时间
    结束装货时间 = 开始装货时间 + 15天
    运单有效期 = 结束装货时间 - 1小时
    报价有效期 = 运单有效期 - 1小时
    收货时间 = 结束装货时间 + 1天
    """
    config = get_pre_order_config(consignor_user_id)
    t = config.get('pendOrderTime', None)
    hour = int(t) if t else 24
    time_fmt = '%Y-%m-%d %H:%M'
    now = datetime.datetime.now()
    if not pre_pub:
        delta = datetime.timedelta(hours=hour, minutes=-10)
    else:
        delta = datetime.timedelta(hours=hour, minutes=10)
    delta_end = delta + datetime.timedelta(days=delta_days)
    delta_receipt = delta_end + datetime.timedelta(days=1)
    delta_valid_order = delta_end + datetime.timedelta(hours=-1)
    delta_valid_expect = delta_valid_order + datetime.timedelta(hours=-1)

    time_info = {
        "despatchStartTime": (now + delta).strftime(time_fmt),
        "despatchEndTime": (now + delta_end).strftime(time_fmt),
        "validityPeriod": (now + delta_valid_order).strftime(time_fmt),
        "receiptStartTime": (now + delta_receipt).strftime(time_fmt),
        "expectPeriod": (now + delta_valid_expect).strftime(time_fmt),
    }
    return time_info


def get_sys_dict(config_type: int) -> dict:
    cursor = mms_db.cursor(pymysql.cursors.DictCursor)
    # 582, 1137898764612157433, 583, 584, 566, 567
    sql = ('SELECT `VALUE` '
           'FROM mms_db.td_s_dict '
           'WHERE ID={id};').format(id=config_type)
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    return data


def get_consignor_config(user_id, config_type: int or str) -> dict:
    cursor = mms_db.cursor(pymysql.cursors.DictCursor)
    # 56，57，98，128
    sql = ('SELECT `VALUE` '
           'FROM mms_db.tf_f_consignor_config '
           'WHERE USER_ID={user_id} '
           'AND CONFIG_TYPE={config_type};').format(user_id=user_id, config_type=config_type)
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    return data


def get_consignor_gift_insurance(user_id):
    """获取货主赠保信息"""
    user = get_user_by_user_id(user_id=user_id)
    customer_id = user.get('CUSTOMER_ID', None)
    cursor = ams_db.cursor(pymysql.cursors.DictCursor)
    sql = ('SELECT '
           'COMPANY_NAME,'
           'GIFT_START_TIME,'
           'GIFT_END_TIME,'
           'GIFT_MONEY '
           'FROM ams_db.tf_f_old_policy_customer '
           'WHERE CUSTOMER_ID ={customer_id} '
           'AND DELETE_FLAG=0;').format(customer_id=customer_id)
    cursor.execute(sql)
    gift_insurance = cursor.fetchone()
    cursor.close()
    return gift_insurance


def get_consignor_type(user_id):
    """获取货主的交易类型：现结/账期"""
    cursor = mms_db.cursor(pymysql.cursors.DictCursor)
    sql = ('SELECT '
           '`BUSINESS_TYPE`,'
           '`SETTLE_METHOD`,'
           '`STATUS`,'
           '`UP_SETTLE_PART_NAME`,'
           '`DOWN_SETTLE_PART_NAME`,'
           '`DELETE_FLAG` '
           'FROM mms_db.td_b_account_subject_config '
           'WHERE USER_ID = {user_id} '
           'AND STATUS = 1;').format(user_id=user_id)
    cursor.execute(sql)
    consignor_type = cursor.fetchone()
    cursor.close()
    return consignor_type


def get_pre_order_config(user_id):
    """查询货主预挂配置"""
    cursor = mms_db.cursor()
    sql = ('SELECT '
           '`VALUE` '
           'FROM mms_db.tf_f_consignor_config '
           'WHERE USER_ID = {user_id} '
           'AND config_type = 94 '
           'AND DELETE_FLAG=0;').format(user_id=user_id)
    cursor.execute(sql)
    data = cursor.fetchone()
    if not data:
        raise ValueError('数据库返回None，检查user_id')
    order_config = json.loads(data[0])
    cursor.close()
    return order_config


def get_receive_default(user_id):
    """获取收货信息"""
    cursor = oms_db.cursor(pymysql.cursors.DictCursor)
    sql = ('SELECT '
           '`CONS_COMPANY_NAME` as deliverCompanyName,'
           '`ID` as deliverId,'
           '`CONS_COORDINATE_X` as deliverCoordinateX,'
           '`CONS_COORDINATE_Y` as deliverCoordinateY,'
           '`CONS_NAME` as deliverName,'
           '`CONS_NAME` as deliverInfo, '
           '`CONS_PROVINCE` as deliverprovince,'
           '`CONS_CITY` as delivercity,'
           '`CONS_AREA` as deliverarea,'
           '`CONS_DETAIL_ADDR` as deliverAddress,'
           '`CONS_LOCATION_ADDR` as deliverPlaceStr,'
           '`CONS_MOBILE` as deliverMobile,'
           '`SPARE_MOBILE` as deliverBackupMobile '
           'FROM oms_db.tf_f_despatch_deliver '
           'WHERE USER_ID ={user_id} '
           'AND CONS_TYPE=2 AND DEFAULT_TYPE=1;').format(user_id=user_id)
    cursor.execute(sql)
    receive_list = cursor.fetchone()
    cursor.close()
    return receive_list


def get_deliver_default(user_id):
    """获取发货信息"""
    cursor = oms_db.cursor(pymysql.cursors.DictCursor)
    sql = ('SELECT '
           '`CONS_COMPANY_NAME` as despatchCompanyName,'
           '`ID` as despatchId,'
           '`CONS_COORDINATE_X` as despatchCoordinateX,'
           '`CONS_COORDINATE_Y` as despatchCoordinateY,'
           '`CONS_NAME` as despatchName,'
           '`CONS_NAME` as despatchInfo, '
           '`CONS_PROVINCE` as despatchprovince,'
           '`CONS_CITY` as despatchcity,'
           '`CONS_AREA` as despatcharea,'
           '`CONS_DETAIL_ADDR` as despatchAddress,'
           '`CONS_LOCATION_ADDR` as despatchPlaceStr,'
           '`CONS_MOBILE` as despatchMobile,'
           '`SPARE_MOBILE` as despatchBackupMobile '
           'FROM oms_db.tf_f_despatch_deliver '
           'WHERE USER_ID ={user_id} '
           'AND CONS_TYPE=1 AND DEFAULT_TYPE=1;').format(user_id=user_id)
    cursor.execute(sql)
    deliver_list = cursor.fetchone()
    cursor.close()
    return deliver_list


def get_receipt_default(consignor_user_id):
    """获取回单快递信息"""
    cursor = oms_db.cursor(pymysql.cursors.DictCursor)
    sql = ('SELECT `ID`,'
           '`USER_ID`,'
           '`CUSTOMER_ID`,'
           '`CONSIGNOR_COMPANY`,'
           '`CONSIGNOR_USER_NAME`,'
           '`RECEIPT_NAME`,'
           '`RECEIPT_MOBILE`,'
           '`RECEIPT_PROVINCE`,'
           '`RECEIPT_CITY`,'
           '`RECEIPT_AREA`,'
           '`RECEIPT_DETAIL_ADDR`,'
           '`RECEIPT_TITLE` '
           'FROM oms_db.tf_f_receipt '
           'WHERE user_id={user_id} AND DEFAULT_TYPE=1;').format(user_id=consignor_user_id)
    cursor.execute(sql)
    receipt_default = cursor.fetchone()
    cursor.close()
    return receipt_default


def get_user_by_serial_number(serial_number: Union[str, int]) -> dict:
    """查询会员的详细信息"""
    cursor = mms_db.cursor(pymysql.cursors.DictCursor)
    sql = ('SELECT `USER_ID`,'
           '`CUSTOMER_ID`,`USER_NM`,`USER_TYPE`,`CONTACTER`,`CONTACTER_PHONE` '
           'FROM mms_db.tf_f_user '
           'WHERE SERIAL_NUMBER={phone};').format(phone=serial_number)
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    return data


def get_user_by_user_id(user_id) -> dict:
    """查询会员的详细信息"""
    cursor = mms_db.cursor(pymysql.cursors.DictCursor)
    sql = ('SELECT `USER_ID`,'
           '`CUSTOMER_ID`,`USER_NM`,`USER_TYPE`,`CONTACTER`,`CONTACTER_PHONE` '
           'FROM mms_db.tf_f_user '
           f'WHERE `USER_ID`={user_id};').format(user_id=user_id)
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    return data


def get_classify_id(cargo_name: str) -> int:
    """获取货物的classify_id"""
    sql = ('SELECT `CLA_ID` '
           'FROM oms_db.tf_b_classify_keywords_new '
           'WHERE `IS_DELETE`= 0 AND `KEYWORD`= "{cargo}";').format(cargo=cargo_name)
    cursor = oms_db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    try:
        return data.get('CLA_ID')
    except AttributeError:
        return -1


def _classify_info_generator(classify_id: int):
    """查询货物分类的迭代器"""
    cursor = oms_db.cursor(pymysql.cursors.DictCursor)
    father_layer = classify_id
    while father_layer > 0:
        sql = ('SELECT '
               '`NAME`, `LAYER`, `FATHER_LAYER`, `IS_END` '
               'FROM oms_db.tf_b_classify_info '
               'WHERE ID={id};').format(id=father_layer)

        cursor.execute(sql)
        data = cursor.fetchone()
        father_layer = data.get('FATHER_LAYER')
        yield data
        _classify_info_generator(father_layer)
    cursor.close()


def get_classify_info_by_classify_id(classify_id):
    """根据货物的classify_id查询货物分类"""
    cargo_layer = []
    for item in _classify_info_generator(classify_id):
        cargo_layer.append(item)
    cargo_layer.reverse()
    cargo_layer_info = {}
    for item in cargo_layer:
        layer_id = 'LAYER' + str(item['LAYER']) + '_ID'
        layer_name = 'LAYER' + str(item['LAYER']) + '_NAME'
        cargo_layer_info[layer_id] = item['LAYER']
        cargo_layer_info[layer_name] = item['NAME']
    if len(cargo_layer) == 2:
        cargo_layer_info['LAYER3_ID'] = None
        cargo_layer_info['LAYER3_NAME'] = None
    return cargo_layer_info


def get_consignor_cargo_list(user_id: str) -> List[dict]:
    """关联货主的货物信息列表"""
    sql = ('SELECT `ID`, `BASE_NAME`, `STATE`, '
           '`LAYER1_ID`, `LAYER1_NAME`, `LAYER2_ID`, `LAYER2_NAME`, `LAYER3_ID`, `LAYER3_NAME` '
           'FROM oms_db.tf_f_cargo_consignor '
           'WHERE CONSIGNOR_USER_ID={user_id};').format(user_id=user_id)
    cursor = oms_db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    cargo_list = cursor.fetchall()
    cursor.close()
    return cargo_list


def get_cargo_insurance(cargo_name: str) -> dict:
    """获取货物货运险信息"""
    classify_id = get_classify_id(cargo_name=cargo_name)
    if classify_id == -1:
        raise ValueError('未获取到货物的classify_id')
    sql = ('SELECT clr.`COMPANY_ID`, '
           'clr.`COMPANY_NAME`, '
           'clr.`INSURANCE_TYPE`, '
           'clr.`CHARGE_MODEL`, '
           'clr.`PLATE_RATE`, '
           'clr.`THRID_RATE`, '
           'clr.`PLATE_UNIT_PREMIUN`, '
           'clr.`THIRD_UNIT_PREMIUN`, '
           'clr.`MIN_PREMIUN`, '
           'clr.`THIRD_MIN_PREMIUN`, '
           'crt.`CARGO_VALUE_LIMITATION`, '
           'crt.`OVER_LIMITATION_RATE`, '
           'crt.`OVER_LIMITATION_FEE`, '
           'crt.`REBATE_PROPORTION`, '
           'crt.`REMARK` '
           'FROM ams_db.tf_f_insurance_classify_rate clr '
           'LEFT JOIN ams_db.tf_b_policy_customer_cargo_type crt '
           'ON clr.`INSURANCE_TYPE` = crt.`POLICY_TYPE` '
           'WHERE clr.`INSURANCE_TYPE`=1 '
           'AND clr.`DELETE_FLAG` = 0 '
           'AND crt.`DELETE_FLAG` = 0 '
           'AND clr.`COMPANY_ID` = crt.`COMPANY_ID` '
           'AND `CLASSIFY_ID` = "{classify_id}";').format(classify_id=classify_id)
    cursor = ams_db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    data = cursor.fetchone()
    return data


def get_liability_insurance(cargo_name: str) -> dict:
    """检查货物责任险信息"""
    classify_id = get_classify_id(cargo_name=cargo_name)
    if classify_id == -1:
        raise ValueError('未获取到货物的classify_id')
    sql = ('SELECT '
           'clr.`COMPANY_ID`, '
           'clr.`COMPANY_NAME`, '
           'clr.`INSURANCE_TYPE`, '
           'clr.`CHARGE_MODEL`, '
           'clr.`PLATE_RATE`, '
           'clr.`THRID_RATE`, '
           'clr.`PLATE_UNIT_PREMIUN`, '
           'clr.`THIRD_UNIT_PREMIUN`, '
           'clr.`MIN_PREMIUN`, '
           'clr.`THIRD_MIN_PREMIUN`, '
           'crt.`CARGO_VALUE_LIMITATION`, '
           'crt.`OVER_LIMITATION_RATE`, '
           'crt.`OVER_LIMITATION_FEE`, '
           'crt.`REBATE_PROPORTION`, '
           'crt.`REMARK` '
           'FROM ams_db.tf_f_insurance_classify_rate clr '
           'LEFT JOIN ams_db.tf_b_policy_customer_cargo_type crt '
           'ON clr.`INSURANCE_TYPE` = crt.`POLICY_TYPE` '
           'WHERE clr.`INSURANCE_TYPE`=2 '
           'AND clr.`DELETE_FLAG` = 0 '
           'AND crt.`DELETE_FLAG` = 0 '
           'AND clr.`COMPANY_ID` = crt.`COMPANY_ID` '
           'AND `CLASSIFY_ID` = "{classify_id}";').format(classify_id=classify_id)
    cursor = ams_db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    data = cursor.fetchone()
    return data


def get_insurance_company_config_correct():
    """执行前 获取保险公司配置，是否等于预设值"""
    sql = ('SELECT '
           '`COMPANY_ID`,'
           '`COMPANY_NAME`,'
           '`POLICY_TYPE`,'
           '`CARGO_VALUE_LIMITATION`,'
           '`CHARGE_MODEL`,'
           '`OVER_LIMITATION_RATE`,'
           '`OVER_LIMITATION_FEE`,'
           '`REBATE_PROPORTION`,'
           '`REMARK`,'
           '`LAST_UPD_BY`,'
           '`LAST_UPD_TIME` '
           'FROM ams_db.tf_b_policy_customer_cargo_type '
           'WHERE `DELETE_FLAG`=0;')
    cursor = ams_db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    data = cursor.fetchone()
    return data


if __name__ == '__main__':
    # print(get_classify_id('无烟煤'))
    # print(get_classify_info(61))
    # print(get_cargo_insurance('笔记本电脑'))
    # print(get_transport_insurance('笔记本电脑'))
    # print(get_user_by_user_id(1355297380739580926))
    print(is_special_cargo('无烟煤'))
    # print(get_liability_insurance('笔记本电脑'))
    print(get_user_by_serial_number(17926663112))
