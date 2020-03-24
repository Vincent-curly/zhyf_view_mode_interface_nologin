import json
import logging
import time

from django.core.paginator import Paginator
from django.core import serializers
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from sqlalchemy.dialects import mysql

from hospital_test.handling import sql_to_dict, get_config, DateEncoder
from hospital_test.models import Consignee, Address, Prescription, init_db, \
    mysql_connect, save_custom_addr, del_custom_addr, save_pres_addr, get_local_session, update_addr_state, \
    update_address
from hospital_test.pagination import Pagination

# Create your views here.
log_path = './log'
log_name = log_path + '//' + time.strftime('%Y%m%d', time.localtime()) + '.log'
logging.basicConfig(level=logging.DEBUG, filename=log_name,
                        format="%(asctime)s %(name)s:%(levelname)s:%(module)s:%(funcName)s:"
                               "%(processName)s:%(process)d:%(message)s")
logging.getLogger(__name__).setLevel(logging.DEBUG)

es = get_local_session()
init_db(es[0])


def entry_addr(request):
    pres_num = request.GET['pres_num']
    custom_num = request.GET['custom_num']
    if pres_num.split('_')[0] == 'MZ':
        sql = "select p.treat_card,p.username,p.tel from MZ_hosp_prescriptions_view p " \
              "where p.pres_num ='"+pres_num+"'and p.treat_card ='"+custom_num+"';"
    else:
        sql = "select p.treat_card,p.username,p.tel from ZY_hosp_prescriptions_view p " \
              "where p.pres_num ='"+pres_num+"'and p.treat_card ='"+custom_num+"';"
    result = mysql_connect(sql)
    context = dict(zip(sql_to_dict(sql), list(result[0])))
    context['pres_num'] = pres_num
    context['custom_num'] = custom_num
    context['addr_lists'] = get_addr(custom_num)
    context['pres_addr_info'] = get_pres_addr(pres_num)
    logging.info("context:%s", context)
    return render(request, 'hospital_test/entry_addr.html', context)


@csrf_exempt
def save_addr(request):
    # POST 请求,获取用户提交的地址信息
    addr_dict = {'custom_num': request.POST.get('custom_num'), 'consignee': request.POST.get('consignee'),
                 'con_tel': request.POST.get("con_tel"), 'province': request.POST.get("province"),
                 'city': request.POST.get("city"), 'zone': request.POST.get("zone"),
                 'addr_detail': request.POST.get("addr_str"), 'is_hos_addr': request.POST.get("is_hos_addr")}
    save_res = save_custom_addr(addr_dict)
    logging.info(save_res)
    return HttpResponse(json.dumps(save_res), content_type='application/json')


@csrf_exempt
def del_addr(request):
    add_id = request.POST.get('addr_id')
    del_res = del_custom_addr(add_id)
    logging.info(del_res)
    return HttpResponse(json.dumps(del_res), content_type='application/json')


@csrf_exempt
def save_addr_to_pres(request):
    consignee_dict = {'pres_num': request.POST.get('pres_num'), 'addr_id': request.POST.get('addr_id'),
                      'send_goods_time': request.POST.get('send_goods_time')}
    save_res = save_pres_addr(consignee_dict)
    if save_res['status'] == 'success':
        up_addr_res = update_addr_state(request.POST.get('addr_id'))
        if up_addr_res['status'] == 'success':
            pass
    else:
        pass
    return HttpResponse(json.dumps(save_res), content_type='application/json')


@csrf_exempt
def get_hos_properties(request):
    is_hos_addr = request.POST.get('is_hos_addr')
    options = ['companyprovince', 'companycity', 'companyzone', 'companyaddress', 'companyname', 'companytel']
    hos_properties = get_config('hospital', options)
    logging.info('医院信息：%s' % (json.dumps(hos_properties, ensure_ascii=False)))
    return HttpResponse(json.dumps(hos_properties), content_type='application/json')


@csrf_exempt
def update_addr(request):
    addr_dict = {'addr_id': request.POST.get('addr_id'), 'consignee': request.POST.get('consignee'),
                 'con_tel': request.POST.get("con_tel"), 'province': request.POST.get("province"),
                 'city': request.POST.get("city"), 'zone': request.POST.get("zone"),
                 'addr_detail': request.POST.get("addr_detail")}
    addr_update_res = update_address(addr_dict)
    if addr_update_res['status'] == 'success':
        up_addr_res = update_addr_state(request.POST.get('addr_id'))
        if up_addr_res['status'] == 'success':
            pass
        else:
            pass
    return HttpResponse(json.dumps(addr_update_res), content_type='application/json')


def list_prescription(request):
    """
    context = {'pres_info': get_prescriptions()}
    logging.info("context:%s", context)
    return render(request, 'hospital_test/list.html', context)
    """
    return render(request, 'hospital_test/list.html')


@csrf_exempt
def list_pres(request):
    upload_status = request.POST.get('upload_status')
    pres_num = request.POST.get('pres_num')
    order_id = request.POST.get('order_id')
    user_name = request.POST.get('user_name')
    doctor = request.POST.get('doctor')
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')
    page = request.POST.get('page', 1)
    param = []
    session = get_local_session()[1]
    if pres_num:
        param.append(Prescription.pres_num == pres_num)
    if order_id:
        param.append(Prescription.order_id == order_id)
    if user_name:
        param.append(Prescription.user_name == user_name)
    if doctor:
        param.append(Prescription.doctor == doctor)
    if start_time:
        param.append(Prescription.pres_time >= start_time)
    if end_time:
        param.append(Prescription.pres_time <= end_time)
    if upload_status:
        param.append(Prescription.upload_status == upload_status)
    for item in param:
        logging.info(item)
    if len(param) == 1 and upload_status == 'all':
        prescription_query = session.query(Prescription)
    else:
        prescription_query = session.query(Prescription).filter(*param)
    sql = str(prescription_query.statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}))
    logging.info('==> executing:%s' % sql)
    prescription_data = prescription_query.all()
    logging.info("==> Parameters:%s" % prescription_data)
    '''
    paginator = Paginator(prescription_data, 10)
    print(paginator)
    pag_num = paginator.num_pages       # 获取总页数
    print(pag_num)
    total_rows = paginator.count        # 获取总的记录数
    print(total_rows)
    current_page_num = int(page)        # 当前页数
    current_page = paginator.page(current_page_num)     # 获取当前页的数据
    print(current_page)
    pag_range = []
    if pag_num < 11:
        pag_range = list(paginator.page_range)        # 页数小于11，获取页码列表
    elif pag_num > 11:
        if current_page_num < 6:
            pag_range = list(range(1, 11))        # 当前页码小于6，设置页码列表为1-10 `
        elif current_page_num > pag_num - 5:
            pag_range = list(range(pag_num - 9, pag_num + 1))
        else:
            pag_range = list(range(current_page_num - 5, current_page_num + 5))       # 当前页码+5大于最大页数时
    '''
    print(prescription_data[0])
    paginator = Pagination(page, prescription_data)
    print(paginator)
    pag_num = paginator.all_pager  # 获取总页数
    print(pag_num)
    total_rows = paginator.all_count  # 获取总的记录数
    print(total_rows)
    print(paginator.page_html())
    page_data = prescription_data[paginator.start:paginator.end]
    msgs = []
    for msg in page_data:
        msgs.append(msg.to_json())
    msgs.append({'current_page_num': page, 'total_rows': total_rows, 'page_html': paginator.page_html()})
    print(msgs)
    return HttpResponse(json.dumps(msgs, cls=DateEncoder, ensure_ascii=False), content_type='application/json')


def get_addr(custom_num):
    session = get_local_session()[1]
    addr_lists = session.query(Address).filter(Address.custom_num == custom_num).order_by(Address.addr_id).all()
    session.close()
    return addr_lists


def get_pres_addr(pres_num):
    session = get_local_session()[1]
    pres_addr_info = session.query(Consignee).filter(Consignee.pres_num == pres_num).all()
    session.close()
    return pres_addr_info

