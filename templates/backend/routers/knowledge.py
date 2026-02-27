import yaml
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/tree")
async def get_directory_tree():
    struct_config = "default"
    try:
        with open("onebase.yml", "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
            struct_config = config_data.get("knowledge_base", {}).get("struct", "default")
    except Exception:
        pass

    def build_tree_from_dict(struct_dict):
        tree = []
        for key, value in struct_dict.items():
            if isinstance(value, dict):
                tree.append({"title": key, "type": "folder", "isOpen": False, "children": build_tree_from_dict(value)})
            elif isinstance(value, str):
                tree.append({"title": key, "type": "file", "path": value})
        return tree

    def scan_dir(dir_path):
        tree = []
        if not dir_path.exists(): return tree
        for item in sorted(dir_path.iterdir()):
            if item.name.startswith('.'): continue
            if item.is_dir():
                children = scan_dir(item)
                if children: tree.append({"title": item.name, "type": "folder", "isOpen": False, "children": children})
            elif item.suffix.lower() in ['.md', '.txt', '.pdf']:
                rel_path = item.relative_to(Path("base")).as_posix()
                tree.append({"title": item.stem, "type": "file", "path": rel_path})
        return tree

    if isinstance(struct_config, dict):
        return build_tree_from_dict(struct_config)
    else:
        return scan_dir(Path("base"))

@router.get("/file/{file_path:path}")
async def get_file_content(file_path: str):
    target_path = Path("base") / file_path
    try:
        if not target_path.resolve().is_relative_to(Path("base").resolve()):
            raise HTTPException(status_code=403, detail="禁止跨目录访问")
        return {"content": target_path.read_text(encoding='utf-8')}
    except Exception as e:
        return {"content": f"⚠️ 无法读取文件内容: {str(e)}"}