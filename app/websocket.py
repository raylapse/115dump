from flask_socketio import emit

def send_job_status_update(job_name, status):
    emit('status_update', {'task_name': job_name, 'status': status}, broadcast=True)
