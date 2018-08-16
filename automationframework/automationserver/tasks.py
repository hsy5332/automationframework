# conding:utf-8
import time
from automationframework import celery_app
from . import new_thread_automation, run_interface_automation


@celery_app.task
def run_automation_task(file_name, run_case_type):
    if run_case_type == 'app':
        new_thread_automation.run_automation_procedure(file_name, run_case_type)  # app 自动化
    elif run_case_type == 'interface':
        run_interface_automation.RunInterfaceAutomation(file_name, run_case_type).run_interface_case()  # 接口自动化
    else:
        pass
    time.sleep(30)
    return file_name, run_case_type
