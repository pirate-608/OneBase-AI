"""Tests for KnowledgeBuilder: parsing, auto-scan, and edge cases."""

import pytest
from pathlib import Path
from onebase.builder import KnowledgeBuilder


class TestBuilderAutoScan:
    def test_auto_scan_base_dir(self, tmp_path):
        """Auto-scan a directory with nested structure."""
        (tmp_path / "overview.md").write_text("# Overview", encoding="utf-8")
        section = tmp_path / "section1"
        section.mkdir()
        (section / "k1.txt").write_text("knowledge", encoding="utf-8")
        builder = KnowledgeBuilder(str(tmp_path))
        # struct should be auto-generated (not "default" string)
        assert isinstance(builder.struct, dict)
        # overview.md should appear
        assert "overview" in builder.struct
        # nested file should appear under section
        assert "section1" in builder.struct
        assert "k1" in builder.struct["section1"]

    def test_auto_scan_ignores_hidden(self, tmp_path):
        """Hidden files/dirs should be excluded from scan."""
        (tmp_path / ".hidden").write_text("secret", encoding="utf-8")
        (tmp_path / "visible.txt").write_text("hello", encoding="utf-8")
        builder = KnowledgeBuilder(str(tmp_path))
        assert ".hidden" not in builder.struct
        assert "visible" in builder.struct

    def test_auto_scan_empty_dir(self, tmp_path):
        builder = KnowledgeBuilder(str(tmp_path))
        assert builder.struct == {}


class TestBuilderParse:
    def test_parse_with_explicit_struct(self, tmp_path):
        (tmp_path / "a.md").write_text("# Hello", encoding="utf-8")
        struct = {"intro": "a.md"}
        builder = KnowledgeBuilder(str(tmp_path), struct=struct)
        valid, missing = builder.parse()
        assert len(valid) == 1
        assert valid[0]["title"] == "intro"
        assert valid[0]["breadcrumbs"] == ["intro"]
        assert len(missing) == 0

    def test_parse_missing_file(self, tmp_path):
        struct = {"section": "nonexistent.md"}
        builder = KnowledgeBuilder(str(tmp_path), struct=struct)
        valid, missing = builder.parse()
        assert len(valid) == 0
        assert len(missing) == 1

    def test_parse_nested_struct(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "deep.txt").write_text("content", encoding="utf-8")
        struct = {"parent": {"child": "sub/deep.txt"}}
        builder = KnowledgeBuilder(str(tmp_path), struct=struct)
        valid, missing = builder.parse()
        assert len(valid) == 1
        assert valid[0]["breadcrumbs"] == ["parent", "child"]

    def test_parse_invalid_node_type(self, tmp_path):
        struct = {"bad": 12345}
        builder = KnowledgeBuilder(str(tmp_path), struct=struct)
        valid, missing = builder.parse()
        assert len(valid) == 0
        assert len(missing) == 1  # invalid format entry

    def test_default_keyword_triggers_autoscan(self, tmp_path):
        (tmp_path / "readme.md").write_text("hi", encoding="utf-8")
        builder = KnowledgeBuilder(str(tmp_path), struct="default")
        assert isinstance(builder.struct, dict)
        assert "readme" in builder.struct
