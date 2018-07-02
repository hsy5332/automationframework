# coding : utf-8
import threading
import time
import run_app_automation


class NewThreadAutomation(threading.Thread):
    def __init__(self, thread_count, device_id, appium_port):
        threading.Thread.__init__(self)
        self.device_id = device_id
        self.thread_count = thread_count
        self.appium_port = appium_port

    def run(self):
        if self.device_id == 'run_appium' and self.appium_port == 'run_appium':
            transmit_appium_port_list = appium_port_list  # 把appium_port_list 赋值给 transmit_appium_port_list
            transmit_appium_port_list.pop(0)  # 把原增加的用来判断是否启动appium 字符串删除
            run_app_automation.RunAppAutomation().launch_appium(device_count, transmit_appium_port_list,
                                                                appium_bootstrap_port_list)  # 启动appium
        else:
            print("正在运行自动化程序,请稍后")
            time.sleep(5)
            try:
                run_app_automation.RunAppAutomation().stop_appium(self.appium_port)
                print("正在关闭appium端口号：%s 的服务进程。" % self.appium_port)
            except:
                print("关闭Appium 服务失败,请手动关闭进程。Appium 服务端口号为: %s" % self.appium_port)


# 运行自动化程序
thread_count = 0;  # 启动线程计数器
thread_list = []  # 存放线程的列表
device_count, device_list, appium_port_list, appium_bootstrap_port_list = run_app_automation.RunAppAutomation().get_device()  # 获取设备数、设备名称、appium、appium bootstrap端口号
device_list.insert(0, 'run_appium')  # 在列表的始端增加一个字符串 用来判断是否启动appium
appium_port_list.insert(0, 'run_appium')

# 创建自动化多设备运行线程
if device_count > 0:
    while thread_count <= device_count:
        run_thread = NewThreadAutomation(thread_count, device_list[thread_count], appium_port_list[thread_count])
        thread_list.append(run_thread)
        thread_count += 1;
    for u, i in enumerate(thread_list):
        i.start()
        if u == 0:  # 判断是否在启动appium，若在启动appium 就等待一会,让appium启动起来在运行自动化程序
            print("正在启动appium服务,请稍等...")
            time.sleep(10)
    for y in thread_list:
        y.join()

    print("完成所有自动化程序")
else:
    print("未获取到任何设备,不执行自动化程序")
