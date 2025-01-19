from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# 路由和其他逻辑
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/job', methods=['GET'])
def get_tasks():
    # 返回任务列表的 API 示例
    return {"Jobs": []}

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
