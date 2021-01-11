from goRequest import Request


class Carrier:
    """
    提供类承运方的操作
    默认流程，承运方自己摘单，随机一辆认证通过的车辆
    """

    def __init__(self, session_id, user_id, account):
        self.session_id = session_id
        self.account = account
        self.carrier_user_id = user_id
        self._related_boss = None
        self._car = None
        self._request = Request(session_id)

    def deal(self):
        pass

    def bidding(self):
        pass

    def re_bidding(self):
        pass

    def modify_bidding(self):
        pass

    def transport_deliver(self):
        pass

    def transport_receiver(self):
        pass

    def _use_advance_payment(self):
        pass

    def _carrier_insurance(self):
        pass

    def _use_fast_payment(self):
        pass

    def _modify_receipt_order(self):
        pass
