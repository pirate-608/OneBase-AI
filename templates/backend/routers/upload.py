import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_postgres.vectorstores import PGVector

from config import SITE_NAME, DB_URL, EMBEDDING_PROVIDER, EMBEDDING_MODEL
from factory import ModelFactory

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.pdf', '.txt', '.md']:
            raise HTTPException(status_code=400, detail="目前仅支持上传 PDF, TXT 或 MD 格式的文件")

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        try:
            loader = PyPDFLoader(tmp_path) if ext == '.pdf' else TextLoader(tmp_path, autodetect_encoding=True)
            docs = loader.load()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(docs)

        for chunk in chunks:
            chunk.metadata['breadcrumbs'] = f"User Upload > {file.filename}"

        embeddings = ModelFactory.get_embedding_model(EMBEDDING_PROVIDER, EMBEDDING_MODEL)
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=SITE_NAME.replace(" ", "_").lower(),
            connection=DB_URL,
            use_jsonb=True,
        )
        vector_store.add_documents(chunks)
        
        return {"status": "success", "filename": file.filename, "chunks": len(chunks)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")