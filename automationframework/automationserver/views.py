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
        try:
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
        except:
            get_devices_request_error = {"code": "-13", "msg": "请求参数错误,请检查参数。", "data": {}}
            return HttpResponse(json.dumps(get_devices_request_error))
    else:
        get_devices_error = {"code": "-12", "msg": "请求方式错误", "data": {}}
        return HttpResponse(json.dumps(get_devices_request_error))


# 连接设备
def connect_devices(request):
    if request.POST:
        try:
            if token(request.POST['token']):
                connect_cmd_list = []  # 存放执行cmd命令得到的数据
                connect_devices_cmd = os.popen("adb connect %s" % request.POST['deviceid'])
                for connect_cmd in connect_devices_cmd:
                    connect_cmd_list.append(connect_cmd)
                if "unable" in connect_cmd_list:
                    return_miss_device_info = {"code": "200", "msg": "连接设备失败请检查设备是否和pc在一个局域网内", "data": {}}
                    return HttpResponse(json.dumps(return_miss_device_info))
                else:
                    get_device_list = []  # 存放获取到的设备ID
                    for get_device in os.popen("adb devices"):
                        if 'device' in get_device and 'attached' not in get_device:
                            get_device_list.append(get_device.split('\t')[0])
                    return_connect_devices = {"code": "200", "msg": "连接设备成功", "data": get_device_list}
                    return HttpResponse(json.dumps(return_connect_devices))
            else:
                connect_devices_token_error = {"code": "-11", "msg": "token过期", "data": {}}
                return HttpResponse(json.dumps(connect_devices_token_error))
        except:
            connect_devices_request_error = {"code": "-13", "msg": "请求参数错误,请检查参数。", "data": {}}
            return HttpResponse(json.dumps(connect_devices_request_error))
    else:
        connect_devices_error = {"code": "-12", "msg": "请求方式错误", "data": {}}
        return HttpResponse(json.dumps(connect_devices_error))


# 断开设备连接
def disconnection_devices(request):
    if request.POST:
        try:
            if token(request.POST['token']):
                disconnection_cmd_list = []
                get_device_list = []
                for disconnection_cmd in os.popen("adb disconnect %s" % request.POST['deviceid']):
                    disconnection_cmd_list.append()
                for get_device in os.popen("adb devices"):
                    if 'device' in get_device and 'attached' not in get_device:
                        get_device_list.append(get_device.split('\t')[0])
                if "disconnected" in disconnection_cmd_list and request.POST['deviceid'] not in get_device:
                    return_disconnection_devices = {"code": "200", "msg": "断开设备成功", "data": get_device_list}
                    return HttpResponse(json.dumps(return_disconnection_devices))
                else:
                    return_disconnection_devices_error = {"code": "200", "msg": "断开设备失败,请检查设备名称是否正确", "data": get_device_list}
                    return HttpResponse(json.dumps(return_disconnection_devices_error))

            else:
                disconnection_devices_token_error = {"code": "-11", "msg": "token过期", "data": {}}
                return HttpResponse(json.dumps(disconnection_devices_token_error))
        except:
            disconnection_devices_request_error = {"code": "-13", "msg": "请求参数错误,请检查参数。", "data": {}}
            return HttpResponse(json.dumps(disconnection_devices_request_error))
    else:
        disconnection_devices_error = {"code": "-12", "msg": "请求方式错误", "data": {}}
        return HttpResponse(json.dumps(disconnection_devices_error))
