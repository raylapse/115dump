from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import config
from job import Job

app = Flask(__name__)
socketio = SocketIO(app)

# 路由和其他逻辑
@app.route('/')
def index():
    return render_template('index.html')

# WebSocket or HTTP API method to manually trigger a job
@app.route('/api/job/start', methods=['POST'])
def start_job():
    task_name = request.json.get('task_name')  # 从请求中获取任务名称
    task = config.get_task(task_name)  # 获取任务实例
    if task:
        job = Job(task_name, task)
        job.start()  # 启动任务
        return jsonify({"status": "success", "message": "Job started successfully."})
    return jsonify({"status": "failure", "message": "Task not found."})

# 监听 WebSocket 事件
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('status_update', {'message': 'Connected to WebSocket server'})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

# WebSocket 任务状态更新
def send_job_status_update(job_name, status):
    emit('status_update', {'task_name': job_name, 'status': status}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
