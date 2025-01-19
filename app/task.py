import json
import os
import uuid
from datetime import datetime

class Task:
    def __init__(self, task_file='config/tasks.json'):
        """
        初始化 TaskManager，加载或创建任务文件。
        
        :param task_file: 任务配置文件路径
        """
        self.task_file = task_file
        self.tasks_data = self._load_tasks()

    def _load_tasks(self):
        """加载任务数据，如果文件不存在则创建空任务列表"""
        if not os.path.exists(self.task_file):
            return {"tasks": []}
        with open(self.task_file, 'r') as f:
            return json.load(f)

    def _save_tasks(self):
        """保存任务数据到文件"""
        with open(self.task_file, 'w') as f:
            json.dump(self.tasks_data, f, indent=4)

    def create_task(self, task_info):
        """
        创建一个新任务，并将其保存到任务文件中
        
        :param task_info: 包含任务信息的字典
        :return: 任务的 UUID
        """
        task_uuid = str(uuid.uuid4())
        task_info['uuid'] = task_uuid
        task_info['created_at'] = datetime.now().isoformat()
        task_info['status'] = 'pending'  # 默认任务状态为 'pending'
        task_info['last_run_time'] = None
        task_info['next_run_time'] = None

        self.tasks_data['tasks'].append(task_info)
        self._save_tasks()

        return task_uuid

    def get_task_by_uuid(self, task_uuid):
        """
        根据 UUID 获取任务的详细信息
        
        :param task_uuid: 任务的 UUID
        :return: 任务的详细信息（字典），若任务不存在则返回 None
        """
        for task in self.tasks_data['tasks']:
            if task['uuid'] == task_uuid:
                return task
        return None

    def update_task(self, task_uuid, updated_info):
        """
        更新指定任务的信息
        
        :param task_uuid: 任务的 UUID
        :param updated_info: 更新的任务信息（字典）
        :return: 布尔值，表示更新是否成功
        """
        task = self.get_task_by_uuid(task_uuid)
        if task:
            task.update(updated_info)
            task['last_updated_at'] = datetime.now().isoformat()
            self._save_tasks()
            return True
        return False

    def delete_task(self, task_uuid):
        """
        删除指定的任务
        
        :param task_uuid: 任务的 UUID
        :return: 布尔值，表示删除是否成功
        """
        task = self.get_task_by_uuid(task_uuid)
        if task:
            self.tasks_data['tasks'] = [t for t in self.tasks_data['tasks'] if t['uuid'] != task_uuid]
            self._save_tasks()
            return True
        return False

    def list_tasks(self):
        """
        获取所有任务的简要信息
        
        :return: 任务的简要列表（只包含 UUID 和任务名）
        """
        return [{"uuid": task['uuid'], "name": task['name']} for task in self.tasks_data['tasks']]

# 示例用法
if __name__ == "__main__":
    task_manager = Task()

    # 创建一个新任务
    task_info = {
        "name": "Sample Task",
        "source_path": "/path/to/source",
        "target_path": "/path/to/target",
        "rules": [
            {"name": "Video Files", "extensions": ".mp4;.mkv", "method": "copy"},
            {"name": "Subtitle Files", "extensions": ".srt;.ass", "method": "symlink"}
        ],
        "enable_watch": True,
        "enable_sync": True,
        "sync_schedule": "0 12 * * *"
    }

    task_uuid = task_manager.create_task(task_info)
    print(f"Created Task UUID: {task_uuid}")

    # 获取任务详细信息
    task = task_manager.get_task_by_uuid(task_uuid)
    print(f"Task Details: {task}")

    # 更新任务
    updated_info = {"status": "running", "next_run_time": "2025-01-19T12:00:00"}
    task_manager.update_task(task_uuid, updated_info)
    print(f"Updated Task: {task_manager.get_task_by_uuid(task_uuid)}")

    # 列出所有任务
    print(f"All Tasks: {task_manager.list_tasks()}")

    # 删除任务
    task_manager.delete_task(task_uuid)
    print(f"Task after deletion: {task_manager.get_task_by_uuid(task_uuid)}")
