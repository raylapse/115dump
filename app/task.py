class Task:
    def __init__(self, data):
        """
        初始化 Task 实例
        
        :param data: 包含任务数据的字典
        """
        self.data = data  # 存储任务数据

    def get_name(self):
        """获取任务名称"""
        return self.data.get('name')

    def get_status(self):
        """获取任务状态"""
        return self.data.get('status', 'pending')

    def get_source_path(self):
        """获取源路径"""
        return self.data.get('source_path')

    def get_target_path(self):
        """获取目标路径"""
        return self.data.get('target_path')

    def get_rules(self):
        """获取任务规则"""
        return self.data.get('rules', [])

    def get_logs(self):
        """获取任务日志"""
        return self.data.get('logs', [])

    def get_created_at(self):
        """获取任务创建时间"""
        return self.data.get('created_at')

    def get_last_run_time(self):
        """获取任务最后运行时间"""
        return self.data.get('last_run_time')

    def get_next_run_time(self):
        """获取任务下次运行时间"""
        return self.data.get('next_run_time')

    # New update method
    def update(self, data):
        """更新任务数据"""
        self.data.update(data)  # 用传入的数据字典更新任务数据
