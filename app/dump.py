import os
import shutil
import config

class Dump:
    def __init__(self, source_tree, target_tree, task):
        """
        初始化 Dump 实例

        :param source_tree: 源目录树（路径列表）
        :param target_tree: 目标目录树（路径列表）
        :param task: 当前任务配置
        """
        self.config = config.Config().get_config()
        self.source_tree = source_tree
        self.target_tree = target_tree
        self.task = task  # 任务配置，决定是否执行文件操作

    def run(self):
        """
        执行 dump 操作：根据 source 和 target tree 的差异，执行新增、删除操作
        """
        added, deleted = self.parseTree(self.source_tree, self.target_tree)
        self.add_files(added)
        self.delete_files(deleted)

    def parseTree(self, src_tree_list: list, dest_tree_list: list) -> tuple[list, list]:
        """
        解析源目录（src_tree_list）和目标目录（dest_tree_list），
        返回新增文件列表（added），删除文件列表（deleted）

        根据 rules 中的 method，决定如何处理文件。
        """
        added = []  # 新增的文件（需要生成 .strm 文件等）
        deleted = []  # 需要删除的文件

        # 遍历源目录（src_tree_list），找出新增的文件
        for src_item in src_tree_list:
            # 获取当前文件的处理方法（根据 rules 中的配置）
            method = self._get_method(src_item)
            
            if method == 'ignore':
                continue  # 忽略该文件，不做处理
            
            # 如果 method 是 'strm'，则需要生成 .strm 文件
            if method == 'strm':
                strm_file = src_item + '.strm'  # 直接生成 .strm 文件名
                if strm_file not in dest_tree_list:  # 如果目标目录没有该 .strm 文件
                    added.append(src_item)  # 将源文件加入新增列表，用于创建 .strm 文件
            else:
                # 对于其他文件（如 copy, symlink, virtual），直接加入新增列表
                added.append(src_item)

        # 遍历目标目录（dest_tree_list），找出需要删除的文件
        for dest_item in dest_tree_list:
            # 获取当前目标文件的处理方法（根据 rules 中的配置）
            method = self._get_method(dest_item)
            
            if method == 'ignore':
                continue  # 忽略该文件，不做处理
            
            # 如果目标目录中是 .strm 文件，检查对应的源文件是否存在
            if method == 'strm':
                corresponding_source_file = dest_item.replace('.strm', '')  # 去掉 .strm 后缀，得到源文件路径
                if corresponding_source_file not in src_tree_list:  # 如果源目录没有对应的文件
                    deleted.append(dest_item)  # 删除目标目录中的 .strm 文件
            else:
                # 删除其他类型的文件（copy, symlink, virtual）
                deleted.append(dest_item)

        return added, deleted

    def _process_file(self, file_path):
        """根据任务配置执行文件的处理操作"""
        if self._is_ignored(file_path):
            return
        elif self._is_copyable(file_path):
            self._copy_file(file_path)
        elif self._is_symlink(file_path):
            self._create_symlink(file_path)
        elif self._is_strm(file_path):
            self._create_strm(file_path)
        elif self._is_virtual(file_path):
            self._create_virtual_file(file_path)

    def _is_ignored(self, file_path):
        """ 判断是否需要忽略文件 """
        return self._get_method(file_path) == 'ignore'

    def _is_copyable(self, file_path):
        """ 判断文件是否需要复制 """
        return self._get_method(file_path) == 'copy'

    def _is_symlink(self, file_path):
        """ 判断文件是否需要创建软链接 """
        return self._get_method(file_path) == 'symlink'

    def _is_strm(self, file_path):
        """ 判断文件是否需要创建 .strm 文件 """
        return self._get_method(file_path) == 'strm'

    def _is_virtual(self, file_path):
        """ 判断文件是否需要创建 0KB 虚拟文件 """
        return self._get_method(file_path) == 'virtual'

    def _get_method(self, file_path):
        """ 根据文件的扩展名从任务配置中获取对应的处理方法 """
        file_extension = os.path.splitext(file_path)[1]
        for rule in self.task['rules']:
            if file_extension in rule['extensions']:
                return rule['method']
        return 'ignore'  # 默认忽略

    def _copy_file(self, file_path):
        """ 复制文件 """
        target_path = os.path.join(self.config["mount_path"], file_path)
        target_dir = os.path.dirname(target_path)

        # 确保目标目录存在
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        shutil.copy(file_path, target_path)
        print(f"Copied file: {file_path} to {target_path}")

    def _create_symlink(self, file_path):
        """ 创建软链接 """
        target_path = os.path.join(self.config["mount_path"], file_path)
        target_dir = os.path.dirname(target_path)

        # 确保目标目录存在
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        os.symlink(file_path, target_path)
        print(f"Created symlink for: {file_path} to {target_path}")

    def _create_strm(self, file_path):
        """ 创建 .strm 文件 """
        strm_path = os.path.join(self.config["mount_path"], file_path + '.strm')
        strm_prefix = self.config.get("strm_prefix", "")
        strm_url = strm_prefix + file_path
        with open(strm_path, 'w') as f:
            f.write(strm_url)
        print(f"Created .strm file for: {file_path}")

    def _create_virtual_file(self, file_path):
        """ 创建 0KB 虚拟文件 """
        target_path = os.path.join(self.config["mount_path"], file_path)
        target_dir = os.path.dirname(target_path)

        # 确保目标目录存在
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        with open(target_path, 'wb') as f:
            pass  # 创建一个空的 0KB 文件
        print(f"Created virtual file for: {file_path}")

    def _delete_file(self, file_path):
        """ 删除目标文件 """
        target_path = os.path.join(self.config["mount_path"], file_path)

        # 确保目标目录存在，避免删除操作失败
        target_dir = os.path.dirname(target_path)
        if not os.path.exists(target_dir):
            print(f"Directory {target_dir} does not exist. Skipping deletion for: {file_path}")
            return

        if os.path.exists(target_path):
            os.remove(target_path)
            print(f"Deleted file: {target_path}")
        else:
            print(f"File not found for deletion: {target_path}")
