# coding : utf-8
import subprocess
import os
import time
import threading


class LaunchServer(threading.Thread):
    def __init__(self, run_type):
        threading.Thread.__init__(self)
        self.run_type = run_type  # 启动类型 Django/celery

    def run(self):
        curent_work_path = os.getcwd()  # 获取当前工作路径
        if self.run_type == 'Django':
            # 打印token值
            try:
                run_django_service_log_file = open(
                    '%s/static/runservicelog/run_django_service_log_file.log' % curent_work_path,
                    'a')  # 运行Django log文件
                print(
                    '正在创建Django服务log存放路径,路径为:%s/static/runservicelog/run_django_service_log_file.log' % curent_work_path)
            except FileNotFoundError:
                try:
                    print('python 默认的路径未找到,请输入一个正确的log存放路径')
                    log_file_path = str(input('请输入运行Djngo服务log记录文件路径:'))
                    run_django_service_log_file = open(log_file_path + '/run_django_service_log_file.log', 'a')
                except:
                    print('请输入正确的文件路径')

            try:
                print('正在启动Django服务,端口号为:8988,请访问 127.0.0.1:8988 检查Django服务是否启动成功。')
                subprocess.Popen('python3 manage.py runserver 0.0.0.0:8988', stdout=run_django_service_log_file,
                                 stderr=run_django_service_log_file, shell=True).wait()
            except Exception as e:
                print(e)
                print('执行命令错误,请检查错误异常')

        elif self.run_type == 'celery':
            run_celery_service_log_file = open(
                '%s/static/runservicelog/run_celery_service_log_file.log' % curent_work_path,
                'a')
            print(
                '正在创建Celery服务log存放路径,路径为:%s/static/runservicelog/run_celery_service_log_file.log' % curent_work_path)
            subprocess.Popen('celery worker -A automationframework -l info', stdout=run_celery_service_log_file,
                             stderr=run_celery_service_log_file, shell=True).wait()

        elif self.run_type == 'flower':
            try:
                print('celery flower 启动成功,请访问 http://localhost:5555/ 进行查看。')
                subprocess.Popen('python3.6 manage.py celery flower', shell=True).wait()
            except:
                print('celery flower 启动失败')


        else:
            print('无该启动类型的服务，请检查服务类型参数传递是否正确')


if __name__ == '__main__':
    print('启动脚本时间为 : %s' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    print('当前请求接口的token为 : %s' % (int(time.time()) + 86400))
    run_type_list, run_thread_list = ['Django', 'celery', 'flower'], [];
    run_count = 0;
    while run_count < len(run_type_list):
        run_thread = LaunchServer(run_type_list[run_count])
        run_thread_list.append(run_thread)
        run_count += 1;

    for i in run_thread_list:
        i.start()

    for y in run_thread_list:
        y.join()
