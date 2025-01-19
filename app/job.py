import conn
import tree
import dump

class Job:

    def __init__(self, name):
        self.name = name
        self.status = 'pending'
        self.logs = []
        # 初始化conn和dump实例
        self.conn = conn.Conn(self.name)
        self.tree = tree.Tree(self.name)
        self.dump = dump.Dump(self.name)

    def start(self):
        # 1. 通过 conn 拿到 client
        client = self.conn.get_client()
        # 2. 通过 tree 获取源目录树
        source_tree = self.tree.get_source_tree(client, self.name)
        # 3. 通过 tree 获取目标目录树
        target_tree = self.tree.get_target_tree(self.name)
        # 4. 初始化 dump 实例
        self.dump = dump.Dump(source_tree, target_tree)
        # 5. 开始 dump
        self.status = 'running'
        self.logs.append("Job started.")
        self.dump.run()

        # 6. 标记任务完成
        self.complete()

    def complete(self):
        self.status = 'completed'
        self.logs.append("Job completed.")

    def fail(self, reason):
        self.status = 'failed'
        self.logs.append(f"Job failed: {reason}")

    