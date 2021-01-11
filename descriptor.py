import json
from dbUtils import rds


class OilAttr:
    def __init__(self):
        self._setter = {}

    def __get__(self, instance, owner):
        oil = instance._oil(**self._setter)
        rds.hset(instance.session_id, 'oil', json.dumps(oil, ensure_ascii=False))
        return oil

    def __set__(self, instance, value: dict):
        self._setter = value


class ReceiptAttr:
    def __init__(self):
        self._setter = {}

    def __get__(self, instance, owner):
        _receipt = instance._receipt(**self._setter)
        rds.hset(instance.session_id, 'receipt', json.dumps(_receipt, ensure_ascii=False))
        return _receipt

    def __set__(self, instance, value: dict):
        self._setter = value


class CommonAttr:
    def __init__(self):
        self._setter = {}

    def __get__(self, instance: object, owner):
        _common = instance._common(**self._setter)
        rds.hset(instance.session_id, 'common', json.dumps(_common, ensure_ascii=False))
        return _common

    def __set__(self, instance, value: dict):
        self._setter = value


class DesignateAttr:
    def __init__(self):
        self._setter = {}

    def __get__(self, instance, owner):
        _designate = instance._designate(**self._setter)
        rds.hset(instance.session_id, 'designate', json.dumps(_designate, ensure_ascii=False))
        return _designate

    def __set__(self, instance, value: dict):
        self._setter = value
