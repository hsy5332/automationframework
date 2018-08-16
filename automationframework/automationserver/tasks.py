# conding:utf-8
import time
from automationframework import celery_app
from . import data_read, new_thread_automation, run_web_automation, run_interface_automation


@celery_app.task
def run_automation_task(file_name, run_case_type):
    # new_thread_automation.run_automation_procedure(file_name, run_case_type)
    print(file_name, run_case_type)
    time.sleep(30)
    return file_name, run_case_type

@celery_app.task
def add(x, y):
    print(x, y)
    time.sleep(30)
    return x + y

