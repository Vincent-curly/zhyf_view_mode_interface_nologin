# coding:utf-8
"""
  Time : 2020-03-17 15:21:10
  Author : Vincent
  FileName: xml_envelope.py
  Software: PyCharm
  Last Modified by: Vincent
  Last Modified time: 2020-03-17 15:21:10
"""
import xml.etree.cElementTree as ET
import base64


class XmlEnvelopeTree(object):
    '''
        Xml Envelope Tree parser
    '''
    def __init__(self, envString):
        if isinstance(envString, dict):
            node_list = []
            for key,value in envString.items():
                node = ET.Element(key)
                node.text = str(value)
                node_list.append(node)
            root = ET.Element('result')  # 创建根节点
            root.extend(node_list)
            self.root = root
            self.tree = ET.ElementTree(root)
        elif isinstance(envString, str):
            self.root = ET.fromstring(envString)

    def xml_to_dict(self):
        '''
            parse Xml Envelope to dict
        '''
        medicine_node = ['medicines', 'dose', 'unit', 'unit_price', 'goods_num', 'dose_that',
                         'remark', 'm_usage', 'goods_norms', 'goods_orgin', 'MedPerDos', 'MedPerDay']
        dict_data = {}
        n = 0
        xq_childs = 0
        for child in self.root.iter():
            # print(child.tag)
            # print(child.text)
            if child.tag not in medicine_node:
                if child.tag == 'xq':
                    xq_childs = child.__len__()     # __len__：返回元素大小，元素的大小为元素的子元素数量
                dict_data[child.tag] = child.text
            else:
                if n < xq_childs:
                    dict_data[child.tag] = [child.text]
                    n += 1
                else:
                    dict_data[child.tag].append(child.text)
        return dict_data

    def envelope_encode(self):
        data = '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(self.root, encoding='utf-8').decode()
        return data


if __name__=='__main__':
    """
    xml_tree = XmlEnvelopeTree(None)
    print(xml_tree)
    xml_tree.tree.write('x_write.xml')
    """
    d = {'description': '成功', 'resultCode': 0, 'status': 'success'}
    xml_tree1 = XmlEnvelopeTree(d)
    print(xml_tree1.envelope_encode())
    print(type(xml_tree1.envelope_encode()))
    en = base64.b64encode(xml_tree1.envelope_encode().encode('utf-8'))
    print(en)
    print(type(en))
    de = en.decode()
    print(de)
    print(type(de))
    de1 = base64.b64decode(de.encode('utf-8')).decode()
    print(de1)
    optional = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><orderInfo><head><company_num>10307</company_num><key>1579062596134</key><sign>593717798B21FC7D7CF2FE6DDD89FE34</sign></head><data><order_time>2020-01-15 14:00:00</order_time><treat_card>53011119671204442X</treat_card><reg_num>U0121552</reg_num><addr_str>云南省,昆明市,官渡区,昆明市官渡区人民医院内三科（昆明关上寅峰路63号二号住院楼5层）</addr_str><consignee>陈文兮</consignee><con_tel>67188105-8033</con_tel><send_goods_time></send_goods_time><is_hos_addr>1</is_hos_addr><prescript><pdetail><user_name>毕丽亚</user_name><age>52</age><gender>0</gender><tel>67188105-8033</tel><is_suffering>1</is_suffering><amount>18</amount><suffering_num>18</suffering_num><ji_fried>1</ji_fried><type>0</type><is_within>0</is_within><other_pres_num>U0121552</other_pres_num><special_instru>(J18.900)肺炎</special_instru><bed_num>73</bed_num><hos_depart>内三科</hos_depart><hospital_num>222847</hospital_num><disease_code>0200</disease_code><doctor>杨阳</doctor><paste_desc_file></paste_desc_file><prescript_remark></prescript_remark><package_dose></package_dose><medication_methods>煎服</medication_methods><is_hos>2</is_hos><per_pack_num>1</per_pack_num><per_pack_dose>200</per_pack_dose><medication_instruction>每天3次</medication_instruction><prescript_remark>煎9袋</prescript_remark><medici_xq><xq><medicines>*黄芪</medicines><dose>30.00</dose><unit>克</unit><unit_price>0.08</unit_price><goods_num>0000041</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*白术</medicines><dose>15.00</dose><unit>克</unit><unit_price>0.07</unit_price><goods_num>0000011</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*陈皮</medicines><dose>10.00</dose><unit>克</unit><unit_price>0.04</unit_price><goods_num>0000273</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*滇柴胡</medicines><dose>15.00</dose><unit>克</unit><unit_price>0.02</unit_price><goods_num>0000190</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*葛根</medicines><dose>20.00</dose><unit>克</unit><unit_price>0.07</unit_price><goods_num>0000029</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*防风</medicines><dose>15.00</dose><unit>克</unit><unit_price>0.08</unit_price><goods_num>0000025</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*防风</medicines><dose>15.00</dose><unit>克</unit><unit_price>0.08</unit_price><goods_num>0000025</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*黄连</medicines><dose>10.00</dose><unit>克</unit><unit_price>0.28</unit_price><goods_num>0000038</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*茯苓</medicines><dose>30.00</dose><unit>克</unit><unit_price>0.07</unit_price><goods_num>0000322</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*法半夏</medicines><dose>10.00</dose><unit>克</unit><unit_price>0.43</unit_price><goods_num>0000024</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*桔梗</medicines><dose>15.00</dose><unit>克</unit><unit_price>0.11</unit_price><goods_num>0000045</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*广藿香</medicines><dose>15.00</dose><unit>克</unit><unit_price>0.06</unit_price><goods_num>0000199</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*浙贝母</medicines><dose>15.00</dose><unit>克</unit><unit_price>0.24</unit_price><goods_num>0000092</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*甘草</medicines><dose>10.00</dose><unit>克</unit><unit_price>0.07</unit_price><goods_num>0000028</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*薏苡仁</medicines><dose>20.00</dose><unit>克</unit><unit_price>0.04</unit_price><goods_num>0000178</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*薏苡仁</medicines><dose>20.00</dose><unit>克</unit><unit_price>0.04</unit_price><goods_num>0000178</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*麻黄</medicines><dose>10.00</dose><unit>克</unit><unit_price>0.09</unit_price><goods_num>0000206</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*苦杏仁</medicines><dose>10.00</dose><unit>克</unit><unit_price>0.06</unit_price><goods_num>0000175</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*蜜瓜蒌皮</medicines><dose>15.00</dose><unit>克</unit><unit_price>0.06</unit_price><goods_num>0000287</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*白及</medicines><dose>15.00</dose><unit>克</unit><unit_price>1.70</unit_price><goods_num>0000004</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*滇百部</medicines><dose>15.00</dose><unit>克</unit><unit_price>0.13</unit_price><goods_num>0000001</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq><xq><medicines>*白前</medicines><dose>15.00</dose><unit>克</unit><unit_price>0.15</unit_price><goods_num>0000007</goods_num><dose_that></dose_that><remark></remark><m_usage></m_usage><goods_norms>克</goods_norms><goods_orgin></goods_orgin><MedPerDos></MedPerDos><MedPerDay></MedPerDay></xq></medici_xq></pdetail></prescript></data></orderInfo>"
    request1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><orderInfo><head><company_num>10426</company_num><sign>ab310c9638f50b64cd8ae1d8f90341ca</sign><key>1582387461673</key></head><data><order_time>2020-02-23 00:04:09</order_time><reg_num>M2020022300041045834</reg_num><addr_str>四川省,成都市,新津县,新津县林园路58号</addr_str><consignee>杨绍琼</consignee><con_tel>15388103153</con_tel><pay_status>1</pay_status><callback_url>http://yaofang.bailuzy.com/api/kangmei/orderUpdate?param=eyJvcmRlcl9zbiI6Ik0yMDIwMDIyMzAwMDQxMDQ1ODM0Iiwic2lnbiI6IjE5YzBiNDRhMTk1MDI2NzdmZTJmZDZkM2YxY2M4ZGRkIn0=</callback_url><logis_url_callback>http://yaofang.bailuzy.com/api/kangmei/expressUpdate?param=eyJvcmRlcl9zbiI6Ik0yMDIwMDIyMzAwMDQxMDQ1ODM0Iiwic2lnbiI6IjE5YzBiNDRhMTk1MDI2NzdmZTJmZDZkM2YxY2M4ZGRkIn0=</logis_url_callback><prescript><pdetail><user_name>杨绍琼</user_name><age>62</age><gender>0</gender><tel>15388103153</tel><is_suffering>0</is_suffering><suffering_num>0</suffering_num><ji_fried>0</ji_fried><amount>3</amount><prescri_type>0</prescri_type><wj_type></wj_type><is_within>0</is_within><other_pres_num>KM_M2020022300041045834</other_pres_num><special_instru>脾虚湿热证</special_instru><doctor>白露中医</doctor><package_dose></package_dose><is_invoice>0</is_invoice><medication_instruction>每日1帖,每贴3次</medication_instruction><prescript_remark>用药时间:两餐间服用,注意事项:忌生冷,忌辛辣,忌油腻,忌发物,忌荤腥,忌烟酒,温服30-40℃</prescript_remark><medication_methods></medication_methods><per_pack_num>3</per_pack_num><medici_xq><xq><medicines>知母</medicines><dose>15</dose><unit>克</unit><unit_price>0.14868</unit_price><goods_num>35</goods_num><m_usage></m_usage></xq><xq><medicines>玄参</medicines><dose>15</dose><unit>克</unit><unit_price>0.09306</unit_price><goods_num>29</goods_num><m_usage></m_usage></xq><xq><medicines>芦根</medicines><dose>20</dose><unit>克</unit><unit_price>0.08550</unit_price><goods_num>496</goods_num><m_usage></m_usage></xq><xq><medicines>肉桂</medicines><dose>5</dose><unit>克</unit><unit_price>0.09666</unit_price><goods_num>179</goods_num><m_usage>后下</m_usage></xq><xq><medicines>黄连</medicines><dose>3</dose><unit>克</unit><unit_price>0.46296</unit_price><goods_num>226</goods_num><m_usage></m_usage></xq><xq><medicines>仙鹤草</medicines><dose>20</dose><unit>克</unit><unit_price>0.06624</unit_price><goods_num>454</goods_num><m_usage></m_usage></xq><xq><medicines>豆蔻</medicines><dose>10</dose><unit>克</unit><unit_price>0.26622</unit_price><goods_num>342</goods_num><m_usage>后下</m_usage></xq><xq><medicines>薏苡仁</medicines><dose>15</dose><unit>克</unit><unit_price>0.05490</unit_price><goods_num>408</goods_num><m_usage></m_usage></xq><xq><medicines>姜厚朴</medicines><dose>15</dose><unit>克</unit><unit_price>0.08190</unit_price><goods_num>405</goods_num><m_usage></m_usage></xq><xq><medicines>柴胡（北柴胡）</medicines><dose>15</dose><unit>克</unit><unit_price>0.37566</unit_price><goods_num>41</goods_num><m_usage></m_usage></xq><xq><medicines>白芍</medicines><dose>15</dose><unit>克</unit><unit_price>0.11628</unit_price><goods_num>403</goods_num><m_usage></m_usage></xq><xq><medicines>当归</medicines><dose>10</dose><unit>克</unit><unit_price>0.19026</unit_price><goods_num>36</goods_num><m_usage></m_usage></xq><xq><medicines>茯神</medicines><dose>20</dose><unit>克</unit><unit_price>0.17604</unit_price><goods_num>146</goods_num><m_usage></m_usage></xq><xq><medicines>炙甘草</medicines><dose>5</dose><unit>克</unit><unit_price>0.12654</unit_price><goods_num>42</goods_num><m_usage></m_usage></xq><xq><medicines>炮姜</medicines><dose>5</dose><unit>克</unit><unit_price>0.11502</unit_price><goods_num>64</goods_num><m_usage></m_usage></xq><xq><medicines>青皮</medicines><dose>10</dose><unit>克</unit><unit_price>0.08676</unit_price><goods_num>24</goods_num><m_usage></m_usage></xq><xq><medicines>燀苦杏仁</medicines><dose>10</dose><unit>克</unit><unit_price>0.12006</unit_price><goods_num>918</goods_num><m_usage></m_usage></xq><xq><medicines>干石斛</medicines><dose>10</dose><unit>克</unit><unit_price>0.41796</unit_price><goods_num>139</goods_num><m_usage></m_usage></xq><xq><medicines>南沙参</medicines><dose>15</dose><unit>克</unit><unit_price>0.17460</unit_price><goods_num>28</goods_num><m_usage></m_usage></xq><xq><medicines>白术</medicines><dose>15</dose><unit>克</unit><unit_price>0.12402</unit_price><goods_num>188</goods_num><m_usage></m_usage></xq></medici_xq></pdetail></prescript></data></orderInfo>"
    env_tree = XmlEnvelopeTree(request1)
    print(env_tree.xml_to_dict())


