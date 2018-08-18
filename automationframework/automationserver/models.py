# coding:utf-8
from django.db import models


# 任务记录表
class rabbit_task_record(models.Model):
    task_id = models.CharField(max_length=150)
    file_name = models.CharField(max_length=50)
    run_case_type = models.CharField(max_length=20)
    devices_id = models.CharField(max_length=50)
    created_log_time = models.DateTimeField()
