from goRequest import Request
from DBUtils import rds
import requests
from requests import utils
import config
import logging

logger = logging.getLogger(__name__)


class Owner:
    """
    货主类：
    主要实现货主操作方法。通过接口操作，无需返回
    """

    def __init__(self, session_id, account, user_id):
        self.session_id = session_id
        self.account = account
        self.consignor_user_id = user_id
        self._request = Request(session_id)

    def login(self):
        """
        :return:
        """
        url = config.host + '/sys/login'
        method = 'POST'
        headers = {
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        data = {
            "loginName": str(self.account),
            "bossId": "",
            "loginPassword": config.account.get(str(self.account)),
            "loginType": "password",
            "verifyCode": "",
            "userMobile": ""
        }
        # logger.info(r)
        response = self._request.go(method, url, header=headers, data=data)
        if response.status_code != 200:
            logger.error('login failed' + response.text)
            # logger.info(rds.hget(self.session_id))
            exit()
        cookie_dict = requests.utils.dict_from_cookiejar(response.cookies)
        for key, value in cookie_dict.items():
            _cookie = '\"' + str(key) + '=' + str(value) + '\"'
        rds.hset(self.session_id, 'cookie', str(_cookie))

    def publish(self, stage_type):
        url = config.host + '/order/addConsignorOrder/addOrderForSeniorConsignor'
        method = 'POST'
        cookie = rds.hget(self.session_id, 'cookie')
        headers = {
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": cookie
        }
        response = self._request.go(method=method, url=url, header=headers, data=stage_type)
        order_id = response.json().get('orderId')
        rds.hset(self.session_id, 'orderId', order_id)


if __name__ == '__main__':
    pass
