# conding : utf-8import osimport timeimport datetimeimport jsonfrom . import data_read, run_web_automation, run_interface_automationfrom .tasks import run_automation_app_task, run_automation_interface_taskfrom .models import rabbit_task_recordfrom django.http import HttpResponse# 请求示例def index(request):    return HttpResponse("这是一个简单的示例")def token(token):    try:        if int(token) + 86400 > int(time.time()):  # 86400是一天的时间戳            return True        else:            return False    except:        return False# 获取本地adb的设备信息def get_devices(request):    if request.POST:        try:            if token(request.POST['token']):                take_devices_list = []  # 获取设备信息列表                take_devices_info = os.popen("adb devices")                for i in take_devices_info:                    if 'device' in i and 'attached' not in i:                        take_devices_list.append(i.split('\t')[0])                return_take_devices = {"code": "200", "msg": "success", "data": take_devices_list}                return HttpResponse(json.dumps(return_take_devices))            else:                get_devices_token_error = {"code": "-11", "msg": "token过期", "data": {}}                return HttpResponse(json.dumps(get_devices_token_error))        except:            get_devices_request_error = {"code": "-13", "msg": "请求参数错误,请检查参数。", "data": {}}            return HttpResponse(json.dumps(get_devices_request_error))    else:        get_devices_error = {"code": "-12", "msg": "请求方式错误", "data": {}}        return HttpResponse(json.dumps(get_devices_error))# 连接设备def connect_devices(request):    if request.POST:        try:            if token(request.POST['token']):                connect_status = 1  # 声明变量来判断设备连接的状态 # 声明变量来判断设备连接的状态 0 是未连接 1 是连接成功,默认是1                connect_devices_cmd = os.popen("adb connect %s" % request.POST['deviceid'])                for connect_cmd in connect_devices_cmd:                    if "unable" in connect_cmd:                        connect_status = 0                if connect_status == 0:                    return_miss_device_info = {"code": "200", "msg": "连接设备失败请检查设备是否和pc在一个局域网内", "data": {}}                    return HttpResponse(json.dumps(return_miss_device_info))                else:                    get_device_list = []  # 存放获取到的设备ID                    for get_device in os.popen("adb devices"):                        if 'device' in get_device and 'attached' not in get_device:                            get_device_list.append(get_device.split('\t')[0])                    return_connect_devices = {"code": "200", "msg": "连接设备成功", "data": get_device_list}                    return HttpResponse(json.dumps(return_connect_devices))            else:                connect_devices_token_error = {"code": "-11", "msg": "token过期", "data": {}}                return HttpResponse(json.dumps(connect_devices_token_error))        except:            connect_devices_request_error = {"code": "-13", "msg": "连接设备失败。", "data": {}}            return HttpResponse(json.dumps(connect_devices_request_error))    else:        connect_devices_error = {"code": "-12", "msg": "请求方式错误", "data": {}}        return HttpResponse(json.dumps(connect_devices_error))# 断开设备连接def disconnection_devices(request):    if request.POST:        try:            if token(request.POST['token']):                get_device_list = []  # 存获取到的设备数据                disconnection_devices_status = 0                get_device_status = 0  # 1代表有，0代表没有                for disconnection_cmd in os.popen("adb disconnect %s" % request.POST['deviceid']):                    if "disconnected" in disconnection_cmd:                        disconnection_devices_status = 1                for get_device in os.popen("adb devices"):                    if request.POST['deviceid'] in get_device:                        get_device_status = 1                    if 'device' in get_device and 'attached' not in get_device:                        get_device_list.append(get_device.split('\t')[0])                if disconnection_devices_status == 1 and get_device_status == 0:                    return_disconnection_devices = {"code": "200", "msg": "断开设备成功", "data": get_device_list}                    return HttpResponse(json.dumps(return_disconnection_devices))                else:                    return_disconnection_devices_error = {"code": "200", "msg": "断开设备失败,请检查设备名称是否正确",                                                          "data": get_device_list}                    return HttpResponse(json.dumps(return_disconnection_devices_error))            else:                disconnection_devices_token_error = {"code": "-11", "msg": "token过期", "data": {}}                return HttpResponse(json.dumps(disconnection_devices_token_error))        except:            disconnection_devices_request_error = {"code": "-13", "msg": "请求参数错误,请检查参数。", "data": {}}            return HttpResponse(json.dumps(disconnection_devices_request_error))    else:        disconnection_devices_error = {"code": "-12", "msg": "请求方式错误", "data": {}}        return HttpResponse(json.dumps(disconnection_devices_error))# 执行自动化程序def run_automation_file(request):    if request.POST:        try:            if token(request.POST['token']):                if data_read.DataRead().check_case_file(request.POST['filename']):                    # runcasetype = app interface web 对应执行自动化用例的名称                    if request.POST['runcasetype'] == 'web':                        run_web_automation.RunWebAutomation.run_web_case(request.POST['filename'], 'web')                        return_run_automation_file = {"code": "200", "msg": "Web自动化程序完成", "data": {}}                        return HttpResponse(json.dumps(return_run_automation_file))                    elif request.POST['runcasetype'] == 'app':                        # 在task中执行自动化程序,rabbit_task_record是方法，delay调用celery中的方法代表延迟执行                        run_task_result = run_automation_app_task.delay(request.POST['filename'],                                                                        request.POST['runcasetype'],                                                                        request.POST['devicesid'])                        # 把执行的任务保存在数据库中存为记录                        save_task_result = rabbit_task_record(task_id=run_task_result.id,                                                              file_name=request.POST['filename'],                                                              run_case_type=request.POST['runcasetype'],                                                              devices_id=request.POST['devicesid'],                                                              created_log_time=datetime.datetime.now())                        save_task_result.save()  # 保存数据                        return_run_automation_file = {"code": "200", "msg": "App自动化程序执行完成", "data": {}}                        return HttpResponse(json.dumps(return_run_automation_file))                    elif request.POST['runcasetype'] == 'interface':                        # 在task中执行自动化程序,rabbit_task_record是方法，delay调用celery中的方法代表延迟执行                        run_task_result = run_automation_interface_task.delay(request.POST['filename'],                                                                              request.POST['runcasetype'])                        # 把执行的任务保存在数据库中存为记录                        save_task_result = rabbit_task_record(task_id=run_task_result.id,                                                              file_name=request.POST['filename'],                                                              run_case_type=request.POST['runcasetype'],                                                              created_log_time=datetime.datetime.now())                        save_task_result.save()  # 保存数据                        return_run_automation_file = {"code": "200", "msg": "App自动化程序执行完成", "data": {}}                        return HttpResponse(json.dumps(return_run_automation_file))                    else:                        return_run_automation_error = {"code": "-15", "msg": "未找到该自动化启动类型", "data": {}}                        return HttpResponse(json.dumps(return_run_automation_error))                else:                    file_not_found = {"code": "-14", "msg": "测试用例文件不存在", "data": {}}                    return HttpResponse(json.dumps(file_not_found))            else:                run_automation_token_error = {"code": "-11", "msg": "token过期", "data": {}}                return HttpResponse(json.dumps(run_automation_token_error))        except:            run_automation_request_error = {"code": "-13", "msg": "请求参数错误,请检查参数。", "data": {}}            return HttpResponse(json.dumps(run_automation_request_error))    else:        run_automation_file_error = {"code": "-12", "msg": "请求方式错误", "data": {}}        return HttpResponse(json.dumps(run_automation_file_error))