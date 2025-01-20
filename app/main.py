import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import threading

# app = Flask(__name__)
app = Flask(__name__, template_folder="../web")  # 指定web文件夹
socketio = SocketIO(app)

# 任务和全局设置
TASKS_FILE = "config/task.json"
CONFIG_FILE = "config/config.json"
LOGS_FOLDER = "logs"
JOB_FILE = "cache/job.json"

# 加载任务数据
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)['tasks']
    return []

# 加载全局配置
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

# 启动任务
def start_job(task_name):
    task = None
    tasks = load_tasks()
    for t in tasks:
        if t['name'] == task_name:
            task = t
            break
    if task:
        job = Job(task_name, task)
        job.start()

    return jsonify({"status": "success", "message": "Job started successfully."}) if job else jsonify({"status": "failure", "message": "Task not found."})

class Job:
    def __init__(self, name, task):
        self.name = f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"  # Job name includes timestamp
        self.task = task
        self.status = "pending"
        self.start_time = None
        self.end_time = None
        self.logs = []
        self.result = {"success": 0, "failed": 0, "cleaned": 0}
        self.lock = threading.Lock()

    def start(self):
        """启动任务"""
        self.start_time = datetime.now()
        self.status = "running"
        self.logs.append(f"Job {self.name} started at {self.start_time}.")
        # 模拟执行任务
        try:
            # 任务模拟操作
            # 这里可以执行具体的任务操作，如调用任务相关的同步/清理等功能
            self.result['success'] = 120
            self.result['failed'] = 5
            self.result['cleaned'] = 8
            self.end_time = datetime.now()
            self.status = "completed"
            self.logs.append(f"Job {self.name} completed at {self.end_time}. Duration: {self.end_time - self.start_time}")
            # 记录到jobs.json
            self.save_job_result()
        except Exception as e:
            self.status = "failed"
            self.logs.append(f"Job {self.name} failed with error: {str(e)}")
            self.save_job_result()

    def save_job_result(self):
        """将任务运行结果保存到job.json"""
        if not os.path.exists(JOB_FILE):
            with open(JOB_FILE, 'w') as f:
                json.dump({"jobs": []}, f)
        
        with open(JOB_FILE, 'r') as f:
            data = json.load(f)

        job_data = {
            "name": self.name,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "result": self.result
        }

        data['jobs'].append(job_data)

        with open(JOB_FILE, 'w') as f:
            json.dump(data, f, indent=4)

# 任务管理
@app.route('/')
def index():
    tasks = load_tasks()
    return render_template('index.html', tasks=tasks)

@app.route('/api/task/start', methods=['POST'])
def api_start_task():
    task_name = request.json.get('task_name')
    return start_job(task_name)

@app.route('/api/task/create', methods=['POST'])
def api_create_task():
    task_data = request.json
    tasks = load_tasks()

    # 启动任务创建逻辑
    new_task = {
        "name": task_data['name'],
        "source_path": task_data['source_path'],
        "target_path": task_data['target_path'],
        "rules": task_data['rules'],
        "enabled": task_data['enabled']
    }
    tasks.append(new_task)
    
    # 保存任务数据
    with open(TASKS_FILE, 'w') as f:
        json.dump({"tasks": tasks}, f, indent=4)
    
    return jsonify({"status": "success", "message": "Task created successfully."})

@app.route('/api/logs', methods=['GET'])
def api_get_logs():
    job_name = request.args.get('job_name')
    logs = []
    with open(JOB_FILE, 'r') as f:
        data = json.load(f)
        for job in data['jobs']:
            if job['name'] == job_name:
                logs.append(job)
    return jsonify(logs)

@app.route('/api/global_settings', methods=['GET', 'POST'])
def api_global_settings():
    config = load_config()
    
    if request.method == 'POST':
        new_config = request.json
        with open(CONFIG_FILE, 'w') as f:
            json.dump(new_config, f, indent=4)
        return jsonify({"status": "success", "message": "Settings updated successfully."})

    return jsonify(config)

# WebSocket 实时更新任务日志
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('status_update', {'message': 'Connected to WebSocket server'})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('log_request')
def handle_log_request(data):
    job_name = data['job_name']
    with open(JOB_FILE, 'r') as f:
        data = json.load(f)
        for job in data['jobs']:
            if job['name'] == job_name:
                emit('log_update', {'task_name': job_name, 'logs': job['result']})

if __name__ == "__main__":
    socketio.run(app, debug=True)
