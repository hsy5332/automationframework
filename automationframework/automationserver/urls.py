# coding : utf-8
from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  url(r'^index', views.index),  # 示例
                  url(r'^devicelist', views.get_devices),  # 获取设备
                  url(r'^connectdevices', views.connect_devices),  # 连接设备
                  url(r'^disconnectdevice', views.disconnection_devices),  # 断开设备
                  url(r'^runcase', views.run_automation_file),  # 执行自动化用例接口
                  # url(r'^testone', views.testone)
              ] + static(settings.STATIC_URL, docment_root=settings.STATIC_ROOT)
