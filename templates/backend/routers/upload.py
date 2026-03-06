import os
import shutil
import logging
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    FEATURE_FILE_UPLOAD,
)
from deps import get_vector_store

router = APIRouter()
logger = logging.getLogger("onebase.backend")

# 🌟 [3-4] 文件上传大小限制，防止资源滥用
MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB


@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    # 🌟 [Step2] Feature Flag 门控：配置关闭时拒绝上传
    if not FEATURE_FILE_UPLOAD:
        raise HTTPException(status_code=403, detail="文件上传功能已关闭")

    try:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in [".pdf", ".txt", ".md"]:
            raise HTTPException(
                status_code=400, detail="目前仅支持上传 PDF, TXT 或 MD 格式的文件"
            )

        # 🌟 [3-4] 读取内容并检查大小
        contents = file.file.read()
        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"文件大小超过 {MAX_UPLOAD_SIZE // (1024*1024)}MB 限制",
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        try:
            loader = (
                PyPDFLoader(tmp_path)
                if ext == ".pdf"
                else TextLoader(tmp_path, autodetect_encoding=True)
            )
            docs = loader.load()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(docs)

        for chunk in chunks:
            chunk.metadata["breadcrumbs"] = f"User Upload > {file.filename}"

        vector_store = get_vector_store()
        vector_store.add_documents(chunks)

        logger.info(
            "文件上传成功: %s (%d chunks, %d bytes)",
            file.filename,
            len(chunks),
            len(contents),
        )
        return {"status": "success", "filename": file.filename, "chunks": len(chunks)}

    except HTTPException:
        raise  # 上面主动抛的 400/413 直接透传
    except Exception as e:
        # 🌟 [3-5] 生产环境不泄漏内部异常细节，详情写日志
        logger.error(
            "文件上传处理失败 [%s]: %s",
            file.filename,
            e,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="文件处理失败，请稍后重试或检查文件格式"
        )
