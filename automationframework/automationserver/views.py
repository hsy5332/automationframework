# conding : utf-8
import os
from django.shortcuts import render
from django.http import HttpResponse


# 请求示例
def index(request):
    return HttpResponse("这是一个简单的示例")


# 获取本地adb的设备信息
def adb_devices(request):
    take_devices_list = []
    take_devices_info = os.popen("adb devices")
    for i in take_devices_info:
        if 'device' in i and '5555' in i:
            take_devices_list.append(i.split('\t')[0])

    return HttpResponse(take_devices_list[0])

def testone(request):
    return adb_devices("GET")