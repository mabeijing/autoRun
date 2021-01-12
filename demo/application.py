import re
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from flask import Flask, request, jsonify, Response, escape
import pymysql
from celery import Celery

app = Flask(__name__)


def make_celery(apps):
    celery = Celery(
        apps.import_name,
        backend=apps.config['CELERY_RESULT_BACKEND'],
        broker=apps.config['CELERY_BROKER_URL']
    )
    celery.conf.update(apps.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with apps.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(app)


@celery.task()
def add_together(a, b):
    return a + b


conn = pymysql.connect(charset='utf8mb4', port=3306, user='test',
                       password='TeSt163@pybgRey', database='oms_db',
                       host='172.20.20.29', use_unicode=True)

cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

PKCS7_BLOCK_SIZE = AES.block_size
PKCS5_BLOCK_SIZE = 8
user_key_f = [0xa7, 0x81, 0x88, 0xf2, 0xaa, 0x69, 0x59, 0x93, 0x7b, 0x96, 0x3b, 0xd6, 0xb6, 0xa7, 0x3e, 0x44]
user_key_s = [0xdb, 0x15, 0x0d, 0x90, 0xb8, 0x26, 0x0d, 0xca, 0x03, 0xde, 0x81, 0xbf, 0x12, 0x4d, 0x94, 0x05]
user_key2 = [-65, -36, 67, 6, 95, 1, -124,
             122, 95, -108, 34, -75, -88, -36, 62, 94]
user_key1 = [-41, -15, -35, -94, 76, 48, -28,
             64, -121, -67, -114, 18, 31, -125, -35, -109]
f_mode = [i + 256 if i < 0 else i for i in user_key1]
s_mode = [i + 256 if i < 0 else i for i in user_key2]

iv = bytes(16)


@app.route('/index')
def index():
    data = 'Cookie:UM_distinctid=17283980a040-0610bb25d7ee87-f7d1d38-1fa400-17283980a05881; CNZZDATA1254886089=1969187-1597747681-%7C1600656985; SHAROJSESSIONID=ZTVkYTQ2MzktMzA4Yy00NmUzLThiMDgtYjRmYjMxYzM1ZjBk'
    return Response(data, mimetype='test/plain')


@app.route('/to_json')
def to_json():
    if request.method == "GET":
        comment = request.get_data()
        # comment = request.values.get("content")
    if request.method == "POST":
        if request.content_type.startswith('application/json'):
            # comment = request.get_json()["content"]
            comment = request.json.get('content')
        elif request.content_type.startswith('multipart/form-data'):
            comment = request.form.get('content')
        else:
            comment = request.values.get("content")
    str_list = re.split(r'(?:[\r\n])', comment.decode('utf-8'))
    data_list = [i for i in str_list if i]
    target_dict = {}
    print(request.headers)
    for item in data_list:
        item_list = re.split(r'(?:[ \t])', item, maxsplit=1)
        if item_list[0].endswith(':'):
            item_list[0] = item_list[0][:-1]
        # tmp_list = item_list[0].split('-')
        # tmp_list_cap = [i.capitalize() for i in tmp_list]
        # item_list[0] = '-'.join(tmp_list_cap)
        item_list[1] = item_list[1].strip()
        target_dict[item_list[0]] = item_list[1]

    # return jsonify(target_dict)
    return Response(json.dumps(target_dict), mimetype='application/json')


@app.route('/to_data')
def to_data():
    if request.method == "GET":
        comment = request.get_data()
        # comment = request.values.get("content")
    if request.method == "POST":
        if request.content_type.startswith('application/json'):
            # comment = request.get_json()["content"]
            comment = request.json.get('content')
        elif request.content_type.startswith('multipart/form-data'):
            comment = request.form.get('content')
        else:
            comment = request.values.get("content")
    str_list = re.split(r'(?:[\r\n])', comment.decode('utf-8'))
    data_list = [i for i in str_list if i]
    print(data_list)
    target_dict = {}
    print(request.headers)
    for item in data_list:
        item_list = re.split(r'(?:[ \t])', item, maxsplit=1)
        if item_list[0].endswith(':'):
            item_list[0] = item_list[0][:-1]
        item_list[1] = item_list[1].strip()
        target_dict[item_list[0]] = item_list[1]
    print(target_dict)
    data_list = []
    for key, value in target_dict.items():
        iv = str(key) + ':' + str(value) + '\n'
        data_list.append(iv)
    print(data_list)
    data = ''.join(data_list)
    return Response(data, mimetype='text/plain')


@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.form
    device_type = data.get('deviceType', None)
    role_type = data.get('roleType', 'carrier')
    cipher_text = data.get('cipherText', None)
    if not cipher_text:
        return Response(json.dumps({'msg': 'cipher_text参数必填，搞啥呢'}), mimetype='application/json')
    if (not role_type) or role_type == 'carrier':
        if cipher_text[0] == 'F':
            key = bytearray(f_mode)
            cipher_data = cipher_text[1:]
        elif cipher_text[0] == 'S':
            key = bytearray(s_mode)
            cipher_data = cipher_text[1:]
        else:
            key = bytearray(f_mode)
            cipher_data = cipher_text
    else:
        if cipher_text[0] == 'F':
            key = bytearray(user_key_f)
            cipher_data = cipher_text[1:]
        elif cipher_text[0] == 'S':
            key = bytearray(user_key_s)
            cipher_data = cipher_text[1:]
        else:
            key = bytearray(user_key_f)
            cipher_data = cipher_text

    if device_type == 'app':
        block = PKCS7_BLOCK_SIZE
    else:
        block = PKCS5_BLOCK_SIZE
    temp = base64.b64decode(cipher_data)
    dec = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
    try:
        decrypt_data = dec.decrypt(temp)
        result = unpad(decrypt_data, block).decode('utf-8')
        data_dict = eval(result)
        return Response(json.dumps(data_dict), mimetype='application/json')
    except ValueError as e:
        return Response(json.dumps({'msg': str(e), 'reson': '密文格式错误,切换roloType或者deviceType重试'}),
                        mimetype='application/json')


@app.route('/get_order_detail_id', methods=['GET', 'POST'])
def query_order_detail_id():
    data = request.form
    orderId = data['orderId']
    sql = 'select DETAIL_ID from tf_b_transport where ORDER_ID={orderId}'.format(
        orderId=orderId)
    cursor.execute(sql)

    data = cursor.fetchone()
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/get_expectId', methods=['GET', 'POST'])
def get_expectId():
    data = request.form
    orderId = data['orderId']
    role_phone = data['phone']
    sql = 'select EXPECT_ID from tf_b_expect where ORDER_ID={orderId} and CARRIER_USER_MOBILE={phone} and DELETE_FLAG=0'.format(
        orderId=orderId, phone=role_phone)
    cursor.execute(sql)

    data = cursor.fetchone()
    return Response(json.dumps(data), mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
