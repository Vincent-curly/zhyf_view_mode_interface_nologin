"""hospital_docking URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from apscheduler.scheduler import Scheduler
from hospital_test.views import entry_addr, save_addr, del_addr, save_addr_to_pres, get_hos_properties, update_addr, \
    list_prescription, list_pres
from timer_work.views import time_out, upload_prescription_job


sched = Scheduler()
@sched.interval_schedule(minutes=1)
def my_job():
    time_out()
    upload_prescription_job()


sched.start()
urlpatterns = [
    path('admin/', admin.site.urls),
    path('customAddr/entry_addr.do', entry_addr),
    path('customAddr/save_addr.do', save_addr),
    path('customAddr/delCustomAddr.do', del_addr),
    path('customAddr/savePresAddr.do', save_addr_to_pres),
    path('customAddr/getHosProperties.do', get_hos_properties),
    path('customAddr/update_addr.do', update_addr),
    path('prescriptionManeger/list.html', list_prescription),
    path('prescriptionManeger/query_prescription', list_pres),
]

