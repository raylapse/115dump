import json
import os
from datetime import datetime
from task import Task

class Config:
    def __init__(self, config_file='config/config.json', tasks_file='config/tasks.json'):
        self.config_file = config_file
        self.tasks_file = tasks_file
        self.config_data = self._load_config()
        self.tasks_data = self._load_tasks()

    def _load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file {self.config_file} not found.")
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def _load_tasks(self):
        """加载任务配置"""
        if not os.path.exists(self.tasks_file):
            return {"tasks": []}
        with open(self.tasks_file, 'r') as f:
            return json.load(f)

    def _save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config_data, f, indent=4)

    def _save_tasks(self):
        """保存任务配置"""
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks_data, f, indent=4)

    # CRUD for tasks
    def create_task(self, data):
        # 唯一性检查：检查任务名称是否已经存在
        if self.get_task(data['name']):
            raise ValueError(f"Task name '{data['name']}' already exists. Task names must be unique.")
        
        # rules 检查：同一种扩展名只能有一种 method
        seen_extensions = {}
        for rule in data['rules']:
            for ext in rule['extensions'].split(';'):
                if ext in seen_extensions:
                    raise ValueError(f"Extension '{ext}' already mapped to '{seen_extensions[ext]}' method. Multiple methods for the same extension are not allowed.")
                seen_extensions[ext] = rule['method']

        # 创建一个新的 Task 实例并保存到任务列表
        task = Task(data)
        self.tasks_data['tasks'].append(task.task_data)
        self._save_tasks()

    def get_task(self, task_name):
        """根据 name 获取任务"""
        for task in self.tasks_data['tasks']:
            if task['name'] == task_name:
                return Task(task)  # 返回 Task 实例
        return None

    def update_task(self, data):
        for existing_task in self.tasks_data['tasks']:
            if existing_task['name'] == data['name']:
                existing_task.update(data)  # 用 Task 的 task_data 更新现有任务的数据字典
                self._save_tasks()
                return True
        return False

    def delete_task(self, task_name):
        """删除任务"""
        task = self.get_task(task_name)
        if task:
            self.tasks_data['tasks'] = [t for t in self.tasks_data['tasks'] if t['name'] != task_name]
            self._save_tasks()
            return True
        return False

    def list_tasks(self):
        """列出所有任务"""
        return [Task(task) for task in self.tasks_data['tasks']]

    # 获取全局配置
    def get_mount_path(self):
        """获取挂载路径"""
        return self.config_data.get("mount_path", "")

    def get_strm_prefix(self):
        """获取 strm 前缀"""
        return self.config_data.get("strm_prefix", "")

    def get_default_task_rules_template(self):
        """获取任务默认规则模板"""
        return self.config_data.get("default_task_rules_template", {})

    def get_logging_level(self):
        """获取日志级别"""
        return self.config_data.get("logging", {}).get("level", "info")

    def get_logging_retention_days(self):
        """获取日志保留天数"""
        return self.config_data.get("logging", {}).get("retention_days", 30)
