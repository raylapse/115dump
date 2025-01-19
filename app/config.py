import json
import os

class Config:
    def __init__(self, config_file='config/config.json'):
        """
        初始化配置管理类，加载配置文件。
        
        :param config_file: 配置文件路径，默认为 'config/config.json'
        """
        self.config_file = config_file
        self.config_data = self._load_config()

    def _load_config(self):
        """加载并解析配置文件"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file {self.config_file} not found.")
        
        with open(self.config_file, 'r') as f:
            return json.load(f)

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

    def update_config(self, new_config):
        """更新配置文件"""
        self.config_data.update(new_config)
        with open(self.config_file, 'w') as f:
            json.dump(self.config_data, f, indent=4)

# 示例用法
if __name__ == "__main__":
    config = Config()

    # 打印配置信息
    print(f"Mount Path: {config.get_mount_path()}")
    print(f"STRM Prefix: {config.get_strm_prefix()}")
    print(f"Default Task Rules Template: {config.get_default_task_rules_template()}")
    print(f"Logging Level: {config.get_logging_level()}")
    print(f"Logging Retention Days: {config.get_logging_retention_days()}")
