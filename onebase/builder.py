import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Union

class KnowledgeBuilder:
    def __init__(self, base_path: str, struct: Union[Dict[str, Any], str, None] = None):
        self.base_path = Path(base_path)
        
        # 🌟 核心改造：如果 struct 是空的、None 或者填了 "default"，则触发自动扫描
        if not struct or struct == "default":
            self.struct = self._auto_scan(self.base_path)
        else:
            self.struct = struct
            
        self.valid_docs = [] 
        self.missing_files = []

    def _auto_scan(self, current_dir: Path) -> Dict[str, Any]:
        """递归扫描物理目录，自动生成与 YAML 结构相同的字典树"""
        result = {}
        if not current_dir.exists() or not current_dir.is_dir():
            return result
            
        # 支持的文件类型
        supported_exts = ['.md', '.txt', '.pdf']
            
        for item in sorted(current_dir.iterdir()):
            # 忽略隐藏文件或目录 (如 .git, .DS_Store)
            if item.name.startswith('.'):
                continue
                
            if item.is_dir():
                # 递归扫描子目录，如果子目录里有有效文件，才加入树中
                sub_tree = self._auto_scan(item)
                if sub_tree:
                    result[item.name] = sub_tree
            elif item.is_file() and item.suffix.lower() in supported_exts:
                # 去除文件后缀名，作为显示的标题 (Key)
                # item.stem 就是去掉后缀的文件名，比如 overview.md -> overview
                title = item.stem 
                # 计算相对于 base 目录的路径作为 Value
                rel_path = item.relative_to(self.base_path).as_posix()
                result[title] = rel_path
                
        return result

    def parse(self) -> Tuple[List[dict], List[str]]:
        """执行结构解析与文件校验"""
        self._traverse(self.struct, breadcrumbs=[])
        return self.valid_docs, self.missing_files

    def _traverse(self, node: Any, breadcrumbs: List[str]):
        """递归遍历结构树"""
        if isinstance(node, dict):
            for key, value in node.items():
                self._traverse(value, breadcrumbs + [key])
                
        elif isinstance(node, str):
            file_path = self.base_path / node
            title = breadcrumbs[-1] if breadcrumbs else "Untitled"
            
            if file_path.exists() and file_path.is_file():
                self.valid_docs.append({
                    "title": title,
                    "breadcrumbs": breadcrumbs,
                    "file_path": file_path
                })
            else:
                self.missing_files.append(str(file_path))
                
        else:
            self.missing_files.append(f"无效的配置格式于 {' -> '.join(breadcrumbs)}")