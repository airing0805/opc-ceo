"""会话管理功能测试"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from claude_sdk_executor import sessions
from claude_sdk_executor.sessions import (
    get_project_hash,
    get_path_based_dirname,
    get_sessions_dir,
    parse_session_metadata,
    find_session_file,
    list_sessions,
    list_all_projects,
    get_session_detail,
    delete_session,
)


class TestProjectHash:
    """项目哈希生成测试"""

    def test_get_project_hash_windows(self):
        """测试 Windows 路径哈希"""
        result = get_project_hash("E:/workspaces/test")
        assert isinstance(result, str)
        assert len(result) == 16

    def test_get_project_hash_linux(self):
        """测试 Linux 路径哈希"""
        result = get_project_hash("/home/user/test")
        assert isinstance(result, str)
        assert len(result) == 16

    def test_path_based_dirname_windows(self):
        """测试 Windows 路径目录名"""
        result = get_path_based_dirname("E:/workspaces/test")
        assert "e-workspaces-test" == result

    def test_path_based_dirname_linux(self):
        """测试 Linux 路径目录名"""
        result = get_path_based_dirname("/home/user/test")
        assert "-home-user-test" == result


class TestSessionMetadata:
    """会话元数据解析测试"""

    @patch("builtins.open")
    def test_parse_valid_session(self, mock_open):
        """测试解析有效会话文件"""
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.__iter__.return_value = iter([
            '{"type":"user","message":{"content":"测试内容"},"sessionId":"test-123"}\n',
            '{"type":"assistant","message":{"content":[{"type":"text","text":"响应内容"}]}}\n',
        ])
        mock_file.stat.return_value.st_size = 100
        mock_open.return_value = mock_file

        result = parse_session_metadata(Path("test.jsonl"))
        assert result["id"] == "test-123"
        assert result["title"] == "测试内容"
        assert result["message_count"] == 2

    @patch("builtins.open")
    def test_parse_invalid_json(self, mock_open):
        """测试解析无效 JSON"""
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.__iter__.return_value = iter(['invalid json\n'])
        mock_file.stat.return_value.st_size = 100
        mock_open.return_value = mock_file

        result = parse_session_metadata(Path("test.jsonl"))
        assert result["message_count"] == 0


class TestSessionList:
    """会话列表测试"""

    @patch("claude_sdk_executor.sessions.get_sessions_dir")
    def test_list_empty_sessions(self, mock_dir):
        """测试列出空会话列表"""
        mock_dir.return_value.exists.return_value = False
        result = list_sessions("/test/path")
        assert result == []

    @patch("claude_sdk_executor.sessions.get_sessions_dir")
    @patch("claude_sdk_executor.sessions.parse_session_metadata")
    def test_list_sessions_sorting(self, mock_parse, mock_dir):
        """测试会话列表按时间排序"""
        mock_dir.return_value.exists.return_value = True
        mock_dir.return_value.glob.return_value = [Path("s1.jsonl"), Path("s2.jsonl")]
        mock_parse.side_effect = [
            {"id": "s1", "timestamp": "2026-02-23T10:00:00Z"},
            {"id": "s2", "timestamp": "2026-02-24T10:00:00Z"},
        ]

        result = list_sessions("/test/path")
        assert result[0]["id"] == "s2"  # 最新在前


class TestSessionDetail:
    """会话详情测试"""

    @patch("claude_sdk_executor.sessions.find_session_file")
    @patch("claude_sdk_executor.sessions.parse_session_metadata")
    def test_get_existing_session(self, mock_parse, mock_find):
        """测试获取存在的会话"""
        mock_find.return_value = Path("test-123.jsonl")
        mock_parse.return_value = {"id": "test-123"}

        result = get_session_detail("test-123")
        assert result["id"] == "test-123"
        assert result["file_path"] == "test-123.jsonl"

    @patch("claude_sdk_executor.sessions.find_session_file")
    def test_get_missing_session(self, mock_find):
        """测试获取不存在的会话"""
        mock_find.return_value = None
        result = get_session_detail("nonexistent")
        assert result is None


class TestDeleteSession:
    """删除会话测试"""

    @patch("claude_sdk_executor.sessions.find_session_file")
    def test_delete_existing_session(self, mock_find):
        """测试删除存在的会话"""
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_find.return_value = mock_file

        result = delete_session("test-123")
        assert result is True
        mock_file.unlink.assert_called_once()

    @patch("claude_sdk_executor.sessions.find_session_file")
    def test_delete_missing_session(self, mock_find):
        """测试删除不存在的会话"""
        mock_find.return_value = None
        result = delete_session("nonexistent")
        assert result is False
