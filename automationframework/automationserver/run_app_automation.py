# coding : utf-8

import os
import random


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

    # 创建 appium 端口号
    def create_appium_port(self, device_count):
        count = 0;
        appium_port = []  # 存放生成appium的端口号
        appium_bootstrap_port = []  # 存放生成appium bootstrap的端口号
        while count < device_count:
            random_port_number = random.randrange(4000, 10000, 2)
            random_bootstrap_number = random.randrange(4001, 9999, 2)
            if random_port_number not in appium_port and random_bootstrap_number not in appium_bootstrap_port:
                appium_port.append(random_port_number)  # 获取1000 到 100000之间的偶数
                appium_bootstrap_port.append(random_bootstrap_number)  # 获取1001 到 9999之间的奇数
                count += 1;
        return appium_port, appium_bootstrap_port

    # 启动 appium
    def launch_appium(self):
        device_count, devices_list, appium_port, appium_bootstrap_port = RunAppAutomation().get_device()
        appium_port_count = 0;
        pid_count = 0;
        pid_list = []
        while appium_port_count < device_count:
            os.popen("appium -p %s -bp %s" % (appium_port[appium_port_count], appium_bootstrap_port[appium_port_count]))
            appium_port_count += 1;

        while pid_count < device_count:
            for pid in os.popen("netstat -ano | findstr %s" % appium_port[pid_count]):
                pid_list.append(pid.replace("\t", '').replace(" ", '').strip().split('LISTENING')[1])
            pid_count += 1;
        return device_count, devices_list, appium_port, appium_bootstrap_port, pid_list


if __name__ == "__main__":
    RunAppAutomation().launch_appium()
