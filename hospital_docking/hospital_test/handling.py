# coding:utf-8
"""
  Time : 2020-03-07 00:07:43
  Author : Vincent
  FileName: handling.py
  Software: PyCharm
  Last Modified by: Vincent
  Last Modified time: 2020-03-07 00:07:43
"""
import re
import os
import json
import datetime
import base64
import configparser
import hashlib
from xml.dom import minidom
from hospital_test.models import Consignee, Prescription, PresDetails


def sql_to_dict(sql):
    '''
    根据 sql 查询语句生成对应字段字典
    :param sql: 查询语句
    :return: 字段字典
    '''
    key_list = []
    key_list2 = []
    select_fields = re.findall('select(.*)from', sql)[0].strip()
    # print(select_fields)
    first_split = select_fields.split(',')
    # print(first_split)
    for i in range(len(first_split)):
        try:
            key_list.append(first_split[i].split('as')[1].strip())
            try:
                key_list2.append(key_list[i].split('.')[1])
            except IndexError:
                key_list2.append(key_list[i].split('.')[0])
        except IndexError:
            key_list.append(first_split[i].split('as')[0].strip())
            try:
                key_list2.append(key_list[i].split('.')[1])
            except IndexError:
                key_list2.append(key_list[i].split('.')[0])
    return key_list2


def get_index(l, x, n):
    '''
    定义通用的获取某元素在序列中第n次出现的位置下标的函数
    :param l: 序列
    :param x: 目标元素
    :param n: 第 n 次出现
    :return:
    '''
    if n <= l.count(x):
        all_index = [key for key, value in enumerate(l) if value == x]
        return all_index[n-1]
    else:
        return None


def get_config(section_name, options):
    """
    读取配置文件信息
    :param section_name:
    :param options:
    :return:
    """
    config_dir = "./resources/"
    config_path = os.path.join(config_dir, "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    options_back = {}
    if isinstance(options, list):
        for option in options:
            if section_name == 'hospital':
                options_back[option] = config.get(section_name, option).encode('utf-8').decode('unicode_escape')
            else:
                options_back[option] = config.get(section_name, option)
        return options_back
    else:
        if section_name == 'hospital':
            return config.get(section_name, options).encode('utf-8').decode('unicode_escape')
        else:
            return config.get(section_name, options)


def md5_creat_password(en_data):
    hl = hashlib.md5()  # 创建 MD5 对象
    hl.update(en_data.encode(encoding='utf-8'))
    return hl.hexdigest().upper()


def response_base64_decode(request_data):
    """对 request 解密"""
    data_encode = request_data.encode('utf-8')
    # print(data_encode)
    response_data_decode = base64.b64decode(data_encode).decode()
    # print(request_data_decode)
    return response_data_decode


def request_base64_encode(response_data):
    """对出参加密"""
    data_encode = response_data.encode('utf-8')
    # print(data_encode)
    request_data_encode = base64.b64encode(data_encode).decode()
    # print(response_data_encode)
    return request_data_encode


class Envelope:
    def __init__(self, env_string):
        dom = minidom.parseString(env_string)
        self.root = dom.documentElement

    def get_context(self, node_name):
        """获取某一结点的值"""
        node = self.root.getElementsByTagName(node_name)
        node_text_node = node[0].childNodes[0]
        return node_text_node.data


class DateEncoder(json.JSONEncoder):
    """
    查询结果转 json 类型，解决 TypeError: Object of type 'datetime' is not JSON serializable 的方法
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)


def ini_encode(ste):
    return ste.encode('unicode_escape').decode()


def ini_decode(std):
    return std.encode('utf-8').decode('unicode_escape')


if __name__=='__main__':
    options = ['companyprovince', 'companycity', 'companyzone', 'companyaddress', 'companyname', 'companytel']
    # company_name = get_config('hospital', options)
    # print(company_name)
    pres_num = 'MZ_201905246418'
    s = '这是一个测试'
    print(md5_creat_password(s))
    pre_sql = "select p.pres_num,p.pres_time,p.treat_card,p.reg_num,p.username,p.age,p.gender,p.tel," \
              "p.is_suffering,p.amount,p.type,p.is_within," \
              "p.is_suffering*p.amount*p.per_pack_num as suffering_num,p.per_pack_num,p.per_pack_dose," \
              "p.ji_fried,p.special_instru,p.hos_depart,p.doctor,p.remark as prescr_remark," \
              "p.medication_methods,p.medication_instruction from MZ_hosp_prescriptions_view p " \
              "where p.pres_num in ('" + pres_num + "');"
    # print(sql_to_dict(pre_sql))
    response = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48cmVzdWx0PjxyZXN1bHRDb2RlPjUwMDwvcmVzdWx0Q29kZT48c3RhdGU+ZmFpbDwvc3RhdGU+PGRlc2NyaXB0aW9uPumqjOivgeWksei0pSzljp/lm6A66K+35rGC5Y+C5pWw5LiN5YWo44CCPC9kZXNjcmlwdGlvbj48L3Jlc3VsdD4="
    res1 = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48cmVzdWx0PjxyZXN1bHRDb2RlPjE8L3Jlc3VsdENvZGU+PG9yZGVySW5mbz48SXNTdWNjZXNzPmZhbHNlPC9Jc1N1Y2Nlc3M+PHJlZ19udW0vPjxwcmVzY3JpcHRpb25JZHMvPjxvcmRlcmlkLz48bWVzc2FnZT7lj4LmlbDmoLzlvI/kuI3mraPnoa7vvIE8L21lc3NhZ2U+PC9vcmRlckluZm8+PGRlc2NyaXB0aW9uPuWksei0pTwvZGVzY3JpcHRpb24+PHN0YXRlPmZhaWw8L3N0YXRlPjwvcmVzdWx0Pg=="
    print(response_base64_decode(response))
    print(response_base64_decode(res1))
    response = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><ns2:saveOrderInfoToCharacterSetResponse xmlns:ns2="http://factory.service.cxf.kangmei.com/"><return>PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48cmVzdWx0PjxyZXN1bHRDb2RlPjE8L3Jlc3VsdENvZGU+PG9yZGVySW5mbz48SXNTdWNjZXNzPmZhbHNlPC9Jc1N1Y2Nlc3M+PHJlZ19udW0vPjxwcmVzY3JpcHRpb25JZHMvPjxvcmRlcmlkLz48bWVzc2FnZT7lj4LmlbDmoLzlvI/kuI3mraPnoa7vvIE8L21lc3NhZ2U+PC9vcmRlckluZm8+PGRlc2NyaXB0aW9uPuWksei0pTwvZGVzY3JpcHRpb24+PHN0YXRlPmZhaWw8L3N0YXRlPjwvcmVzdWx0Pg==</return></ns2:saveOrderInfoToCharacterSetResponse></soap:Body></soap:Envelope>"""
    k = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><result><description>success</description><resultCode>0</resultCode><state>success</state><orderInfo><reg_num>OP0004350665</reg_num><IsSuccess>true</IsSuccess><message>success</message><orderid>KM20031726413</orderid><prescriptionIds>KM20031726413-1</prescriptionIds></orderInfo></result>"
    en = Envelope(response)
    b_data = en.get_context('return')
    print(b_data)
    x_data = response_base64_decode(b_data)
    xm = Envelope(k)
    print(xm.get_context('orderid'))
    s = '云南省精神病医院'
    appID = '101856'
    appSecret = '云南省昆明市盘龙区穿金路733号'
    se = ini_encode(s)
    se1 = ini_encode(appSecret)
    sd = ini_decode(se)
    sd1 = ini_decode(se1)
    print(se)
    print(se1)
    print(sd)
    print(sd1)
    p = Prescription()
    print(dict(p))

