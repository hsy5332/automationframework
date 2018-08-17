# conding:utf-8
import time
from automationframework import celery_app
from . import new_thread_automation, run_interface_automation

@celery_app.task
def run_automation_app_task(file_name, run_case_type):
    new_thread_automation.run_automation_procedure(file_name, run_case_type)  # app 自动化
    return file_name, run_case_type


@celery_app.task
def run_automation_interface_task(file_name, run_case_type):
    run_interface_automation.RunInterfaceAutomation(file_name, run_case_type).run_interface_case()  # 接口自动化
    return file_name, run_case_type

