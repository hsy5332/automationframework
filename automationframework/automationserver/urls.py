# coding : utf-8
from django.conf.urls import url
from automationserver import views
from django.conf import settings

urlpatterns = [
    url(r'^index', views.index),  # 示例
    url(r'^devicelist', views.get_devices),  # 获取设备
    url(r'^connectdevices', views.connect_devices),  # 连接设备
    url(r'^disconnectdevice', views.disconnection_devices)  # 断开设备
    # url(r'^testone', views.testone)
]
