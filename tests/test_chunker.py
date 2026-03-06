"""Tests for DocumentProcessor chunking logic."""

import pytest
from pathlib import Path
from onebase.chunker import DocumentProcessor


class TestDocumentProcessor:
    def test_process_txt_file(self, tmp_path):
        f = tmp_path / "hello.txt"
        f.write_text("Hello world. This is a test document.", encoding="utf-8")
        processor = DocumentProcessor(chunk_size=500)
        docs = [
            {"file_path": f, "title": "Hello", "breadcrumbs": ["greetings", "Hello"]}
        ]
        chunks = processor.process(docs)
        assert len(chunks) >= 1
        assert chunks[0].metadata["title"] == "Hello"
        assert chunks[0].metadata["breadcrumbs"] == "greetings > Hello"
        assert chunks[0].metadata["source_file"] == "hello.txt"

    def test_process_md_file(self, tmp_path):
        f = tmp_path / "readme.md"
        f.write_text("# Heading\n\nSome paragraph content here.", encoding="utf-8")
        processor = DocumentProcessor(chunk_size=500)
        docs = [{"file_path": f, "title": "Readme", "breadcrumbs": ["Readme"]}]
        chunks = processor.process(docs)
        assert len(chunks) >= 1

    def test_process_unsupported_ext_skipped(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("a,b,c", encoding="utf-8")
        processor = DocumentProcessor(chunk_size=500)
        docs = [{"file_path": f, "title": "Data", "breadcrumbs": ["Data"]}]
        chunks = processor.process(docs)
        assert len(chunks) == 0

    def test_process_empty_list(self):
        processor = DocumentProcessor(chunk_size=500)
        chunks = processor.process([])
        assert chunks == []

    def test_chunk_size_splits_large_doc(self, tmp_path):
        f = tmp_path / "large.txt"
        # ~2000 chars → with chunk_size=200, expect multiple chunks
        f.write_text("word " * 400, encoding="utf-8")
        processor = DocumentProcessor(chunk_size=200, chunk_overlap=20)
        docs = [{"file_path": f, "title": "Large", "breadcrumbs": ["Large"]}]
        chunks = processor.process(docs)
        assert len(chunks) > 1

    def test_breadcrumbs_joined(self, tmp_path):
        f = tmp_path / "note.txt"
        f.write_text("content", encoding="utf-8")
        processor = DocumentProcessor(chunk_size=500)
        docs = [{"file_path": f, "title": "Note", "breadcrumbs": ["A", "B", "Note"]}]
        chunks = processor.process(docs)
        assert chunks[0].metadata["breadcrumbs"] == "A > B > Note"
