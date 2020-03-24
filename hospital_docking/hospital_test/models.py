# coding:utf-8
"""
  Time : 2020-02-23 07:58:30
  Author : Vincent
  FileName: mysql_orm.py
  Software: PyCharm
  Last Modified by: Vincent
  Last Modified time: 2020-02-23 07:58:30
"""
import time
import logging
import json
from sqlalchemy import create_engine
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey, DateTime, TIMESTAMP, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()               # 表格对象基类


class Consignee(Base):
    """
    处方地址关联表类
    """
    __tablename__ = 'pres_consignee'
    pres_num = Column(String(50), nullable=False, primary_key=True, comment='医院处方号')
    addr_id = Column(Integer, nullable=False, comment='地址id')
    send_goods_time = Column(String(25), comment='送货时间')
    is_write_mid = Column(Integer, nullable=False, default=0, comment="是否写入中间表 0 未处理 1 已处理")


class Prescription(Base):
    """
    处方表类
    """
    __tablename__ = 'mid _prescriptions'
    pres_num = Column(String(50), nullable=False, primary_key=True, comment='处方单号')
    pres_time = Column(String(25), comment='处方生成时间')
    treat_card = Column(String(50), comment='诊疗卡号')
    reg_num = Column(String(50), comment='挂单号')
    province = Column(String(10), comment='省份')
    city = Column(String(10), comment='城市')
    zone = Column(String(10), comment='区')
    addr_detail = Column(String(120), comment='收货地址')
    consignee = Column(String(20), comment='收货人')
    con_tel = Column(String(50), comment='收货人电话')
    send_goods_time = Column(String(25), comment='送货时间')
    user_name = Column(String(20), comment='患者姓名')
    age = Column(Integer, comment='患者年龄')
    gender = Column(Integer, comment='患者性别')
    tel = Column(String(50), comment='患者电话')
    is_suffering = Column(Integer, comment='是否煎煮 取值范围：0 否，1 是')
    amount = Column(Integer, comment='数量')
    suffering_num = Column(Integer, comment='煎煮剂数')
    ji_fried = Column(Integer, comment='几煎')
    per_pack_num = Column(Integer, comment='每剂几包')
    per_pack_dose = Column(Integer, comment='每包多少ml')
    type = Column(Integer, comment='处方类型 0:中药，1:西药，2:膏方，3:丸剂，5:散剂，7:免煎颗粒')
    is_within = Column(Integer, comment='服用方式 0 内服，1 外用')
    other_pres_num = Column(String(50), nullable=False, comment='医院处方号')
    special_instru = Column(String(100), comment='处方特殊说明 诊断信息')
    bed_num = Column(String(50), comment='床位号')
    hos_depart = Column(String(50), comment='医院科室')
    hospital_num = Column(String(50), comment='住院号')
    disease_code = Column(String(50), comment='病区号')
    doctor = Column(String(50), comment='医生姓名')
    prescript_remark = Column(String(120), comment='处方备注')
    upload_status = Column(Integer, default=0, comment='上传状态(成功 -1,刚生成时为0,每失败一次+1)')
    description = Column(String(100), comment='上传描述')
    upload_time = Column(TIMESTAMP(timezone=False), comment='上传时间')
    order_id = Column(String(36), comment='康美订单id')
    is_hos_addr = Column(Integer, comment='地址类型 0 未知,1送医院,2 送患者家里')
    medication_methods = Column(String(50), comment='用药方法')
    medication_instruction = Column(String(50), comment='用药指导')
    source = Column(Integer, comment='0 门诊 1 住院')

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        if "keys" in dict:
            del dict['keys']
        if "metadata" in dict:
            del dict['metadata']
        return dict

    def keys(self):
        '''当对实例化对象使用dict(obj)的时候, 会调用这个方法,这里定义了字典的键, 其对应的值将以obj['name']的形式取,
        但是对象是不可以以这种方式取值的, 为了支持这种取值, 可以为类增加这个方法'''
        return ('addr_detail', 'age', 'amount', 'bed_num', 'city', 'con_tel', 'consignee', 'disease_code', 'doctor',
                'gender', 'hos_depart', 'hospital_num', 'is_hos_addr', 'is_suffering', 'is_within', 'ji_fried',
                'keys', 'medication_instruction', 'medication_methods', 'metadata', 'order_id', 'other_pres_num',
                'per_pack_dose', 'per_pack_num', 'pres_num', 'pres_time', 'prescript_remark', 'province',
                'reg_num', 'send_goods_time', 'source', 'special_instru', 'suffering_num', 'tel', 'treat_card',
                'type', 'upload_status', 'upload_time', 'user_name', 'zone')

    def __getitem__(self, item):
        '''内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值'''
        return getattr(self, item)


class PresDetails(Base):
    """
    处方明细(药材)表类
    """
    __tablename__ = 'mid_prescription_details'
    pres_detail_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True, comment='处方详情id')
    pres_num = Column(String(36), nullable=False, comment='处方单号')
    goods_num = Column(String(100), nullable=False, comment='药材编号')
    medicines = Column(String(100), nullable=False, comment='药品名')
    dose = Column(String(10), comment='剂量')
    unit = Column(String(50), comment='单位')
    m_usage = Column(String(100), comment='药品特殊煎法')
    goods_norms = Column(String(100), comment='药品规格')
    goods_orgin = Column(String(100), comment='药品产地')
    remark = Column(String(100), comment='备注')
    dose_that = Column(String(100), comment='药品注意事项说明')
    unit_price = Column(Float, server_default='0.00', comment='医院药品销售单价')
    MedPerDos = Column(String(20), comment='用量(剂量)eg:2片/次(每次两片)')
    MedPerDay = Column(String(20), comment='执行频率(频次)（eg:一日3次）')


class Address(Base):
    """
    地址 custom_addr 表类
    """
    __tablename__ = 'custom_addr'
    addr_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True, comment='地址id')
    custom_num = Column(String(50), nullable=False, comment='患者id,标识唯一患者')
    consignee = Column(String(30), comment='收货人')
    con_tel = Column(String(50), comment='收货人电话')
    province = Column(String(10), comment='省份')
    city = Column(String(10), comment='城市')
    zone = Column(String(10), comment='区县')
    addr_detail = Column(String(50), nullable=False, comment='详细地址')
    is_hos_addr = Column(Integer, comment='地址类型 0 未知,1送医院,2 送患者家里')
    auto_state = Column(Integer, default=0, comment='是否默认地址')


def mysql_connect(sql):
    """
    使用原生SQL查询对方数据库视图，返回查询数据
    :return: data
    engine = create_engine('dialect+driver://username:password@host:port/database')
        [dialect -- 数据库类型, driver -- 数据库驱动选择, username -- 数据库用户名,
        password -- 用户密码, host 服务器地址, port 端口, database 数据库]
    """
    conn_pool = create_engine(
        # "mysql+pymysql://root:KM*021191@localhost:3306/zhyf?charset=utf8",
        "mysql+mysqlconnector://root:KM*021191@localhost:3306/addr_test?charset=utf8",
        max_overflow=0,         # 超过连接池大小外最多创建的连接
        pool_size=5,            # 连接池大小
        pool_timeout=30,        # 池中没有线程最多等待的时间，否则报错
        pool_recycle=3600       # 多久之后对线程池中的线程进行一次连接的回收（重置）
        )
    conn = conn_pool.raw_connection()   # 从连接池中获取1个连接,开始连接
    cursor = conn.cursor()
    logging.info('==> executing:%s' % sql)
    cursor.execute(sql)
    print(cursor.description)
    data = cursor.fetchall()
    logging.info("==> Parameters:")
    for da in data:
        logging.info(da)
    cursor.close()
    conn.close()
    return data


def mysql_connect_fatchall(sql):
    """
    使用原生SQL查询对方数据库视图，返回查询数据
    :return: data
    engine = create_engine('dialect+driver://username:password@host:port/database')
        [dialect -- 数据库类型, driver -- 数据库驱动选择, username -- 数据库用户名,
        password -- 用户密码, host 服务器地址, port 端口, database 数据库]
    """
    conn_pool = create_engine(
        # "mysql+pymysql://root:KM*021191@localhost:3306/zhyf?charset=utf8",
        "mysql+mysqlconnector://root:KM*021191@localhost:3306/addr_test?charset=utf8",
        max_overflow=0,         # 超过连接池大小外最多创建的连接
        pool_size=5,            # 连接池大小
        pool_timeout=30,        # 池中没有线程最多等待的时间，否则报错
        pool_recycle=3600       # 多久之后对线程池中的线程进行一次连接的回收（重置）
        )
    conn = conn_pool.raw_connection()   # 从连接池中获取1个连接,开始连接
    cursor = conn.cursor()
    logging.info('==> executing:%s' % sql)
    cursor.execute(sql)
    columns = [col[0] for col in cursor.description]  # 拿到对应的字段列表
    data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    logging.info("==> Parameters:")
    for da in data:
        logging.info(da)
    cursor.close()
    conn.close()
    return data


def get_local_session(sql=""):
    """
    初始化数据库连接,返回 engine 和 session
    :return: (engine,session)
    """
    engine = create_engine(
        # "mysql+pymysql://root:KM*021191@localhost:3306/zhyf?charset=utf8",
        "mysql+mysqlconnector://root:KM*021191@localhost:3306/zhyf_host?charset=utf8",
        max_overflow=0,         # 超过连接池大小外最多创建的连接
        pool_size=5,            # 连接池大小
        pool_timeout=30,        # 池中没有线程最多等待的时间，否则报错
        pool_recycle=3600       # 多久之后对线程池中的线程进行一次连接的回收（重置）
        )
    if sql:
        en = engine.raw_connection()
        cursor = en.cursor()
        logging.info('==> executing:%s' % sql)
        cursor.execute(sql)
        data = cursor.fetchall()
        logging.info("==> Parameters:")
        for da in data:
            logging.info(da)
        cursor.close()
        en.close()
        return data
    else:
        DBSession = sessionmaker(bind=engine)  # 创建会话的类
        session = DBSession()
        return engine, session


def save_custom_addr(dict_data):
    """
    保存地址信息
    :param dict_data: 前端提交的地址信息字典
    :return:
    """
    message = {}
    addr_session = get_local_session()[1]
    addr_query = addr_session.query(Address).filter(
        Address.custom_num == dict_data['custom_num']).order_by(Address.addr_id)
    addr_query_sql = str(addr_query.statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}))
    logging.info('==> executing:%s' % addr_query_sql)
    addr_res = addr_query.all()
    # logging.info("==> Parameters:" + json.dumps(addr_res, ensure_ascii=False))
    logging.info("==> Parameters:%s", addr_res)
    if len(addr_res) < 5:
        addr_information = Address(custom_num=dict_data['custom_num'], consignee=dict_data['consignee'],
                                   con_tel=dict_data['con_tel'], province=dict_data['province'],
                                   city=dict_data['city'], zone=dict_data['zone'], addr_detail=dict_data['addr_detail'],
                                   is_hos_addr=dict_data.get('is_hos_addr'))
        addr_session.add(addr_information)
        logging.info("连接数据库保存地址：")
        try:
            addr_session.commit()  # 尝试提交数据库事务
            logging.info('地址信息保存成功！')
            message['status'] = 'success'
        except SQLAlchemyError as e:
            addr_session.rollback()
            logging.info('地址信息保存失败！')
            logging.info(e)
            message['status'] = 'fail'
            message['message'] = str(e) + "\n请联系管理员！"
    else:
        message['status'] = 'fail'
        message['message'] = '每位患者最多保存5个地址！'
    addr_session.close()
    return message


def del_custom_addr(addr_id):
    """
    根据地址 id 删除记录
    :param addr_id:
    :return:
    """
    message = {}
    session = get_local_session()[1]
    logging.info("删除联系人：")
    addr = session.query(Address).filter(Address.addr_id == addr_id).delete()
    logging.info("==> Parameters:" + json.dumps(addr, ensure_ascii=False))
    try:
        session.commit()
        message['status'] = 'success'
        logging.info('联系人删除成功！')
    except SQLAlchemyError as e:
        session.rollback()
        logging.info('联系人删除失败！')
        logging.info(e)
        message['status'] = 'fail'
        message['message'] = str(e) + "\n请联系管理员！"
    session.close()
    return message


def save_pres_addr(pres_addr):
    """
    根据地址 id 和 处方号 pres_num 做处方地址关联
    :param pres_addr:
    :return:
    """
    message = {}
    consignee_session = get_local_session()[1]
    consignee_info = Consignee(pres_num=pres_addr['pres_num'], addr_id=pres_addr['addr_id'],
                               send_goods_time=pres_addr['send_goods_time'])
    logging.info("连接数据库关联处方和地址：")
    consignee_session.add(consignee_info)
    try:
        consignee_session.commit()  # 尝试提交数据库事务
        logging.info('处方地址关联成功！')
        message['status'] = 'success'
    except SQLAlchemyError as e:
        consignee_session.rollback()
        logging.info('处方关联失败！')
        logging.info(e)
        message['status'] = 'fail'
        message['message'] = str(e) + "\n请联系管理员！"
    consignee_session.close()
    return message


def update_address(new_addr):
    message = {}
    session = get_local_session()[1]
    logging.info("更新地址：")
    addr_update = session.query(Address).filter(Address.addr_id == new_addr['addr_id']).update({
        'consignee': new_addr['consignee'], 'con_tel': new_addr['con_tel'], 'province': new_addr['province'],
        'city': new_addr['city'], 'zone': new_addr['zone'], 'addr_detail': new_addr['addr_detail']})
    logging.info("==> Parameters:" + json.dumps(addr_update, ensure_ascii=False))
    try:
        session.commit()
        message['status'] = 'success'
        logging.info('地址更新成功！')
    except SQLAlchemyError as e:
        session.rollback()
        logging.info('地址更新失败！')
        logging.info(e)
        message['status'] = 'fail'
        message['message'] = str(e) + "\n请联系管理员！"
    session.close()
    return message


def update_addr_state(addr_id):
    """
    处方地址关联完，更新地址状态
    :param addr_id:
    :return:
    """
    message = {}
    session = get_local_session()[1]
    logging.info("更新地址状态：")
    auto_state_update = session.query(Address).filter(Address.addr_id == addr_id).update({'auto_state': 1})
    # logging.info("==> Parameters:" + json.dumps(auto_state_update, ensure_ascii=False))
    try:
        session.commit()
        message['status'] = 'success'
        logging.info('地址状态更新成功！')
    except SQLAlchemyError as e:
        session.rollback()
        logging.info('地址状态更新失败！')
        logging.info(e)
        message['status'] = 'fail'
        message['message'] = str(e) + "\n请联系管理员！"
    session.close()
    return message


def update_prescription_statues(pres_num, order_id='', describe=''):
    """
    更新处方上传状态 成功 -1 失败 +1
    :param pres_num:
    :param order_id:
    :param describe:
    :return:
    """
    session = get_local_session()[1]
    if order_id:
        up = session.query(Prescription).filter(Prescription.pres_num == pres_num).update({
            Prescription.upload_status: '-1', Prescription.order_id: order_id, Prescription.description: describe,
            Prescription.upload_time: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))})
    else:
        up = session.query(Prescription).filter(Prescription.pres_num == pres_num).update({
            Prescription.upload_status: Prescription.upload_status + 1, Prescription.description: describe})
    try:
        session.commit()
        logging.info("处方号：%s 上传状态更新成功！" % pres_num)
    except SQLAlchemyError as e:
        session.rollback()
        logging.info('处方号： %s 上传状态更新失败！' % pres_num)
        logging.info(e)
    session.close()


def init_db(en):
    """
    根据类创建数据库表
    :return:
    """
    Base.metadata.create_all(en)


def drop_db(en):
    """
    根据类 删除数据库表
    :return:
    """
    Base.metadata.drop_all(en)  # 这行代码很关键哦！！ 读取继承了Base类的所有表在数据库中进行删除表


if __name__ == '__main__':
    es = get_local_session()
    # init_db(es[0])                    # 执行创建
    drop_db(es[0])
