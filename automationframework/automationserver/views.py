# conding : utf-8
import os
import time
import json
from django.shortcuts import render
from django.http import HttpResponse


# 请求示例
def index(request):
    return HttpResponse("这是一个简单的示例")


def token(token):
    try:
        if int(token) + 86400 > int(time.time()):  # 86400是一天的时间戳
            return True
        else:
            return False
    except:
        return False


# 获取本地adb的设备信息
def get_devices(request):
    if request.POST:
        if token(request.POST['token']):
            take_devices_list = []  # 获取设备信息列表
            take_devices_info = os.popen("adb devices")
            for i in take_devices_info:
                if 'device' in i and 'attached' not in i:
                    take_devices_list.append(i.split('\t')[0])
            return_take_devices = {"code": "200", "msg": "success", "data": take_devices_list}
            return HttpResponse(json.dumps(return_take_devices))
        else:
            get_devices_token_error = {"code": "-11", "msg": "token过期", "data": {}}
            return HttpResponse(json.dumps(get_devices_token_error))
    else:
        get_devices_request_error = {"code": "-12", "msg": "请求方式错误", "data": {}}
        return HttpResponse(json.dumps(get_devices_request_error))


# 连接设备
def connect_devices(request):
    if request.POST:
        if token(request.POST['token']):
            pass
        else:
            connect_devices_token_error = {"code": "-11", "msg": "token过期", "data": {}}
            return HttpResponse(json.dumps(connect_devices_token_error))
    else:
        connect_devices_error = {"code": "-12", "msg": "请求方式错误", "data": {}}
        return HttpResponse(json.dumps(connect_devices_error))


# 断开设备连接
def disconnection_devices(request):
    if request.POST:
        if token(request.POST['token']):
            pass
        else:
            disconnection_devices_token_error = {"code": "-11", "msg": "token过期", "data": {}}
            return HttpResponse(json.dumps(disconnection_devices_token_error))
    else:
        disconnection_devices_error = {"code": "-12", "msg": "请求方式错误", "data": {}}
        return HttpResponse(json.dumps(disconnection_devices_error))
