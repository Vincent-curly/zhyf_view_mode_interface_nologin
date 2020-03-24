# coding:utf-8
"""
  Time : 2020-03-16 00:22:40
  Author : Vincent
  FileName: zhenzismsclient.py
  Software: PyCharm
  Last Modified by: Vincent
  Last Modified time: 2020-03-16 00:22:40
"""
import urllib.request
import urllib.parse
import ssl


class ZhenziSmsClient(object):
    def __init__(self, apiUrl, appId, appSecret):
        self.apiUrl = apiUrl
        self.appId = appId
        self.appSecret = appSecret

    def send(self, number, message, messageId=''):
        data = {
            'appId': self.appId,
            'appSecret': self.appSecret,
            'message': message,
            'number': number,
            'messageId': messageId
        }

        data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(self.apiUrl+'/sms/send.do', data=data)
        context = ssl._create_unverified_context()
        res_data = urllib.request.urlopen(req, context=context)
        res = res_data.read()
        res = res.decode('utf-8')
        return res

    def balance(self):
        data = {
            'appId': self.appId,
            'appSecret': self.appSecret
        }
        data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(self.apiUrl+'/account/balance.do', data=data)
        res_data = urllib.request.urlopen(req)
        res = res_data.read()
        return res

    def findSmsByMessageId(self, messageId):
        data = {
            'appId': self.appId,
            'appSecret': self.appSecret,
            'messageId': messageId
        }
        data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(self.apiUrl+'/smslog/findSmsByMessageId.do', data=data)
        res_data = urllib.request.urlopen(req)
        res = res_data.read()
        return res


if __name__=='__main__':
    mgclient = ZhenziSmsClient('https://sms_developer.zhenzikj.com', '101856', '6eacf139-384e-4026-ac3e-1dfc5517d452')
    me = "-{}-{}将处方插入中间表发生异常！处方号：{} ."
    tel = '18687126965'
    hos_name = '云南省精神病医院'
    pres_num = 'MZ_202003160440'
    print(mgclient.send(tel, me.format(tel, hos_name, pres_num)))