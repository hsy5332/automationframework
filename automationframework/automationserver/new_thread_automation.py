# coding : utf-8
import threading


class NewThreadAutomation(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        pass


# 创建线程
threads = []
threadcount = 0
while threadcount < 3:
    thread = NewThreadAutomation()
    threads.append(thread)
    threadcount = threadcount + 1;
for i in threads:
    i.start()
for y in threads:
    y.join()
