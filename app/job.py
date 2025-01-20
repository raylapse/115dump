import conn
import tree
import dump
import task
from datetime import datetime
from task import Task
import threading
import logging
from utils import SocketIOHandler

class Job:
    def __init__(self, name, task):
        """
        初始化 Job 实例
        
        :param name: 任务名称
        :param task: 任务实例（Task 类实例），包含任务配置和规则
        """
        self.name = name
        self.task = task  # 传入的 Task 类实例，包含任务的配置和规则
        self.status = 'pending'  # 任务的初始状态
        self.logs = []  # 日志记录
        self.conn = conn.Conn()  # 初始化连接实例
        self.tree = tree.Tree()  # 初始化目录树实例
        self.dump = dump.Dump()  # 初始化 dump 实例
        self.start_time = None  # 任务开始时间
        self.end_time = None  # 任务结束时间
        self.lock = threading.Lock()  # 创建一个锁对象，用于线程同步
        self.logger = self._setup_logger()  # 初始化 logger

    def _setup_logger(self):
        """为每个 Job 设置独立的日志文件，并同时发送到 WebSocket"""
        logger = logging.getLogger(self.task_name)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        log_filename = f"{self.task_name}_{timestamp}.log"
        
        # 日志文件处理器
        file_handler = logging.FileHandler(f'logs/{log_filename}')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # SocketIO 处理器
        socketio_handler = SocketIOHandler(self.socketio, self.task_name)
        socketio_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)  # 将日志记录到文件
        logger.addHandler(socketio_handler)  # 将日志实时推送到 WebSocket
        logger.setLevel(logging.INFO)
        return logger
    
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

    def fail(self, reason):
        """任务失败时的处理"""
        self.status = 'failed'  # 设置任务状态为失败
        self.logs.append(f"Job {self.name} failed: {reason}")

    def update_logs(self, message):
        """更新日志"""
        self.logs.append(message)

    def get_logs(self):
        """获取日志"""
        return '\n'.join(self.logs)

    def schedule(self):
        """定时调度任务（例如使用 Cron 表达式）"""
        # 你可以在此方法中使用像 `schedule` 或 `APScheduler` 之类的库来设置定时任务
        pass


# 示例用法
if __name__ == "__main__":
    # 假设 Task 类实例已经被创建，task 是一个实例化后的 Task 对象
    task = Task()  # 假设 Task 类已经实现并被正确初始化
    
    # 创建并启动任务
    job = Job(name="Sync Job 1", task=task)
    job.start()
    
    # 输出任务日志
    print(job.get_logs())
