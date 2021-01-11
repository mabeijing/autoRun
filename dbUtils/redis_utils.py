import errno
import json
from json.decoder import JSONDecodeError
import redis
from ._config import redis_config

pool = redis.ConnectionPool(**redis_config)
redis_connect = redis.Redis(connection_pool=pool)


class Rds(redis.Redis):
    def __init__(self):
        super(Rds, self).__init__(connection_pool=pool)

    def hget(self, name, key):
        data = super(Rds, self).hget(name, key)
        try:
            return json.loads(data)
        except JSONDecodeError:
            from decimal import Decimal
            return eval(data)
        except Exception as e:
            print(e)
            return super(Rds, self).hget(name, key)


rds = Rds()
