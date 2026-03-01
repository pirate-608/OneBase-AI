import yaml
import chardet
from pathlib import Path
from fastapi import APIRouter, HTTPException
from langchain_community.document_loaders import PyPDFLoader

router = APIRouter()


# 🌟 [2-3] 改为同步函数，避免文件 I/O 阻塞异步事件循环
# FastAPI 会自动在线程池中运行同步端点
@router.get("/tree")
def get_directory_tree():
    struct_config = "default"
    try:
        with open("onebase.yml", "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
            struct_config = config_data.get("knowledge_base", {}).get(
                "struct", "default"
            )
    except Exception:
        pass

    def build_tree_from_dict(struct_dict):
        tree = []
        for key, value in struct_dict.items():
            if isinstance(value, dict):
                tree.append(
                    {
                        "title": key,
                        "type": "folder",
                        "isOpen": False,
                        "children": build_tree_from_dict(value),
                    }
                )
            elif isinstance(value, str):
                tree.append({"title": key, "type": "file", "path": value})
        return tree

    def scan_dir(dir_path):
        tree = []
        if not dir_path.exists():
            return tree
        for item in sorted(dir_path.iterdir()):
            if item.name.startswith("."):
                continue
            if item.is_dir():
                children = scan_dir(item)
                if children:
                    tree.append(
                        {
                            "title": item.name,
                            "type": "folder",
                            "isOpen": False,
                            "children": children,
                        }
                    )
            elif item.suffix.lower() in [".md", ".txt", ".pdf"]:
                rel_path = item.relative_to(Path("base")).as_posix()
                tree.append({"title": item.stem, "type": "file", "path": rel_path})
        return tree

    if isinstance(struct_config, dict):
        return build_tree_from_dict(struct_config)
    else:
        return scan_dir(Path("base"))


# 🌟 [2-3] 改为同步函数，避免文件 I/O 和 PDF 解析阻塞异步事件循环
@router.get("/file/{file_path:path}")
def get_file_content(file_path: str):
    target_path = Path("base") / file_path
    try:
        if not target_path.resolve().is_relative_to(Path("base").resolve()):
            raise HTTPException(status_code=403, detail="禁止跨目录访问")

        ext = target_path.suffix.lower()

        # 🌟 1. 针对 PDF 文件的处理：提取文本预览
        if ext == ".pdf":
            try:
                loader = PyPDFLoader(str(target_path))
                docs = loader.load()
                # 拼接每一页的文本，并加上页码分割线，方便用户在 Markdown 渲染中阅读
                content = "\n\n".join(
                    [
                        f"**--- 第 {i+1} 页 ---**\n\n{doc.page_content}"
                        for i, doc in enumerate(docs)
                    ]
                )
                return {
                    "content": content
                    or "⚠️ 无法提取此 PDF 的文本内容（可能是纯图片扫描件）。"
                }
            except Exception as pdf_e:
                return {"content": f"⚠️ PDF 解析失败: {str(pdf_e)}"}

        # 🌟 2. 针对 TXT/MD 文件的处理：智能编码探测
        try:
            # 默认优先尝试 UTF-8
            content = target_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # 失败则使用 chardet 探测 (完美解决 Windows GBK/ANSI 等编码乱码问题)
            raw_data = target_path.read_bytes()
            detected = chardet.detect(raw_data)
            encoding = detected.get("encoding", "utf-8")
            try:
                content = raw_data.decode(encoding or "utf-8", errors="replace")
            except Exception:
                # 终极兜底：如果有无法识别的乱码字符，直接替换为问号，保证服务不死
                content = raw_data.decode("utf-8", errors="replace")

        return {"content": content}

    except Exception as e:
        return {"content": f"⚠️ 无法读取文件内容: {str(e)}"}
