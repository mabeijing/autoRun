import requests
import logging

logger = logging.getLogger(__name__)


class Request:
    """
    自定义请求：
    实现日志记录，错误拦截，打印具体case明细步骤和当前环境参数
    恢复环境
    高级功能。并发请求
    """

    def __init__(self, session_id):
        self.session_id = session_id

    def go(self, method, url, data=None, header=None):
        try:
            r = requests.request(method, url, data=data, headers=header)
            logger.error(self.session_id + ': ' + str(r.text))
            return r
        except Exception as e:
            logger.error(self.session_id + ': ' + str(e))
            exit()
