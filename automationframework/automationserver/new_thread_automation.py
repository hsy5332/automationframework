# coding : utf-8
import threading
import time
# from automationframework.automationserver import run_app_automation, data_read  # 单独此文件需要开启 windows
from automationserver import run_app_automation, data_read, send_report  # 启动django服务需要开启


class NewThreadAutomation(threading.Thread):
    def __init__(self, thread_count, device_count, device_id, appium_port, appium_port_list,
                 appium_bootstrap_port_list, file_name, run_case_type):
        threading.Thread.__init__(self)
        self.device_id = device_id  # 设备id
        self.thread_count = thread_count  # 线程计算器
        self.appium_port = appium_port  # 每次运行线程的appium 端口号
        self.appium_port_list = appium_port_list  # 全部 appium 端口号
        self.appium_bootstrap_port_list = appium_bootstrap_port_list  # 全部 appium_bootstrap 端口号
        self.device_count = device_count  # 获取的设备数
        self.file_name = file_name  # 测试用例文件名
        self.run_case_type = run_case_type  # run_case_type = app

    def run(self):

        if self.device_id == 'run_appium' and self.appium_port == 'run_appium':
            transmit_appium_port_list = self.appium_port_list  # 把appium_port_list 赋值给 transmit_appium_port_list
            transmit_appium_port_list.pop(0)  # 把原增加的用来判断是否启动appium 字符串删除
            run_app_automation.RunAppAutomation().launch_appium(self.device_count, transmit_appium_port_list,
                                                                self.appium_bootstrap_port_list)  # 启动appium
        else:
            print("正在运行自动化程序,请稍后")
            time.sleep(self.thread_count + 2)
            excel_sheel_form = data_read.DataRead().gain_shell_name(self.run_case_type)
            # 执行App自动化
            start_run_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 执行用例时间
            case_amount, pass_case_count, not_run_case = run_app_automation.RunAppAutomation().run_app_automation_case(
                self.file_name, excel_sheel_form[0],
                excel_sheel_form[1],
                self.device_id, self.appium_port)
            try:
                run_app_automation.RunAppAutomation().stop_appium(self.appium_port)
                print("正在关闭appium端口号：%s 的服务进程。" % self.appium_port)
            except:
                print("关闭Appium 服务失败,请手动关闭进程。Appium 服务端口号为: %s" % self.appium_port)
            if send_report.SendReport().sender_email(start_run_time, case_amount, pass_case_count, not_run_case):  # 发送邮件
                print('邮件发送成功')
            else:
                print('发送邮件失败')


# 运行自动化程序
def run_automation_procedure(file_name, run_case_type):
    thread_count = 0;  # 启动线程计数器
    thread_list = []  # 存放线程的列表
    device_count, device_list, appium_port_list, appium_bootstrap_port_list = run_app_automation.RunAppAutomation().get_device()  # 获取设备数、设备名称、appium、appium
    # bootstrap端口号
    device_list.insert(0, 'run_appium')  # 在列表的始端增加一个字符串 用来判断是否启动appium
    appium_port_list.insert(0, 'run_appium')
    # 创建自动化多设备运行线程
    if device_count > 0:
        while thread_count <= device_count:
            run_thread = NewThreadAutomation(thread_count, device_count, device_list[thread_count],
                                             appium_port_list[thread_count], appium_port_list,
                                             appium_bootstrap_port_list, file_name, run_case_type)
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
        return True
    else:
        print("未获取到任何设备,不执行自动化程序")
        return False


if __name__ == "__main__":
    run_automation_procedure('app_function_case.xlsx', 'app')  # 运行App 自动化用例 参数名
