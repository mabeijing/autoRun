import pymysql
from ._config import oms_db_ini, ams_db_ini, mms_db_ini

oms_db = pymysql.Connect(**oms_db_ini)
mms_db = pymysql.connect(**mms_db_ini)
ams_db = pymysql.Connect(**ams_db_ini)

if __name__ == '__main__':
    print(oms_db_ini)
