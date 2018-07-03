# coding : utf-8

import os
import random
import threading
import subprocess
import time
import getpass
from automationframework.automationserver import data_read  # 单独此文件需要开启 windows
# from automationserver import data_read  # 启动django服务需要开启


class RunAppAutomation:
    # 获取本地设备信息
    def get_device(self):
        devices_list = []  # 存放设备列表
        for device_id in os.popen("adb devices"):
            if 'device' in device_id and 'attached' not in device_id:
                devices_list.append(device_id.split('\t')[0])
        device_count = len(devices_list)  # 获取的设备数
        appium_port, appium_bootstrap_port = RunAppAutomation.create_appium_port(self, device_count)
        return device_count, devices_list, appium_port, appium_bootstrap_port

    def check_system(self):
        if os.name == 'nt':
            return True  # 返回true 是Windows
        else:
            return False

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
            appium_cmd = subprocess.Popen(
                'appium -p %s -bp %s >static/appiumlog/log_%s_%s_%s' % (
                    self.appium_port, self.appium_bootstrap_port, self.appium_port, self.appium_bootstrap_port,
                    int(time.time())),
                shell=True)
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
    def stop_appium(self, appium_port):
        # 获取所有的appium 服务对应的pid
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
            print(appium_pid_list)
            for kill_pid in appium_pid_list:
                os.popen('kill %s' % kill_pid)  # 关闭appium服务

    # 执行app自动化用例
    def run_app_automation_case(self, file_name, configure_sheel_name,
                                run_sheel_name):  # filename 用例名称 configure_sheel_name 配置表格 run_sheel_name 执行用例表格
        print(file_name, configure_sheel_name, run_sheel_name)
        # 在这里调用data_read read_case_file方法去遍历表格
        configure_case_nows, configure_case_column, configure_sheel = data_read.DataRead().read_case_file(file_name,
                                                                                                          configure_sheel_name)
        print('读取配置表')
        print(configure_case_nows, configure_case_column, configure_sheel)
        run_case_nows, run_case_column, run_sheel = data_read.DataRead().read_case_file(file_name, run_sheel_name)
        print('读取运行表')
        print(run_case_nows, run_case_column, run_sheel)
        print("调取app自动化用例成功")


if __name__ == "__main__":
    RunAppAutomation().get_device()
    # device_count = 2
    # appium_port = [4586, 7892]
    # appium_bootstrap_port = [5645, 7541]
    # RunAppAutomation().launch_appium(device_count, appium_port, appium_bootstrap_port)
