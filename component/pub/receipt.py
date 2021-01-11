import utils


class Receipt:
    """
    主要实现回单押金跟货主配置项随机选择(未实现)
    获取默认回单快递信息
    随机一个回单信息
    """

    def __init__(self, session_id, user_id):
        self.session_id = session_id
        self._consignor_user_id = user_id
        self._receipt_info = {}

    # 是否押回单
    def __call__(self, have_receipt: bool = False, receipt_title: str = None):
        receipt_info = utils.get_receipt_default(self._consignor_user_id)
        if have_receipt:
            self._receipt_info['haveReceipt'] = '1'
        else:
            self._receipt_info['haveReceipt'] = '0'
        self._receipt_info['receiptMoney'] = '100'
        self._receipt_info['receiptNameSpan'] = receipt_info['ID']
        self._receipt_info['receiptName'] = receipt_info['RECEIPT_NAME']
        self._receipt_info['receiptMobile'] = receipt_info['RECEIPT_MOBILE']
        self._receipt_info['receiptLabel'] = receipt_info['RECEIPT_TITLE']
        self._receipt_info['receiptProvince'] = receipt_info['RECEIPT_PROVINCE']
        self._receipt_info['receiptCity'] = receipt_info['RECEIPT_CITY']
        self._receipt_info['receiptArea'] = receipt_info['RECEIPT_AREA']
        self._receipt_info['receiptAddressDetails'] = receipt_info['RECEIPT_DETAIL_ADDR']

        return self._receipt_info
