"""
普通货-抢单-单价-自主保险-正常货物
"""
from session import Session

session = Session()
session.stage.cargo.random_common_cargo()
stage = session.stage.create_order.bidding_order_consignor_insurance()
print(stage)
session.owner.login()
session.owner.publish(stage)
exit()
session.carrier.deal()

session.carrier.transport_deliver()

session.carrier.transport_reciver()

session.admin.check_order_insurance()

session.admin.receipt_examine()

session.admin.settlement_examine()

session.admin.owner_settlement()

session.admin.carrier_settlement()

session.admin.owner_invoice_examine()

session.admin.invoice()

session.admin.invoice_ems()
