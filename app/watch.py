# Webhook 处理模块，监听来自 CloudDrive2 的 Webhook 消息

from flask import request

def handle_webhook(event_data):
    # 处理 Webhook 事件，更新任务
    print(f"Received webhook event: {event_data}")
    # 更新任务状态或触发任务处理
