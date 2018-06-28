# conding : utf-8
import os
from django.shortcuts import render
from django.http import HttpResponse


# 请求示例
def index(request):
    return HttpResponse("这是一个简单的示例")


# 获取本地adb的设备信息
def adb_devices(request):
    take_devices_info = os.system("adb devices")
    return HttpResponse(take_devices_info)

def testone(request):
    return adb_devices("GET")