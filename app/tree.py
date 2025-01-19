import os
from p115client import tool

class Tree:

    def get_source_tree(self, client, path):
        ### 解析115目录树，生成目录数组
        try:
            it = tool.export_dir_parse_iter(
                client=client, 
                export_file_ids=path, 
                target_pid=path, 
                parse_iter=tool.parse_export_dir_as_dict_iter, 
                delete=True,
                async_=False,
                show_clock=True)
            i = 0
            path_index = {}
            source_tree = []
            for item in it:
                i += 1
                parent = path_index.get(item['parent_key'])
                if parent is None:
                    item['path'] = ''
                else:
                    if i == 2 and path.endswith(item['name']):
                        item['path'] = path
                    else:
                        item['path'] = "{0}/{1}".format(parent['path'], item['name'])
                path_index[item['key']] = item
                if item['path'] != '':
                    source_tree.append(item['path'].replace('/', os.sep))
            return source_tree
        except Exception as e:
            ### self.logger.error('生成目录树出错: %s' % e)
            raise e
        
    def get_target_tree(self, base_dir: str, root_dir: str, target_tree: list):
        ### 获取目标路径目录树，用于处理差异
        if not os.path.exists(root_dir):
            return target_tree
        dirs = os.listdir(root_dir)
        for dir in dirs:
            item = os.path.join(root_dir, dir)
            target_tree.append(item.lstrip(base_dir + os.sep))
            if os.path.isfile(item):
                # 如果是文件，则不用递归
                continue
            self.get_target_tree(base_dir, item, target_tree)
        return target_tree