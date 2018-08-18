# coding : utf-8

import os
import random
import threading
import subprocess
import time
import getpass
# from automationframework.automationserver import data_read  # 单独此文件需要开启 windows
from . import data_read  # 启动django服务需要开启
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction


class RunAppAutomation:
    # 获取本地设备信息
    def get_device(self, devices_id):
        devices_list = []  # 存放设备列表
        for device_id in os.popen("adb devices"):
            if 'device' in device_id and 'attached' not in device_id:
                devices_list.append(device_id.split('\t')[0])
        if devices_id == 'all' or devices_id == '' or devices_id == ' ':
            device_count = len(devices_list)  # 获取的设备数
        else:
            device_count = 1;
            devices_list = [devices_id]
        appium_port, appium_bootstrap_port = RunAppAutomation.create_appium_port(self, device_count)
        return device_count, devices_list, appium_port, appium_bootstrap_port

    # 检测当前pc系统 windows 还是非windows
    def check_system(self):
        if os.name == 'nt':
            return True  # 返回true 是Windows
        else:
            return False

    # 获取手机安卓系统版本
    def get_device_android_version(self, device_id):
        try:
            android_version = os.popen('adb -s %s shell getprop ro.build.version.release' % device_id).read().strip()
            return android_version
        except:
            return '4.4.2'

    # 检查端口号是否存在
    def check_appium_port(self, appium_port, appium_bootstrap_port):
        if os.name == 'nt':
            if os.popen("netstat -ano | findstr %s" % appium_port).read() == '' and os.popen(
                    "netstat -ano | findstr %s" % appium_bootstrap_port).read() == '':
                return True
            else:
                return False
        else:
            if os.popen("lsof -i tcp:%s" % appium_port).read() == '' and os.popen(
                    "lsof -i tcp:%s" % appium_bootstrap_port).read() == '':
                return True
            else:
                return False

    # 创建 appium 端口号
    def create_appium_port(self, device_count):
        count = 0;
        appium_port = []  # 存放生成appium的端口号
        appium_bootstrap_port = []  # 存放生成appium bootstrap的端口号
        while count < device_count:
            random_port_number = random.randrange(4000, 10000, 2)
            random_bootstrap_number = random.randrange(4001, 9999, 2)
            check_appium_port_status = RunAppAutomation().check_appium_port(random_port_number, random_bootstrap_number)
            if random_port_number not in appium_port and random_bootstrap_number not in appium_bootstrap_port and check_appium_port_status == True:
                appium_port.append(random_port_number)  # 获取1000 到 100000之间的偶数
                appium_bootstrap_port.append(random_bootstrap_number)  # 获取1001 到 9999之间的奇数
                count += 1;
        return appium_port, appium_bootstrap_port

    # 启动 appium 多线程类
    class LaunchAppiumThread(threading.Thread):
        def __init__(self, appium_port, appium_bootstrap_port):
            threading.Thread.__init__(self)
            self.appium_port = appium_port  # appium 端口号
            self.appium_bootstrap_port = appium_bootstrap_port  # appium bootstrap 端口号

        def run(self):
            # Django 服务开启
            appium_cmd = subprocess.Popen(
                'appium -p %s -bp %s >static/appiumlog/log_%s_%s_%s.log' % (
                    self.appium_port, self.appium_bootstrap_port, self.appium_port, self.appium_bootstrap_port,
                    int(time.time())),
                shell=True)

            # 调试开启
            # appium_cmd = subprocess.Popen('appium -p %s -bp %s' % (self.appium_port, self.appium_bootstrap_port),
            #                               shell=True)
            appium_pid = appium_cmd.pid
            if appium_pid > 0:
                mysql_cursor, connect_mysql = data_read.DataRead().save_database()
                execute_sql = "insert into `automationquery_automation_appium_pid` (`appium_port`,`appium_bootstrap_port`,`appium_pid`,`created_time`)VALUES('%s','%s','%s','%s')" % (
                    self.appium_port, self.appium_bootstrap_port, appium_pid, int(time.time()))
                mysql_cursor.execute(execute_sql)
                connect_mysql.commit()  # 提交数据
                connect_mysql.close()  # 关闭数据库连接
            appium_cmd.wait()

    # 启动appium
    def launch_appium(self, device_count, appium_port, appium_bootstrap_port):
        thread_count = 0;
        thread_list = []
        while thread_count < device_count:
            # 创建 appium 多线程 启动appium
            launch_appium_thread = RunAppAutomation.LaunchAppiumThread(appium_port[thread_count],
                                                                       appium_bootstrap_port[thread_count])
            thread_list.append(launch_appium_thread)
            thread_count += 1;
        for i in thread_list:
            i.start()
        for y in thread_list:
            y.join()

    # 关闭appium 服务
    def stop_appium(self, device_id, appium_port, contrast_time_stamp):
        # 获取数据库中所有的appium 服务对应的pid
        mysql_cursor, connect_mysql = data_read.DataRead().save_database()
        execute_sql = "UPDATE `automationquery_automation_appium_pid` SET `devices_id` = '%s' WHERE `appium_port` = '%s'" % (
            device_id, appium_port)
        mysql_cursor.execute(execute_sql)
        connect_mysql.commit()  # 提交数据
        execute_select_sql = "SELECT `appium_pid` FROM `automationquery_automation_appium_pid` WHERE `appium_port` = '%s' AND `created_time` > '%s'" % (
            appium_port, str(contrast_time_stamp - 60))
        mysql_cursor.execute(execute_select_sql)  # 查询数据
        execute_select_sql_results = mysql_cursor.fetchall()  # 返回所有的查询结果数据
        for pid_tuple in execute_select_sql_results:
            appium_pid = pid_tuple[0]
        connect_mysql.close()

        # 关闭appium服务
        if os.name == 'nt':
            appium_pid_list = []
            for get_appium_pid in os.popen("netstat -ano | findstr %s" % appium_port):
                if 'LISTENING' in get_appium_pid and str(appium_port) in get_appium_pid:
                    appium_pid_list.append(
                        get_appium_pid.replace(" ", "").strip().split('LISTENING')[1])  # Windows 获取pid
            for kill_pid in appium_pid_list:
                os.popen('taskkill -pid %s -t -f ' % kill_pid)  # 关闭appium服务
        else:
            appium_pid_list = []
            for get_appium_pid in os.popen("lsof -i tcp:%s" % appium_port):
                if 'LISTEN' in get_appium_pid and str(appium_port) in get_appium_pid:
                    appium_pid_list.append(
                        get_appium_pid.replace(' ', '').strip().split('node')[1].split(getpass.getuser())[
                            0])  # linux Unix 获取pid getpass.getuser() 获取当前系统登录的用户名
            for kill_pid in appium_pid_list:
                os.popen('kill %s' % kill_pid)  # 关闭appium服务
            os.popen('kill %s' % appium_pid)  # 关闭Appium 主进程Pid

    # 读取用例操作类型
    def read_case_operate_type(self, file_name, run_sheel_name, appium_driver):
        pass_case_count = 0;  # 执行用例的通过数
        not_run_case = 0;  # 不执行的用例数
        run_case_nows, run_case_column, run_sheel = data_read.DataRead().read_case_file(file_name, run_sheel_name)
        print("正在读取测试用例,请稍后...")
        event_id = time.strftime('%Y%m%d%H%M%S', time.localtime())  # 每台设备运行的eventid
        run_case_now_count = 1;  # 遍历用例表格计数器 从1 开始 第一行不算
        case_report_list = []  # 存放测试结果列表,然后去保存到数据库
        end_case_number = []  # Excel end操作类型标记列表
        if_case_number = []  # Excel if 操作类型标记列表
        if_number = 0;  # 用例中 if计数器

        for if_end_count in range(1, run_case_nows):  # if_end_count if和end 计数器
            operate_types = run_sheel.row_values(if_end_count)[1]  # 获取Excel所有操作类型
            if 'if' in operate_types:
                if_case_number.append(if_end_count)  # 获取操作类型为if 在Excel中的序号
            if 'end' in operate_types:
                end_case_number.append(if_end_count)  # 获取操作类型为end 在Excel中的序号

        while run_case_now_count < run_case_nows:
            case_id = int(run_sheel.row_values(run_case_now_count)[0])  # 用例编号
            operate_type = run_sheel.row_values(run_case_now_count)[1]  # 操作类型
            element_attribute = run_sheel.row_values(run_case_now_count)[2]  # 元素属性
            parameter = run_sheel.row_values(run_case_now_count)[3]  # 参数
            case_describe = run_sheel.row_values(run_case_now_count)[5]  # 步骤描述
            case_execute = run_sheel.row_values(run_case_now_count)[6]  # 用例执行状态
            stat_case_time = time.time()  # 开始执行用例时间
            if 'Y' in case_execute or 'y' in case_execute:
                if operate_type == '等待时间':
                    try:
                        time.sleep(int(element_attribute))  # 先读取用例中的time，进行转化若无法转化则取默认值3

                    except:
                        time.sleep(3)
                    case_report = '用例编号:%s,执行通过。' % case_id
                    print(case_report)
                elif '点击_' in operate_type:
                    case_report = RunAppAutomation().operate_click(operate_type, element_attribute, appium_driver,
                                                                   case_id)
                    print(case_report)
                elif '滑动' in operate_type:
                    case_report = RunAppAutomation().operate_slide(operate_type, appium_driver, case_id)
                    print(case_report)
                elif '长按_' in operate_type:
                    case_report = RunAppAutomation().operate_long_click(operate_type, element_attribute, appium_driver,
                                                                        case_id)
                    print(case_report)
                elif '输入_' in operate_type:
                    case_report = RunAppAutomation().operate_input(operate_type, element_attribute, appium_driver,
                                                                   case_id, parameter)
                    print(case_report)
                elif '物理按钮' in operate_type:
                    case_report = RunAppAutomation().operate_physics_key(appium_driver, case_id, int(parameter))
                    print(case_report)
                elif '查找_' in operate_type:
                    case_report = RunAppAutomation().operate_check_element(operate_type, element_attribute,
                                                                           appium_driver, case_id)
                    print(case_report)
                elif 'if' in operate_type:
                    case_report = RunAppAutomation().operate_check_element(operate_type, element_attribute,
                                                                           appium_driver, case_id)
                    if "执行通过" not in case_report:
                        print(case_report)
                        # try:
                        #     x = end_case_number[if_number]
                        # except IndexError:
                        #     if len(end_case_number) - 1 >= 0:
                        #         x = end_case_number[len(end_case_number) - 1]
                        #         print("当前用例中的if和and不等，请检查用例")
                        #     else:
                        #         print("当前用例中的if和and不等，请检查用例")
                        #         pass
                        if len(end_case_number) == len(if_case_number):
                            run_case_now_count = end_case_number[if_number]
                        else:
                            print("当前用例中的if和and不等，请检查用例")
                            run_case_now_count = end_case_number[-1]
                    if_number += 1;
            else:
                not_run_case += 1;
                case_report = '用例编号:%s,执行状态为No,故不执行。' % (case_id)
                print(case_report)
            if '执行通过' in case_report:
                pass_case_count += 1;  # 当用例执行通过，则加1
            end_case_time = time.time()  # 结束用例时间
            case_report_dictionary = {
                'devicesexecute': 'Yes',
                'operatetype': operate_type,
                'element': element_attribute,
                'parameter': parameter,
                'rundescribe': case_describe,
                'caseexecute': case_execute,
                'runcasetime': round(end_case_time - stat_case_time, 2),
                'caseid': case_id,
                'eventid': event_id,
                'casereport': case_report,
                'createdtime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'updatetime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            }
            case_report_list.append(case_report_dictionary)  # 把数据存到列表中
            run_case_now_count += 1;  # 循环计数器 +1
        return run_case_nows - 1, pass_case_count, not_run_case, case_report_list  # 返回用例总数、执行通过用例的数量、执行用例结果

    # 执行app自动化用例
    def run_app_automation_case(self, file_name, configure_sheel_name, run_sheel_name, device_id, appium_port):
        # filename 用例名称 configure_sheel_name 配置表格 run_sheel_name 执行用例表格 device_id 设备id
        configure_case_rows, configure_case_column, configure_sheel = data_read.DataRead().read_case_file(file_name,
                                                                                                          configure_sheel_name)
        for i in range(1, configure_case_rows):
            app_package = configure_sheel.row_values(i)[0]  # 获取app 包名
            app_activity = configure_sheel.row_values(i)[1]  # 获取启动的activity
            app_path = configure_sheel.row_values(i)[2]  # 获取apk的路径

        platform_version = RunAppAutomation().get_device_android_version(device_id)  # 获取当前设备的Android系统版本
        connect_appium_device_config = RunAppAutomation().original_device_info(device_id, 'Android',
                                                                               platform_version,
                                                                               app_package, app_activity,
                                                                               app_path)  # 初始化appium 连接设备信息

        try:
            driver = webdriver.Remote('http://localhost:%s/wd/hub' % appium_port,
                                      connect_appium_device_config)  # 连接appium
            driver.implicitly_wait(20)  # 在未获取到元素时 等待 10 秒
            case_amount, pass_case_count, not_run_case, case_report_list = RunAppAutomation().read_case_operate_type(
                file_name,
                run_sheel_name,
                driver)  # 读取用例操作类型 并执行
            # 获取总用例数、执行用过的用例数、用例执行结果的列表
            try:
                mysql_cursor, connect_mysql = data_read.DataRead().save_database()  # 获取数据库游标 游标执行sql,以及连接的变量用于关闭数据连接
                if len(case_report_list) > 0:
                    add_device_info_count = 0;  # case report 加入设备信息计数器
                    while add_device_info_count < len(case_report_list):
                        case_report_list[add_device_info_count].update(
                            {'devicesinfos': "设备名：" + str(device_id) + "," + "系统版本信息：" + 'Android' + str(
                                platform_version)}),
                        case_report_list[add_device_info_count].update({'appiumport': appium_port}),
                        case_report_list[add_device_info_count].update({'devicesexecute': 'Yes'})
                        add_device_info_count += 1;
                    execute_sql_count = 0;  # 执行sql数据计数器
                    while execute_sql_count < len(case_report_list):
                        execute_sql = "insert into `automationquery_automation_function_app`  (`devicesinfos`,`appiumport`,`devicesexecute`,`operatetype`," \
                                      "`element`,`parameter`,`rundescribe`,`caseexecute`,`runcasetime`,`caseid`,`eventid`,`casereport`,`createdtime`," \
                                      "`updatetime`)VALUES('%s','%s','%s','%s',\"%s\",'%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                                          case_report_list[execute_sql_count].get('devicesinfos'),
                                          case_report_list[execute_sql_count].get('appiumport'),
                                          case_report_list[execute_sql_count].get('devicesexecute'),
                                          case_report_list[execute_sql_count].get('operatetype'),
                                          case_report_list[execute_sql_count].get('element'),
                                          case_report_list[execute_sql_count].get('parameter'),
                                          case_report_list[execute_sql_count].get('rundescribe'),
                                          case_report_list[execute_sql_count].get('caseexecute'),
                                          case_report_list[execute_sql_count].get('runcasetime'),
                                          case_report_list[execute_sql_count].get('caseid'),
                                          case_report_list[execute_sql_count].get('eventid'),
                                          case_report_list[execute_sql_count].get('casereport'),
                                          str(case_report_list[execute_sql_count].get('createdtime')),
                                          str(case_report_list[execute_sql_count].get('updatetime')),
                                      )
                        mysql_cursor.execute(execute_sql)
                        execute_sql_count += 1;
                    connect_mysql.commit()  # 提交数据
                    connect_mysql.close()  # 关闭数据库连接
                else:
                    pass
            except:
                print("保存数据失败。")
            return case_amount, pass_case_count, not_run_case  # 返回总用例数、执行用过的用例数 用于发送邮件的统计
        except:
            print('连接Appium失败,连接设备号为: %s 端口号为: %s ' % (device_id, appium_port))
        driver.quit()  # 退出appium

    # 设备连接Appium 配置文件
    def original_device_info(self, udid, platform_name, platform_version, app_package, app_activity, app_path):
        device_info = {
            'deviceName': udid,
            'platformName': platform_name,
            'platformVersion': platform_version,
            'appPackage': app_package,
            'appActivity': app_activity,
            'udid': udid,
            'unicodeKeyboard': "True",
            'resetKeyboard': "True",
        }
        if app_path != '':
            device_info['app'] = app_path
        else:
            pass
        return device_info

    # 点击事件
    def operate_click(self, operate_type, element, driver, case_id):
        if operate_type == "点击_id":
            try:
                driver.find_element_by_id(element).click()  # 点击ID事件
                casere_port = "用例编号:%s,执行通过。" % (case_id)
                return casere_port
            except:
                casere_port = "用例编号:%s,执行不通过。" % (case_id)
                return casere_port
        elif operate_type == "点击_xpath":
            try:
                driver.find_element_by_xpath(element).click()  # 点击xpath
                casere_port = "用例编号:%s,执行通过。" % (case_id)
                return casere_port
            except:
                casere_port = "用例编号:%s,执行不通过。" % (case_id)
                return casere_port
        elif operate_type == "点击_textname":  # 点击textname
            try:
                driver.find_elements_by_name(element)[0].click()
                casere_port = "用例编号:%s,执行通过。" % (case_id)
                return casere_port
            except:
                casere_port = "用例编号:%s,执行不通过。" % (case_id)
                return casere_port

        elif operate_type == "点击_classid":
            try:
                driver.find_elements_by_class_name(element)[0].click()  # 点击xpath
                casere_port = "用例编号:%s,执行通过。" % (case_id)
                return casere_port
            except:
                casere_port = "用例编号:%s,执行不通过。" % (case_id)
                return casere_port
        else:
            print("用例编号:%s,执行不通过，该用例的元素属性或参数可能有问题，请检查该用例。" % (case_id))

    # 滑动操作
    def operate_slide(self, operate_type, driver, case_id):
        x = driver.get_window_size()['width']
        y = driver.get_window_size()['height']
        if operate_type == "向上滑动":
            try:
                driver.swipe(x * 0.5, y * 0.9, x * 0.5, y * 0.3)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "向左滑动":
            try:
                driver.swipe(x * 0.9, y * 0.5, x * 0.08, y * 0.5)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "向下滑动":
            try:
                driver.swipe(x * 0.5, y * 0.3, x * 0.5, y * 0.9)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "向右滑动":
            try:
                driver.swipe(x * 0.08, y * 0.5, x * 0.9, y * 0.5)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        else:
            case_report = "用例编号:%s,执行不通过，该用例的元素属性或参数可能有问题，请检查该用例。" % (case_id)
            return case_report

    # 输入操作
    def operate_input(self, operate_type, element, driver, case_id, *parameter):
        if operate_type == "输入_id":
            try:
                driver.find_element_by_id(element).send_keys(parameter[0])
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "输入_xpath":
            try:
                driver.find_element_by_xpath(element).send_keys(parameter[0])
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "输入_classid":
            try:
                driver.find_elements_by_class_name(element)[0].send_keys(parameter[0])
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "输入_textname":
            try:
                driver.find_elements_by_name(element)[0].send_keys(parameter[0])
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        else:
            case_report = "用例编号:%s,执行不通过，该用例的元素属性或参数可能有问题，请检查该用例。" % (case_id)
            return case_report

    # Android物理按键操作
    def operate_physics_key(self, driver, case_id, *parameter):
        key_code = str(parameter[0])
        try:
            driver.keyevent(key_code)
            case_report = "用例编号:%s,执行通过。" % (case_id)
            return case_report
        except:
            case_report = "用例编号:%s,执行不通过。" % (case_id)
            return case_report

    # 检查元素是否存在
    def operate_check_element(self, operate_type, element, driver, case_id):
        if operate_type == "查找_id":
            try:
                driver.find_element_by_id(element)
                case_report = "用例编号:%s,执行通过。页面包含此元素" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。页面不包含此元素。" % (case_id)
                return case_report
        elif operate_type == "查找_xpath":
            try:
                driver.find_element_by_xpath(element)
                case_report = "用例编号:%s,执行通过。页面包含此元素" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。页面不包含此元素。" % (case_id)
                return case_report
        elif operate_type == "查找_classid":
            try:
                driver.find_elements_by_class_name(element)
                case_report = "用例编号:%s,执行通过。页面包含此元素" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。页面不包含此元素。" % (case_id)
                return case_report
        elif operate_type == "查找_textname":
            try:
                driver.find_elements_by_name(element)[0]  # 注意 此方法在appium高版本上 可能无法运行
                case_report = "用例编号:%s,执行通过。页面包含此元素" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。页面不包含此元素。" % (case_id)
                return case_report
        elif operate_type == '查找_文本':
            all_xpath_element = driver.find_elements_by_xpath('//*')
            for xpath_element in all_xpath_element:
                if xpath_element.text == element:
                    case_report = "用例编号:%s,执行通过。页面包含此元素。" % (case_id)
                    return case_report
            case_report = "用例编号:%s,执行不通过。页面不包含此元素。" % (case_id)
            return case_report
        elif operate_type == "if包含_id":
            try:
                driver.find_element_by_id(element)
                case_report = "用例编号:%s,执行通过。页面包含此元素。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。页面不包含此元素。" % (case_id)
                return case_report
        elif operate_type == "if包含_xpath":
            try:
                driver.find_element_by_xpath(element)
                case_report = "用例编号:%s,执行通过。页面包含此元素。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。页面不包含此元素。" % (case_id)
                return case_report
        elif operate_type == "if包含_classid":
            try:
                driver.find_elements_by_class_name(element)
                case_report = "用例编号:%s,执行通过。页面包含此元素。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。页面不包含此元素。" % (case_id)
                return case_report
        elif operate_type == "if包含_textname":
            try:
                driver.find_elements_by_name(element)[0]
                case_report = "用例编号:%s,执行通过。页面包含此元素。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。页面不包含此元素。" % (case_id)
                return case_report
        elif operate_type == 'if包含_文本':
            all_xpath_element = driver.find_elements_by_xpath('//*')
            for xpath_element in all_xpath_element:
                if xpath_element.text == element:
                    case_report = "用例编号:%s,执行通过。页面包含此元素。" % (case_id)
                    return case_report
            case_report = "用例编号:%s,执行不通过。页面不包含此元素。" % (case_id)
            return case_report
        else:
            case_report = "用例编号:%s,执行不通过，该用例的元素属性可能有问题，请检查该用例。" % (case_id)
            return case_report

    # 长按操作
    def operate_long_click(self, operate_type, element, driver, case_id, *parameter):
        if operate_type == "长按_id":  # 长按元素id
            try:
                el = driver.find_element_by_id(element)
                TouchAction(driver).long_press(el, 1).release().perform()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "长按_classid":  # 长按元素classname
            try:
                el = driver.find_elements_by_class_name(element)[0]
                TouchAction(driver).long_press(el, 1).release().perform()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "长按_xpath":  # 长按元素xpath
            try:
                el = driver.find_element_by_xpath(element)
                TouchAction(driver).long_press(el, 1).release().perform()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "长按_textname":  # 长按textname
            try:
                el = driver.find_elements_by_name(element)[0]
                TouchAction(driver).long_press(el, 1).release().perform()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        else:
            case_report = "用例编号:%s,执行不通过，该用例的元素属性或参数可能有问题，请检查该用例。" % (case_id)
            return case_report


if __name__ == "__main__":
    RunAppAutomation().get_device()
    # device_count = 2
    # appium_port = [4586, 7892]
    # appium_bootstrap_port = [5645, 7541]
    # RunAppAutomation().launch_appium(device_count, appium_port, appium_bootstrap_port)
