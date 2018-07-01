# coding : utf-8
import threading
import run_app_automation


class NewThreadAutomation(threading.Thread):
    def __init__(self, device_id):
        threading.Thread.__init__(self)
        self.device_id = device_id

    def run(self):
        print(self.device_id)


# 创建线程
count = 0;
threads = []
thread_count, device_list, appium_port, appium_bootstrap_port, pid_list = run_app_automation.RunAppAutomation().launch_appium()  # 获取设备数、设备名称、appium、appium bootstrap端口号
while count < thread_count:
    thread = NewThreadAutomation(device_list[count])
    threads.append(thread)
    count += 1;
for i in threads:
    i.start()
for y in threads:
    y.join()
