# coding : utf-8
import subprocess
import os

curent_work_path = os.getcwd()  # 获取当前工作路径
try:
    run_service_log_file = open('%s/static/runservicelog/run_service_log_file.log' % curent_work_path, 'a')  # 运行Django log文件
    print('正在创建Django服务log存放路径,路径为:%s/static/runservicelog/run_service_log_file.log' % curent_work_path)
except FileNotFoundError:
    try:
        print('python 默认的路径未找到,请输入一个正确的log存放路径')
        log_file_path = str(input('请输入运行Djngo服务log记录文件路径:'))
        run_service_log_file = open(log_file_path + '/run_service_log_file.log', 'a')
    except:
        print('请输入正确的文件路径')

try:
    print('正在启动Django服务,端口号为:8988,请访问 127.0.0.1:8988 检查Django服务是否启动成功。')
    subprocess.Popen('python manage.py runserver 0.0.0.0:8988', stdout=run_service_log_file, stderr=run_service_log_file, shell=True).wait()
except Exception as e:
    print(e)
    print('执行命令错误,请检查错误异常')
