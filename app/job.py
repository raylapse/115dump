import conn
import tree
import dump
import task
import json
from datetime import datetime
import threading
import logging
from app.util import SocketIOHandler
import os

class Job:
    def __init__(self, task):
        """
        初始化 Job 实例
        
        :param task: 任务实例（Task 类实例），包含任务配置和规则
        """
        self.task = task  # 传入的 Task 类实例，包含任务的配置和规则
        self.timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # 生成时间戳
        self.name = f"{self.task.get_name()}_{self.timestamp}"  # 使用 task name 和时间戳来生成 Job 名称
        self.status = 'pending'  # 任务的初始状态
        self.logs = []  # 日志记录
        self.conn = conn.Conn()  # 初始化连接实例
        self.tree = tree.Tree()  # 初始化目录树实例
        self.dump = dump.Dump()  # 初始化 dump 实例
        self.start_time = None  # 任务开始时间
        self.end_time = None  # 任务结束时间
        self.lock = threading.Lock()  # 创建一个锁对象，用于线程同步
        self.logger = self._setup_logger()  # 初始化 logger
        self.job_data = self._load_job_data()  # 载入已有的 job 数据

    def _setup_logger(self):
        """为每个 Job 设置独立的日志文件，并同时发送到 WebSocket"""
        logger = logging.getLogger(self.name)
        log_filename = f"logs/{self.name}.log"  # 使用 job name 作为日志文件名
        
        # 日志文件处理器
        file_handler = logging.FileHandler(log_filename)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # SocketIO 处理器
        socketio_handler = SocketIOHandler(self.socketio, self.name)
        socketio_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)  # 将日志记录到文件
        logger.addHandler(socketio_handler)  # 将日志实时推送到 WebSocket
        logger.setLevel(logging.INFO)
        return logger
    
    def _load_job_data(self):
        """加载 job.json 文件，获取已有的任务数据"""
        job_file_path = 'cache/job.json'
        if os.path.exists(job_file_path):
            with open(job_file_path, 'r') as f:
                return json.load(f)
        else:
            return {"jobs": []}

    def _save_job_data(self):
        """保存 job 数据到 job.json 文件"""
        job_file_path = 'cache/job.json'
        with open(job_file_path, 'w') as f:
            json.dump(self.job_data, f, indent=4)

    def start(self):
        """
        启动任务
        1. 获取客户端
        2. 获取源目录树和目标目录树
        3. 执行增量同步或全量同步
        """
        self.start_time = datetime.now()  # 记录任务开始时间
        self.status = 'running'  # 设置任务状态为运行中
        self.logs.append(f"Job {self.name} started at {self.start_time}.")
        
        # 记录任务开始信息到 job.json
        job_info = {
            "name": self.name,
            "status": "running",
            "start_time": self.start_time.isoformat(),
            "result": {"success": 0, "failed": 0, "cleaned": 0}
        }
        self.job_data['jobs'].append(job_info)
        self._save_job_data()  # 保存到 job.json

        try:
            # 获取 client
            client = self.conn.get_client()
            
            # 获取源目录树和目标目录树
            with self.lock:  # 确保获取树的过程中不会有其他任务干扰
                source_tree = self.tree.get_source_tree(client, self.task.get_source_path())
                target_tree = self.tree.get_target_tree(self.task.get_target_path())
            
            # 执行增量同步（dump）
            self.dump.run(source_tree, target_tree, self.task)
            
            # 标记任务完成
            self.complete()
        
        except Exception as e:
            self.fail(f"Job failed with error: {str(e)}")

    def complete(self):
        """标记任务为完成，并记录日志"""
        self.end_time = datetime.now()  # 记录任务结束时间
        self.status = 'completed'  # 设置任务状态为已完成
        self.logs.append(f"Job {self.name} completed at {self.end_time}. Duration: {self.end_time - self.start_time}")

        # 更新 job.json 中的任务信息
        for job in self.job_data['jobs']:
            if job['name'] == self.name:
                job['status'] = 'completed'
                job['end_time'] = self.end_time.isoformat()
                job['result'] = {"success": 120, "failed": 5, "cleaned": 8}  # 假设的结果
        self._save_job_data()  # 保存更新后的任务数据

    def fail(self, reason):
        """任务失败时的处理"""
        self.status = 'failed'  # 设置任务状态为失败
        self.logs.append(f"Job {self.name} failed: {reason}")

        # 更新 job.json 中的任务信息
        for job in self.job_data['jobs']:
            if job['name'] == self.name:
                job['status'] = 'failed'
                job['end_time'] = datetime.now().isoformat()
                job['result'] = {"success": 0, "failed": 0, "cleaned": 0}  # 假设的结果
        self._save_job_data()  # 保存更新后的任务数据

    def update_logs(self, message):
        """更新日志"""
        self.logs.append(message)

    def get_logs(self):
        """获取日志"""
        return '\n'.join(self.logs)
