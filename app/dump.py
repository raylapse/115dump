import os
import config

class Dump:
    def __init__(self, source_tree, target_tree):
        self.config = config.Config().get_config()
        self.source_tree = source_tree
        self.target_tree = target_tree

    # 执行dump
    def run(self):
        # 判断是否是全量dump
        if self.source_tree == '/':
            self.full_dump()
        else:
            self.delta_dump()

    # 全量dump，若目标目录已存在则删除后重新生成
    def full_dump(self):
        target_path = self.config['mount_path'] + self.target_tree[0]
        if os.path.exists(target_path):
            os.rmdir(target_path)
        self._dump()

    # 增量dump，只复制新增或修改的文件
    def delta_dump(self):
        self._dump()

    def _dump(self):
        # 比较源目录树和目标目录树，新增，删除，修改子目录和文件，并把操作记录到日志以及返回数组中
        pass