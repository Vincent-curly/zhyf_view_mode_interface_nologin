# coding:utf-8
"""
  Time : 2020-03-15 01:57:15
  Author : Vincent
  FileName: HosPrescriptionService.py
  Software: PyCharm
  Last Modified by: Vincent
  Last Modified time: 2020-03-15 01:57:15
"""
import time
import logging
import requests
from sqlalchemy.dialects import mysql
from sqlalchemy.exc import SQLAlchemyError
from suds.client import Client
from hospital_test.models import Consignee, Prescription, PresDetails, get_local_session, update_prescription_statues
from hospital_test.handling import get_config, md5_creat_password, request_base64_encode, response_base64_decode, \
    Envelope


logger = logging.getLogger('suds')
logger.setLevel(logging.INFO)


def upload_prescription(pres):
    request_sb = build_upload_prescription_req(pres)
    url = get_config('interface', 'orderUrl')
    logging.info("调用康美接口saveOrderInfoToCharacterSet Begin, 请求url：%s, 请求体：%s" % (url, request_sb))
    """
    # 使用 suds 调用 webservice 接口保存订单
    request_body = request_base64_encode(request_sb)
    logger.info('request_body:%s' % request_body)
    client = Client(url)
    response = client.service.saveOrderInfoToCharacterSet(request_body, 'utf-8')
    # print('last sent:\n', client.last_sent())
    # print('last recv:\n', client.last_received())
    logger.info('response:%s' % response)
    logger.info("调用康美接口saveOrderInfoToCharacterSet End, 接口返回：%s", response_base64_decode(response))
    """
    # 使用 requests 向 webservice 接口发送报文数据保存订单
    request_body = get_request_body(request_sb)
    response = requests.post(url, request_body)
    logging.info('response envelope:%s' % response.text)
    env = Envelope(response.text)
    xml_data = response_base64_decode(env.get_context('return'))
    logging.info("调用康美接口saveOrderInfoToCharacterSet End, 接口返回：%s", xml_data)
    xml = Envelope(xml_data)
    if (xml.get_context("resultCode") == '0') or (xml.get_context("resultCode") == '22'):
        order_id = xml.get_context("orderid")
        description = xml.get_context('message')
        logging.info("处方上传成功！处方号：%s -- 对应订单号：%s" % (pres.pres_num, order_id))
        update_prescription_statues(pres.pres_num, order_id=order_id, describe=description)
    else:
        logging.info("处方上传失败！处方号为：%s", pres.pres_num)
        if xml.get_context("resultCode") == '500':
            reason = xml.get_context('description')
        else:
            reason = xml.get_context('message')
        update_prescription_statues(pres.pres_num, describe=reason)


def build_upload_prescription_req(pres):
    """
    组装请求报文
    :param pres:
    :return:
    """
    key = int(time.time() * 1000)
    sign = md5_creat_password("saveOrderInfo" + str(key) + get_config('hospital', 'companyPass'))
    pres_details = find_prescription_details(pres)       # 查询得到订单详情
    content = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    content += "<orderInfo>"
    content += "<head>"
    content += "<company_num>" + get_config('hospital', 'companyNum') + "</company_num>"
    content += "<key>" + str(key) + "</key>"
    content += "<sign>" + sign + "</sign>"
    content += "</head>"
    content += "<data>"
    content += "<order_time>" + pres.pres_time + "</order_time>"
    content += "<treat_card>" + pres.treat_card + "</treat_card>"
    content += "<reg_num>" + pres.reg_num + "</reg_num>"
    content += "<addr_str>" + pres.province + "," + pres.city + "," + pres.zone + "," + pres.addr_detail + "</addr_str>"
    content += "<consignee>" + pres.consignee + "</consignee>"
    content += "<con_tel>" + pres.con_tel + "</con_tel>"
    content += "<send_goods_time>" + (pres.send_goods_time if pres.send_goods_time else '') + "</send_goods_time>"
    content += "<is_hos_addr>" + str(pres.is_hos_addr) + "</is_hos_addr>"
    content += "<prescript>"
    content += "<pdetail>"
    content += "<user_name>" + pres.user_name + "</user_name>"
    content += "<doctor>" + pres.doctor + "</doctor>"
    content += "<age>" + str(pres.age) + "</age>"
    content += "<gender>" + str(pres.gender) + "</gender>"
    content += "<tel>" + pres.tel + "</tel>"
    content += "<is_suffering>" + str(pres.is_suffering) + "</is_suffering>"
    content += "<amount>" + str(pres.amount) + "</amount>"
    content += "<suffering_num>" + str(pres.suffering_num) + "</suffering_num>"
    content += "<ji_fried>" + str(pres.ji_fried) + "</ji_fried>"
    content += "<per_pack_num>" + str(pres.per_pack_num) + "</per_pack_num>"
    content += "<per_pack_dose>" + (str(pres.per_pack_dose) if pres.per_pack_dose else '200') + "</per_pack_dose>"
    content += "<type>" + str(pres.type) + "</type>"
    content += "<other_pres_num>" + pres.other_pres_num + "</other_pres_num>"
    content += "<special_instru>" + pres.special_instru + "</special_instru>"
    content += "<is_within>" + str(pres.is_within) + "</is_within>"
    content += "<bed_num>" + (str(pres.bed_num) if pres.bed_num else '') + "</bed_num>"
    content += "<hos_depart>" + (pres.hos_depart if pres.hos_depart else '') + "</hos_depart>"
    content += "<hospital_num>" + (pres.hospital_num if pres.hospital_num else '') + "</hospital_num>"
    content += "<disease_code>" + (pres.disease_code if pres.disease_code else '') + "</disease_code>"
    content += "<prescript_remark>" + (pres.prescript_remark if pres.prescript_remark else '') + "</prescript_remark>"
    content += "<medication_methods>" + (pres.medication_methods if pres.medication_methods else '') + \
               "</medication_methods>"
    content += "<medication_instruction>" + \
               (pres.medication_instruction if pres.medication_instruction else '') + "</medication_instruction>"
    content += "<is_hos>" + ('2' if pres.source == 1 else '1') + "</is_hos>"
    content += "<medici_xq>"
    for pres_det in pres_details:
        content += "<xq>"
        content += "<medicines>" + pres_det.medicines + "</medicines>"
        content += "<dose>" + pres_det.dose + "</dose>"
        content += "<unit>" + pres_det.unit + "</unit>"
        content += "<goods_num>" + pres_det.goods_num + "</goods_num>"
        content += "<dose_that>" + (pres_det.dose_that if pres_det.dose_that else '') + "</dose_that>"
        content += "<remark>" + (pres_det.remark if pres_det.remark else '') + "</remark>"
        content += "<m_usage>" + (pres_det.m_usage if pres_det.m_usage else '') + "</m_usage>"
        content += "<goods_norms>" + (pres_det.goods_norms if pres_det.goods_norms else '') + "</goods_norms>"
        content += "<goods_orgin>" + (pres_det.goods_orgin if pres_det.goods_orgin else '') + "</goods_orgin>"
        content += "</xq>"
    content += "</medici_xq>"
    content += "</pdetail>"
    content += "</prescript>"
    content += "</data>"
    content += "</orderInfo>"
    return content


def find_prescription_details(pres):
    session = get_local_session()[1]
    logging.info("从中间表查询处方详情：")
    pres_detail_query = session.query(PresDetails).filter(PresDetails.pres_num == pres.pres_num)
    sql = str(pres_detail_query.statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}))
    logging.info('==> executing:%s' % sql)
    pres_detail_res = pres_detail_query.all()
    logging.info("==> Parameters:%s" % pres_detail_res)
    session.close()
    return pres_detail_res


def get_request_body(content):
    """
    对请求报文进行 Base64
    :param content:
    :return:
    """
    sb = "<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\"  >"
    sb += "<soap:Body>"
    sb += "<ns1:saveOrderInfoToCharacterSet xmlns:ns1=\"http://factory.service.cxf.kangmei.com/\">"
    sb += "<request>"
    sb += request_base64_encode(content)
    sb += "</request>"
    sb += "<characterSet>UTF-8</characterSet>"
    sb += "</ns1:saveOrderInfoToCharacterSet>"
    sb += "</soap:Body>"
    sb += "</soap:Envelope>"
    return sb


def insert_mid_prescription(prescription):
    message = {}
    session = get_local_session()[1]
    logging.info("插入中间表==>处方表：")
    prescription_info = Prescription(
        pres_num=prescription['pres_num'], pres_time=prescription['pres_time'], treat_card=prescription['treat_card'],
        reg_num=prescription['reg_num'], province=prescription['province'], city=prescription['city'],
        zone=prescription['zone'], addr_detail=prescription['addr_detail'], consignee=prescription['consignee'],
        con_tel=prescription['con_tel'], send_goods_time=prescription['send_goods_time'],
        user_name=prescription['user_name'], age=prescription['age'], gender=prescription['gender'],
        tel=prescription['tel'], is_suffering=prescription['is_suffering'], amount=prescription['amount'],
        suffering_num=prescription['suffering_num'], ji_fried=prescription['ji_fried'],
        per_pack_num=prescription['per_pack_num'], per_pack_dose=prescription['per_pack_dose'], type=prescription['type'],
        is_within=prescription['is_within'], other_pres_num=prescription.get('other_pres_num', prescription['pres_num']),
        special_instru=prescription['special_instru'], bed_num=prescription.get('bed_num'),
        hos_depart=prescription.get('hos_depart'), hospital_num=prescription.get('hospital_num'),
        disease_code=prescription.get('disease_code'), doctor=prescription['doctor'],
        prescript_remark=prescription['prescript_remark'], is_hos_addr=prescription['is_hos_addr'],
        medication_methods=prescription['medication_methods'],
        medication_instruction=prescription['medication_instruction'], source=prescription['source']
    )
    session.add(prescription_info)
    try:
        session.commit()
        message['status'] = 'success'
        logging.info("处方表成功插入中间表！")
    except SQLAlchemyError as e:
        session.rollback()
        logging.info("处方表插入中间表失败！")
        message['status'] = 'fail'
        logging.info(e)
    session.close()
    return message


def insert_mid_prescription_detail(pres_details):
    message = {}
    pres_detail_lists = []
    session = get_local_session()[1]
    logging.info("插入中间表==>处方明细表：")
    for pres_detail in pres_details:
        detail_info = PresDetails(
            pres_num=pres_detail['pres_num'], goods_num=pres_detail['goods_num'], medicines=pres_detail['medicines'],
            dose=pres_detail['dose'], unit=pres_detail['unit'], m_usage=pres_detail['m_usage'],
            goods_norms=pres_detail['goods_norms'], goods_orgin=pres_detail['goods_orgin'], remark=pres_detail['remark'],
            dose_that=pres_detail['dose_that'], unit_price=pres_detail.get('unit_price'),
            MedPerDay=pres_detail.get('MedPerDay'), MedPerDos=pres_detail.get('MedPerDos')
        )
        pres_detail_lists.append(detail_info)
    session.add_all(pres_detail_lists)
    try:
        session.commit()
        logging.info("处方详情插入中间处方明细表成功！")
        message['status'] = 'success'
    except SQLAlchemyError as e:
        session.rollback()
        logging.info("处方详情插入中间处方明细表失败！")
        message['status'] = 'fail'
        logging.info(e)
    session.close()
    return message


def update_consignee_status(pres_num):
    message = {}
    session = get_local_session()[1]
    logging.info("更新写入中间表状态：")
    is_write_mid_update = session.query(Consignee).filter(Consignee.pres_num == pres_num).update({'is_write_mid': 1})
    logging.info("==> Parameters:影响行：%s" % is_write_mid_update)
    try:
        session.commit()
        logging.info('写入中间表状态更新成功！')
        message['status'] = 'success'
    except SQLAlchemyError as e:
        session.rollback()
        logging.info('写入中间表状态更新失败！')
        message['status'] = 'fail'
        logging.info(e)
    session.close()
    return message
