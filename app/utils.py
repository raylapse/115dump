from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from job import Job
import logging
import os
import time
from flask_socketio import emit

class JobScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def add(self, task, cron_expression):
        """
        创建并启动计划任务
        :param task: Task 实例
        :param cron_expression: cron 表达式
        """
        self.scheduler.add_job(self.run, CronTrigger.from_crontab(cron_expression), args=[task])
        logging.info(f"Scheduled job for task: {task.get_name()} with cron expression: {cron_expression}")

    def run(self, task):
        """执行任务"""
        logging.info(f"Running task: {task.get_name()}")
        job = Job(task.get_name(), task)  # 创建一个 Job 实例并执行
        job.start()

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()

class LogCleaner:
    def __init__(self, retention_days):
        self.retention_days = retention_days
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.clean_logs, 'interval', days=1)
        self.scheduler.start()

    def clean(self):
        """清理过期日志文件"""
        log_dir = 'logs/'
        now = time.time()
        for log_file in os.listdir(log_dir):
            file_path = os.path.join(log_dir, log_file)
            if os.path.isfile(file_path):
                # 获取文件的最后修改时间
                file_age_days = (now - os.path.getmtime(file_path)) / (60 * 60 * 24)
                if file_age_days > self.retention_days:
                    os.remove(file_path)
                    print(f"Deleted old log file: {file_path}")

class SocketIOHandler(logging.Handler):
    def __init__(self, socketio, task_name):
        super().__init__()
        self.socketio = socketio
        self.task_name = task_name  # 用于标识任务
        self.channel = task_name  # 为每个任务创建不同的频道（或标识）

    def emit(self, record):
        """将日志记录发送到 WebSocket"""
        log_message = self.format(record)  # 格式化日志信息
        # 使用 emit 将日志信息推送到客户端
        emit('log_update', {'task_name': self.task_name, 'message': log_message}, room=self.channel)
