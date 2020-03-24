# coding:utf-8
import time
import logging
from sqlalchemy.dialects import mysql
from hospital_test.models import Prescription, mysql_connect, get_local_session, mysql_connect_fatchall
from timer_work.HosPrescriptionService import upload_prescription, insert_mid_prescription, \
    insert_mid_prescription_detail, update_consignee_status
from hospital_test.handling import sql_to_dict, get_config
from timer_work import zhenzismsclient as msgClient


# Create your views here.
def time_out():
    format_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print(format_time)


lastSendTime = 0
SMS_SEND_INTERVAL = 600000


def upload_prescription_job():
    """
    定时轮询上传处方和写入中间表
    :return:
    """
    logging.info("上传处方定时任务开始================================")
    prescription_lists = get_pre_lists_by_statues(0, 10000)
    if prescription_lists:
        upload_prescriptions(prescription_lists)
        check_and_alert()
    else:
        logging.info("本次无未上传处方！")
    insert_mid_by_pres_consignee()
    logging.info("上传处方定时任务结束================================")


def get_pre_lists_by_statues(start_status, end_status):
    """
    在中间表中根据处方状态查询需要上传的处方
    :param start_status:
    :param end_status:
    :return:
    """
    session = get_local_session()[1]
    pre_lists_query = session.query(Prescription).filter(Prescription.upload_status.between(start_status, end_status))
    sql = str(pre_lists_query.statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}))
    logging.info('==> executing:%s' % sql)
    pre_lists = pre_lists_query.all()
    logging.info("==> Parameters:%s" % pre_lists)
    return pre_lists


def upload_prescriptions(pre_lists):
    """
    上传处方至智慧药房，成功后把中间表的upload_status置为-1，否则该值+1
    :param pre_lists: 需要上传的处方列表
    :return:
    """
    logging.info("开始批量上传 %s 个处方" % (len(pre_lists)))
    for pres_object in pre_lists:
        upload_prescription(pres_object)


def check_and_alert():
    """
    查询中间表中上传多次的处方并发送告警信息
    :return:
    """
    global lastSendTime
    fail_prescription_lists = get_pre_lists_by_statues(0, 10000)          # 在中间表中根据处方状态查询上传次数大于0的处方
    if fail_prescription_lists:
        for i in range(len(fail_prescription_lists)):
            fail_pres_num = fail_prescription_lists[i].pres_num
            message_send_counts = fail_prescription_lists[i].upload_status
            fail_reason = fail_prescription_lists[i].description
            detail = '科室：' + fail_prescription_lists[i].hos_depart + '--开单医生：' + \
                     fail_prescription_lists[i].doctor + '--患者姓名' + fail_prescription_lists[i].user_name
            options = ['appID', 'appSecret', 'messageServiceUrl', 'retryTimes', 'isContact', 'emergencyContact']
            msg_info = get_config('message', options)
            if msg_info['isContact'] and (message_send_counts <= int(msg_info['retryTimes'])) and (
                    (lastSendTime == 0) or (lastSendTime > 0 and time.time() - lastSendTime >= SMS_SEND_INTERVAL)):
                mgclient = msgClient.ZhenziSmsClient(msg_info['messageServiceUrl'], msg_info['appID'],
                                                     msg_info['appSecret'])
                me = "{}处方上传失败！处方号：{}-原因：{}---详情：{}."
                logging.info('发送提醒信息：%s' % me.format(get_config('hospital', 'companyName'), fail_pres_num,
                                                     fail_reason, detail))
                result = mgclient.send(msg_info['emergencyContact'], me.format(get_config('hospital', 'companyName'),
                                                                               fail_pres_num, fail_reason, detail))
                lastSendTime = time.time()
                logging.info("结果：%s" % result)
    else:
        return


def insert_mid_by_pres_consignee():
    """
    将未写入中间表的地址与处方信息合并后插入中间表
    :return:
    """
    prescriptions = []
    pres_details = []
    pre_sql = ''
    detail_sql = ''
    pres_consignee_lists = find_un_write_pres_consignee()
    if pres_consignee_lists:
        for pres_consignee_list in pres_consignee_lists:
            del pres_consignee_list['addr_id']
            del pres_consignee_list['is_write_mid']
            prefix = pres_consignee_list['pres_num'][:3]
            if prefix == 'MZ_':
                pre_sql += "select p.pres_num,p.pres_time,p.treat_card,p.reg_num,p.username as user_name,p.age," \
                           "p.gender,p.tel,p.is_suffering,p.amount,p.type,p.is_within," \
                          "p.is_suffering*p.amount*p.per_pack_num as suffering_num,p.per_pack_num,p.per_pack_dose," \
                          "p.ji_fried,p.special_instru,p.hos_depart,p.doctor,p.remark as prescript_remark," \
                          "p.medication_methods,p.medication_instruction,(select 0) as source " \
                           "from MZ_hosp_prescriptions_view p " \
                          "where p.pres_num in ('"+pres_consignee_list['pres_num']+"');"
                detail_sql += "select pd.pres_num as pres_num,pd.medicines,pd.dose,pd.unit,pd.goods_num,pd.dose_that," \
                              "pd.remark,pd.m_usage,pd.goods_norms,pd.goods_orgin from MZ_details_view pd " \
                              "where pd.pres_num in ('"+pres_consignee_list['pres_num']+"');"
            elif prefix == 'ZY_':
                pre_sql += "select p.pres_num,p.pres_time,p.treat_card,p.reg_num,p.username as user_name,p.age," \
                           "p.gender,p.tel,p.is_suffering,p.amount,p.type,p.is_within," \
                           "p.is_suffering*p.amount*p.per_pack_num as suffering_num,p.per_pack_num,p.per_pack_dose," \
                           "p.ji_fried,p.special_instru,p.hos_depart,p.bed_num,p.hospital_num,p.disease_code,p.doctor," \
                           "p.remark as prescript_remark,p.medication_methods,p.medication_instruction," \
                           "(select 1) as source from ZY_hosp_prescriptions_view p " \
                           "where p.pres_num in ('"+pres_consignee_list['pres_num']+"');"
                detail_sql += "select pd.pres_num as pres_num,pd.medicines,pd.dose,pd.unit,pd.goods_num,pd.dose_that," \
                              "pd.remark,pd.m_usage,pd.goods_norms,pd.goods_orgin from ZY_details_view pd " \
                              "where pd.pres_num in ('" + pres_consignee_list['pres_num'] + "');"
            # pre_res = mysql_connect(pre_sql)
            # prescription = dict(zip(sql_to_dict(pre_sql), list(pre_res[0])))
            prescription = mysql_connect_fatchall(pre_sql)[0]
            # print('sql_to_dict(pre_sql):', sql_to_dict(pre_sql))
            # print('pre_res:', pre_res)
            # print('list(pre_res):', list(pre_res[0]))
            # print('pres_dict:', pres_dict)
            if prescription:
                # detail_res = mysql_connect(detail_sql)
                detail_res = mysql_connect_fatchall(detail_sql)
                if detail_res:
                    # print('pres_consignee_list:', pres_consignee_list)
                    prescription.update(pres_consignee_list)
                    # print(prescription)
                    prescriptions.append(prescription)
                    for detail_re in detail_res:
                        # detail_dict = dict(zip(sql_to_dict(detail_sql), detail_re))
                        # print(detail_dict)
                        pres_details.append(detail_re)
                    insert_res = insert_prescriptions(prescriptions, pres_details)
                    if not insert_res:
                        message = "将处方插入中间表发生异常！"
                        logging.error(message)
                        send_remind_message(pres_consignee_list['pres_num'], message)
                else:
                    message = "从医院查询的处方详情为空！"
                    logging.error(message + "处方号：%s" % pres_consignee_list['pres_num'])
                    send_remind_message(pres_consignee_list['pres_num'], message)
            else:
                message = "从医院查询的处方为空！"
                logging.error(message + "处方号：%s" % pres_consignee_list['pres_num'])
                send_remind_message(pres_consignee_list['pres_num'], message)
    else:
        return


def find_un_write_pres_consignee():
    """
    获取在关联表录入地址，但未写入中间表的记录 is_write_mid=0
    :return:
    """
    uw_records = []
    uw_sql = "select pc.pres_num, pc.addr_id, ca.province, ca.city, ca.zone, ca.addr_detail, ca.consignee," \
             " ca.con_tel, pc.send_goods_time, ca.is_hos_addr, pc.is_write_mid " \
             "from pres_consignee pc, custom_addr ca " \
             "where pc.addr_id = ca.addr_id and pc.is_write_mid = 0"
    for record in get_local_session(uw_sql):
        uw_records.append(dict(zip(sql_to_dict(uw_sql), list(record))))
    return uw_records


def insert_prescriptions(prescription_lists, pres_detail_lists):
    logging.info("将要插入中间表的处方信息：%s", prescription_lists)
    logging.info("将要插入中间表的处方详情：%s", pres_detail_lists)
    for i in range(len(prescription_lists)):
        pres_res = insert_mid_prescription(prescription_lists[i])
        detail_res = insert_mid_prescription_detail(pres_detail_lists)
        if pres_res['status'] == 'success' and detail_res['status'] == 'success':
            mid_res = update_consignee_status(prescription_lists[i]['pres_num'])
            if mid_res['status'] == 'success':
                return True
        else:
            return False


def send_remind_message(pres_num, message):
    options = ['appID', 'appSecret', 'messageServiceUrl', 'emergencyContact']
    msg_info = get_config('message', options)
    logging.info("msg_info:%s" % msg_info)
    hos_name = get_config('hospital', 'companyName')
    msg_client = msgClient.ZhenziSmsClient(msg_info['messageServiceUrl'], msg_info['appID'], msg_info['appSecret'])
    me = "-{}-" + message + "处方号：{} ."
    for tel in msg_info['emergencyContact'].split(','):
        logging.info('发送提醒信息：%s 到 %s' % (me.format(hos_name, pres_num), tel))
        result = msg_client.send(tel, me.format(hos_name, pres_num))
        logging.info("结果：%s" % result)


