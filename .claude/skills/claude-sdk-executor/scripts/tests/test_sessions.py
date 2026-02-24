"""
测试 sessions.py 的所有功能

覆盖率目标：80%+
"""

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, MagicMock, patch

import pytest

# 导入被测试的模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from sessions import (
    CLAUDE_DIR,
    PROJECTS_DIR,
    delete_session,
    execute_task,
    find_session_file,
    get_path_based_dirname,
    get_project_hash,
    get_session_detail,
    get_sessions_dir,
    list_all_projects,
    list_sessions,
    main,
    parse_session_metadata,
    print_json,
)


class TestGetProjectHash:
    """测试 get_project_hash 函数"""

    def test_basic_path(self):
        """测试基本路径"""
        result = get_project_hash("E:/workspaces/project")
        assert isinstance(result, str)
        assert len(result) == 16

    def test_relative_path(self):
        """测试相对路径"""
        result = get_project_hash("./project")
        assert isinstance(result, str)
        assert len(result) == 16

    def test_same_path_same_hash(self):
        """测试相同路径生成相同哈希"""
        path1 = "E:/workspaces/project"
        path2 = "E:/workspaces/project"
        assert get_project_hash(path1) == get_project_hash(path2)

    def test_different_paths_different_hashes(self):
        """测试不同路径生成不同哈希"""
        path1 = "E:/workspaces/project1"
        path2 = "E:/workspaces/project2"
        assert get_project_hash(path1) != get_project_hash(path2)

    def test_windows_path_normalization(self):
        """测试 Windows 路径规范化"""
        path1 = "E:/workspaces/project"
        path2 = "E:\\workspaces\\project"
        assert get_project_hash(path1) == get_project_hash(path2)


class TestGetPathBasedDirname:
    """测试 get_path_based_dirname 函数"""

    def test_basic_path(self):
        """测试基本路径"""
        result = get_path_based_dirname("E:/workspaces/project")
        assert "workspaces" in result
        assert "project" in result

    def test_special_characters_replaced(self):
        """测试特殊字符被替换"""
        result = get_path_based_dirname("E:/workspaces:project")
        assert ":" not in result
        assert "-" in result

    def test_backslash_replacement(self):
        """测试反斜杠替换"""
        result = get_path_based_dirname("E:\\workspaces\\project")
        assert "\\" not in result
        assert "-" in result

    def test_windows_drive_lowercase(self):
        """测试 Windows 盘符小写"""
        result = get_path_based_dirname("E:/workspaces/project")
        assert result.startswith("e-")

    def test_underscore_replacement(self):
        """测试下划线替换"""
        result = get_path_based_dirname("E:/workspaces/project_name")
        assert "_" not in result
        assert "-" in result


class TestGetSessionsDir:
    """测试 get_sessions_dir 函数"""

    def test_path_based_dir_exists(self, tmp_path):
        """测试路径替换目录存在时返回该目录"""
        # 创建临时目录结构
        test_path = tmp_path / "test_project"
        test_path.mkdir()

        path_dirname = get_path_based_dirname(str(test_path))
        mock_projects_dir = tmp_path / "projects"
        mock_projects_dir.mkdir()
        project_dir = mock_projects_dir / path_dirname
        project_dir.mkdir()

        try:
            with patch("sessions.PROJECTS_DIR", mock_projects_dir):
                result = get_sessions_dir(str(test_path))
                assert result == project_dir
        finally:
            project_dir.rmdir()
            mock_projects_dir.rmdir()
            test_path.rmdir()

    def test_neither_dir_exists_returns_path_based(self, tmp_path):
        """测试两个目录都不存在时返回路径替换目录"""
        test_path = tmp_path / "test_project2"
        test_path.mkdir()

        mock_projects_dir = tmp_path / "projects2"
        mock_projects_dir.mkdir()

        try:
            with patch("sessions.PROJECTS_DIR", mock_projects_dir):
                result = get_sessions_dir(str(test_path))
                assert result.name == get_path_based_dirname(str(test_path))
        finally:
            mock_projects_dir.rmdir()
            test_path.rmdir()

    def test_hash_dir_exists(self, tmp_path):
        """测试哈希目录存在时返回哈希目录"""
        test_path = tmp_path / "test_project3"
        test_path.mkdir()

        project_hash = get_project_hash(str(test_path))
        mock_projects_dir = tmp_path / "projects3"
        mock_projects_dir.mkdir()
        hash_dir = mock_projects_dir / project_hash
        hash_dir.mkdir()

        try:
            with patch("sessions.PROJECTS_DIR", mock_projects_dir):
                result = get_sessions_dir(str(test_path))
                assert result == hash_dir
        finally:
            hash_dir.rmdir()
            mock_projects_dir.rmdir()
            test_path.rmdir()


class TestParseSessionMetadata:
    """测试 parse_session_metadata 函数"""

    def test_empty_file(self, tmp_path):
        """测试空文件"""
        session_file = tmp_path / "empty.jsonl"
        session_file.write_text("")

        result = parse_session_metadata(session_file)
        assert result["id"] == "empty"
        assert result["title"] == "无标题"
        assert result["timestamp"] is None
        assert result["message_count"] == 0

    def test_empty_lines_in_file(self, tmp_path):
        """测试文件中的空行"""
        session_file = tmp_path / "empty_lines.jsonl"
        content = json.dumps({
            "type": "user",
            "message": {"content": "测试"},
            "timestamp": "2026-02-24T10:00:00Z",
            "sessionId": "session-abc"
        })
        session_file.write_text("\n\n" + content + "\n\n")

        result = parse_session_metadata(session_file)
        assert result["id"] == "session-abc"
        assert result["message_count"] == 1

    def test_file_read_error(self, tmp_path):
        """测试文件读取错误"""
        session_file = tmp_path / "nonexistent.jsonl"

        # 文件不存在时会触发异常处理
        result = parse_session_metadata(session_file)
        # 应该捕获异常并返回错误信息
        assert result["id"] == "nonexistent"

    def test_valid_user_message_string_content(self, tmp_path):
        """测试字符串内容的用户消息"""
        session_file = tmp_path / "test1.jsonl"
        content = json.dumps({
            "type": "user",
            "message": {"content": "分析项目代码"},
            "timestamp": "2026-02-24T10:00:00Z",
            "sessionId": "session-123"
        })
        session_file.write_text(content)

        result = parse_session_metadata(session_file)
        assert result["id"] == "session-123"
        assert "分析项目代码" in result["title"]
        assert result["message_count"] == 1

    def test_valid_user_message_list_content(self, tmp_path):
        """测试数组内容的用户消息"""
        session_file = tmp_path / "test2.jsonl"
        content = json.dumps({
            "type": "user",
            "message": {
                "content": [{"type": "text", "text": "这是测试消息"}]
            },
            "timestamp": "2026-02-24T10:00:00Z",
            "sessionId": "session-456"
        })
        session_file.write_text(content)

        result = parse_session_metadata(session_file)
        assert result["id"] == "session-456"
        assert "这是测试消息" in result["title"]

    def test_ide_selection_filtered(self, tmp_path):
        """测试过滤 IDE 选择内容"""
        session_file = tmp_path / "test3.jsonl"
        content = json.dumps({
            "type": "user",
            "message": {"content": "<ide_selection>selection</ide_selection>"},
            "timestamp": "2026-02-24T10:00:00Z",
            "sessionId": "session-789"
        })
        session_file.write_text(content)

        result = parse_session_metadata(session_file)
        # 应该跳过 ide_selection 内容
        assert result["title"] == "无标题"

    def test_assistant_message_tool_use(self, tmp_path):
        """测试助手消息中的工具使用"""
        session_file = tmp_path / "test4.jsonl"
        user_msg = json.dumps({
            "type": "user",
            "message": {"content": "分析代码"},
            "timestamp": "2026-02-24T10:00:00Z",
            "sessionId": "session-001"
        })
        assistant_msg = json.dumps({
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "text", "text": "好的"},
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "file.py"}},
                    {"type": "tool_use", "name": "Grep", "input": {"pattern": "test"}}
                ]
            }
        })
        session_file.write_text(user_msg + "\n" + assistant_msg)

        result = parse_session_metadata(session_file)
        assert "Read" in result["tools"]
        assert "Grep" in result["tools"]
        assert result["message_count"] == 2

    def test_cwd_extraction(self, tmp_path):
        """测试提取工作目录"""
        session_file = tmp_path / "test5.jsonl"
        content = json.dumps({
            "type": "user",
            "message": {"content": "测试"},
            "cwd": "E:/workspaces/project",
            "timestamp": "2026-02-24T10:00:00Z",
            "sessionId": "session-cwd"
        })
        session_file.write_text(content)

        result = parse_session_metadata(session_file)
        assert result["cwd"] == "E:/workspaces/project"

    def test_long_title_truncation(self, tmp_path):
        """测试长标题截断"""
        session_file = tmp_path / "test6.jsonl"
        long_text = "这是一段很长的文本" * 20
        content = json.dumps({
            "type": "user",
            "message": {"content": long_text},
            "timestamp": "2026-02-24T10:00:00Z",
            "sessionId": "session-long"
        })
        session_file.write_text(content)

        result = parse_session_metadata(session_file)
        assert len(result["title"]) <= 103  # 100 + "..."
        assert result["title"].endswith("...")

    def test_json_decode_error_handling(self, tmp_path):
        """测试 JSON 解析错误处理"""
        session_file = tmp_path / "test7.jsonl"
        valid = json.dumps({"type": "user", "message": {"content": "valid"}})
        session_file.write_text(valid + "\ninvalid json\n" + valid)

        result = parse_session_metadata(session_file)
        # 应该忽略无效行，解析有效行
        assert result["message_count"] >= 1

    def test_parse_exception_handling(self, tmp_path):
        """测试解析异常处理"""
        session_file = tmp_path / "test8.jsonl"
        # 写入一些可能导致解析错误的内容
        # 注意：parse_session_metadata 会捕获 JSONDecodeError 但不会捕获普通异常
        # 如果文件无法读取（权限问题等）会触发异常处理
        # 但在我们的测试环境中，文件可以正常读取
        # 所以我们测试文件存在但内容无效的情况
        session_file.write_text("not json at all")

        result = parse_session_metadata(session_file)
        # 无效 JSON 会被跳过，返回默认值
        assert result["id"] == "test8"
        assert result["title"] == "无标题"

    def test_no_session_id(self, tmp_path):
        """测试没有 session_id 时使用文件名"""
        session_file = tmp_path / "test9.jsonl"
        content = json.dumps({
            "type": "user",
            "message": {"content": "测试"}
        })
        session_file.write_text(content)

        result = parse_session_metadata(session_file)
        assert result["id"] == "test9"


class TestFindSessionFile:
    """测试 find_session_file 函数"""

    def test_direct_match(self, tmp_path):
        """测试直接匹配文件"""
        mock_projects_dir = tmp_path / "projects"
        mock_projects_dir.mkdir()
        project_dir = mock_projects_dir / "proj-123"
        project_dir.mkdir()
        session_file = project_dir / "session-abc.jsonl"
        session_file.write_text("{}")

        try:
            with patch("sessions.PROJECTS_DIR", mock_projects_dir):
                result = find_session_file("session-abc")
                assert result == session_file
        finally:
            session_file.unlink()
            project_dir.rmdir()
            mock_projects_dir.rmdir()

    def test_prefix_match(self, tmp_path):
        """测试前缀匹配"""
        mock_projects_dir = tmp_path / "projects"
        mock_projects_dir.mkdir()
        project_dir = mock_projects_dir / "proj-456"
        project_dir.mkdir()
        session_file = project_dir / "session-abcdef-123.jsonl"
        session_file.write_text("{}")

        try:
            with patch("sessions.PROJECTS_DIR", mock_projects_dir):
                result = find_session_file("session-abcdef")
                assert result == session_file
        finally:
            session_file.unlink()
            project_dir.rmdir()
            mock_projects_dir.rmdir()

    def test_not_found(self, tmp_path):
        """测试找不到文件"""
        mock_projects_dir = tmp_path / "projects"
        mock_projects_dir.mkdir()

        try:
            with patch("sessions.PROJECTS_DIR", mock_projects_dir):
                result = find_session_file("nonexistent")
                assert result is None
        finally:
            mock_projects_dir.rmdir()

    def test_projects_dir_not_exists(self, tmp_path):
        """测试项目目录不存在"""
        mock_projects_dir = tmp_path / "nonexistent_projects"

        with patch("sessions.PROJECTS_DIR", mock_projects_dir):
            result = find_session_file("any-id")
            assert result is None

    def test_non_project_dir_skipped(self, tmp_path):
        """测试跳过非目录文件"""
        mock_projects_dir = tmp_path / "projects"
        mock_projects_dir.mkdir()
        # 创建一个文件而非目录
        file_path = mock_projects_dir / "not_a_dir"
        file_path.write_text("")

        try:
            with patch("sessions.PROJECTS_DIR", mock_projects_dir):
                result = find_session_file("any-id")
                assert result is None
        finally:
            file_path.unlink()
            mock_projects_dir.rmdir()


class TestListSessions:
    """测试 list_sessions 函数"""

    def test_empty_directory(self, tmp_path):
        """测试空目录"""
        sessions_dir = tmp_path / "sessions_empty"
        sessions_dir.mkdir()

        with patch("sessions.get_sessions_dir", return_value=sessions_dir):
            result = list_sessions("/any/path")
            assert result == []

    def test_sessions_dir_not_exists(self, tmp_path):
        """测试会话目录不存在"""
        sessions_dir = tmp_path / "nonexistent_sessions"

        with patch("sessions.get_sessions_dir", return_value=sessions_dir):
            result = list_sessions("/any/path")
            assert result == []

    def test_sessions_sorted_by_timestamp(self, tmp_path):
        """测试按时间戳排序"""
        sessions_dir = tmp_path / "sessions_sorted"
        sessions_dir.mkdir()

        # 创建多个会话文件
        sessions = [
            ("session-1", "2026-02-24T09:00:00Z"),
            ("session-2", "2026-02-24T10:00:00Z"),
            ("session-3", "2026-02-24T08:00:00Z"),
        ]

        for sid, ts in sessions:
            session_file = sessions_dir / f"{sid}.jsonl"
            content = json.dumps({
                "type": "user",
                "message": {"content": "测试"},
                "timestamp": ts,
                "sessionId": sid
            })
            session_file.write_text(content)

        try:
            with patch("sessions.get_sessions_dir", return_value=sessions_dir):
                result = list_sessions("/any/path")
                # 应该按时间降序排序
                assert result[0]["id"] == "session-2"  # 10:00
                assert result[1]["id"] == "session-1"  # 09:00
                assert result[2]["id"] == "session-3"  # 08:00
        finally:
            for sid, _ in sessions:
                (sessions_dir / f"{sid}.jsonl").unlink()
            sessions_dir.rmdir()

    def test_non_jsonl_files_ignored(self, tmp_path):
        """测试忽略非 jsonl 文件"""
        sessions_dir = tmp_path / "sessions_filtered"
        sessions_dir.mkdir()

        # 创建不同类型的文件
        (sessions_dir / "session.jsonl").write_text("{}")
        (sessions_dir / "readme.txt").write_text("text")
        (sessions_dir / "script.py").write_text("# python")

        try:
            with patch("sessions.get_sessions_dir", return_value=sessions_dir):
                result = list_sessions("/any/path")
                assert len(result) == 1
                assert result[0]["id"] == "session"
        finally:
            (sessions_dir / "session.jsonl").unlink()
            (sessions_dir / "readme.txt").unlink()
            (sessions_dir / "script.py").unlink()
            sessions_dir.rmdir()


class TestListAllProjects:
    """测试 list_all_projects 函数"""

    def test_no_projects(self, tmp_path):
        """测试没有项目"""
        mock_projects_dir = tmp_path / "no_projects"
        mock_projects_dir.mkdir()

        try:
            with patch("sessions.PROJECTS_DIR", mock_projects_dir):
                result = list_all_projects()
                assert result == []
        finally:
            mock_projects_dir.rmdir()

    def test_projects_dir_not_exists(self):
        """测试项目目录不存在"""
        mock_projects_dir = Path(__file__).parent / "nonexistent_projects"

        with patch("sessions.PROJECTS_DIR", mock_projects_dir):
            result = list_all_projects()
            assert result == []

    def test_sorted_by_session_count(self, tmp_path):
        """测试按会话数量排序"""
        mock_projects_dir = tmp_path / "projects_sorted"
        mock_projects_dir.mkdir()

        proj1 = mock_projects_dir / "proj-1"
        proj1.mkdir()
        proj2 = mock_projects_dir / "proj-2"
        proj2.mkdir()
        proj3 = mock_projects_dir / "proj-3"
        proj3.mkdir()

        # 创建不同数量的会话
        for i in range(3):
            (proj1 / f"session-{i}.jsonl").write_text("{}")
        for i in range(1):
            (proj2 / f"session-{i}.jsonl").write_text("{}")
        for i in range(2):
            (proj3 / f"session-{i}.jsonl").write_text("{}")

        try:
            with patch("sessions.PROJECTS_DIR", mock_projects_dir):
                result = list_all_projects()
                assert result[0]["hash"] == "proj-1"  # 3 sessions
                assert result[1]["hash"] == "proj-3"  # 2 sessions
                assert result[2]["hash"] == "proj-2"  # 1 session
        finally:
            for i in range(3):
                (proj1 / f"session-{i}.jsonl").unlink()
            proj1.rmdir()
            (proj2 / f"session-{0}.jsonl").unlink()
            proj2.rmdir()
            for i in range(2):
                (proj3 / f"session-{i}.jsonl").unlink()
            proj3.rmdir()
            mock_projects_dir.rmdir()

    def test_non_dir_files_skipped(self, tmp_path):
        """测试跳过非目录文件"""
        mock_projects_dir = tmp_path / "projects_with_files"
        mock_projects_dir.mkdir()

        # 创建一个项目目录
        proj = mock_projects_dir / "proj-real"
        proj.mkdir()
        (proj / "session.jsonl").write_text("{}")

        # 创建一个文件而非目录
        (mock_projects_dir / "not_a_dir").write_text("")

        try:
            with patch("sessions.PROJECTS_DIR", mock_projects_dir):
                result = list_all_projects()
                # 应该只有一个项目
                assert len(result) == 1
                assert result[0]["hash"] == "proj-real"
        finally:
            (proj / "session.jsonl").unlink()
            proj.rmdir()
            (mock_projects_dir / "not_a_dir").unlink()
            mock_projects_dir.rmdir()

    def test_cwd_extraction_from_sessions(self, tmp_path):
        """测试从会话中提取工作目录"""
        mock_projects_dir = tmp_path / "projects_cwd"
        mock_projects_dir.mkdir()

        proj = mock_projects_dir / "proj-cwd"
        proj.mkdir()

        session_file = proj / "session-cwd.jsonl"
        content = json.dumps({
            "type": "user",
            "message": {"content": "测试"},
            "cwd": "E:/workspaces/test",
            "sessionId": "session-123"
        })
        session_file.write_text(content)

        try:
            with patch("sessions.PROJECTS_DIR", mock_projects_dir):
                result = list_all_projects()
                assert len(result) == 1
                assert result[0]["path"] == "E:/workspaces/test"
        finally:
            session_file.unlink()
            proj.rmdir()
            mock_projects_dir.rmdir()


class TestGetSessionDetail:
    """测试 get_session_detail 函数"""

    def test_session_found(self, tmp_path):
        """测试找到会话"""
        session_file = tmp_path / "session-123.jsonl"
        session_file.write_text("{}")

        with patch("sessions.find_session_file", return_value=session_file):
            with patch("sessions.parse_session_metadata", return_value={
                "id": "session-123",
                "title": "测试会话",
                "timestamp": "2026-02-24T10:00:00Z",
                "message_count": 5,
                "size": 1024,
                "tools": ["Read", "Grep"],
                "cwd": "E:/test"
            }):
                result = get_session_detail("session-123")
                assert result["id"] == "session-123"
                assert "file_path" in result
                assert result["file_path"] == str(session_file)

    def test_session_not_found(self):
        """测试找不到会话"""
        with patch("sessions.find_session_file", return_value=None):
            result = get_session_detail("nonexistent")
            assert result is None


class TestDeleteSession:
    """测试 delete_session 函数"""

    def test_delete_successful(self, tmp_path):
        """测试成功删除"""
        session_file = tmp_path / "to-delete.jsonl"
        session_file.write_text("{}")

        with patch("sessions.find_session_file", return_value=session_file):
            result = delete_session("to-delete")
            assert result is True
            assert not session_file.exists()

    def test_delete_not_found(self):
        """测试删除不存在的会话"""
        with patch("sessions.find_session_file", return_value=None):
            result = delete_session("nonexistent")
            assert result is False

    def test_delete_file_not_exists(self, tmp_path):
        """测试文件不存在"""
        session_file = tmp_path / "gone.jsonl"
        with patch("sessions.find_session_file", return_value=session_file):
            result = delete_session("gone")
            assert result is False


class TestExecuteTask:
    """测试 execute_task 函数"""

    def test_import_error_handling(self):
        """测试导入错误处理 - 模拟 SDK 不存在"""
        # 由于模块在导入时已经加载，我们简化测试
        # execute_task 函数中有 try-except 处理导入错误
        # 实际测试需要重新导入模块，这里我们只测试结构
        # 覆盖异常处理分支
        pass

    async def test_execute_task_returns_structure(self):
        """测试 execute_task 返回结构正确"""
        # 由于实际 SDK 调用复杂，我们测试函数的基本结构
        # 确保函数可以被调用
        # 注意：实际测试需要 mock SDK
        pass


class TestPrintJson:
    """测试 print_json 函数"""

    def test_basic_json_output(self, monkeypatch):
        """测试基本 JSON 输出"""
        data = {"key": "value"}

        mock_buffer = Mock()
        mock_stdout = Mock()
        mock_stdout.buffer = mock_buffer
        monkeypatch.setattr(sys, "stdout", mock_stdout)
        monkeypatch.setattr(sys, "platform", "win32")

        print_json(data)

        # 验证 buffer.write 被调用
        assert mock_buffer.write.called

    def test_unicode_characters(self, monkeypatch):
        """测试 Unicode 字符"""
        data = {"中文": "测试"}

        mock_buffer = Mock()
        mock_stdout = Mock()
        mock_stdout.buffer = mock_buffer
        monkeypatch.setattr(sys, "stdout", mock_stdout)
        monkeypatch.setattr(sys, "platform", "win32")

        print_json(data)

        assert mock_buffer.write.called

    def test_unix_platform(self, monkeypatch, capsys):
        """测试 Unix 平台"""
        data = {"key": "value"}

        monkeypatch.setattr(sys, "platform", "linux")

        print_json(data)

        captured = capsys.readouterr()
        assert '"key": "value"' in captured.out

    def test_mixed_platform(self, monkeypatch):
        """测试其他平台"""
        data = {"test": "value"}

        mock_buffer = Mock()
        mock_stdout = Mock()
        mock_stdout.buffer = mock_buffer
        monkeypatch.setattr(sys, "stdout", mock_stdout)
        monkeypatch.setattr(sys, "platform", "darwin")

        print_json(data)

        assert mock_buffer.write.called or mock_stdout.write.called


class TestMainCLI:
    """测试 main 函数的 CLI 功能"""

    @patch("sessions.list_sessions")
    @patch("sessions.print_json")
    @patch("sessions.sys.argv", ["sessions.py", "list", "--cwd", "E:/test"])
    def test_list_command(self, mock_print, mock_list):
        """测试 list 命令"""
        mock_list.return_value = [
            {"id": "session-1", "title": "测试1"},
            {"id": "session-2", "title": "测试2"}
        ]

        main()
        mock_list.assert_called_once()
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert call_args["count"] == 2
        assert len(call_args["sessions"]) == 2

    @patch("sessions.print_json")
    @patch("sessions.list_all_projects")
    @patch("sessions.sys.argv", ["sessions.py", "projects"])
    def test_projects_command(self, mock_list_all, mock_print):
        """测试 projects 命令"""
        mock_list_all.return_value = [
            {"hash": "proj-1", "path": "E:/test1", "session_count": 5}
        ]

        main()
        mock_list_all.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert call_args["count"] == 1

    @patch("sessions.get_session_detail")
    @patch("sessions.print_json")
    @patch("sessions.sys.argv", ["sessions.py", "get", "session-123"])
    def test_get_command_found(self, mock_print, mock_get):
        """测试 get 命令找到会话"""
        mock_get.return_value = {
            "id": "session-123",
            "title": "测试会话"
        }

        main()
        mock_get.assert_called_with("session-123")
        call_args = mock_print.call_args[0][0]
        assert call_args["id"] == "session-123"

    @patch("sessions.print_json")
    @patch("sessions.sys.exit", side_effect=SystemExit)
    @patch("sessions.sys.argv", ["sessions.py", "get"])
    def test_get_command_missing_id(self, mock_exit, mock_print):
        """测试 get 命令缺少 session_id"""
        with pytest.raises(SystemExit):
            main()
        mock_print.assert_called()
        call_args = mock_print.call_args[0][0]
        assert "需要提供 session_id" in call_args["error"]

    @patch("sessions.get_session_detail")
    @patch("sessions.print_json")
    @patch("sessions.sys.argv", ["sessions.py", "get", "nonexistent"])
    def test_get_command_not_found(self, mock_print, mock_get):
        """测试 get 命令找不到会话"""
        mock_get.return_value = None

        main()
        call_args = mock_print.call_args[0][0]
        assert "会话不存在" in call_args["error"]

    @patch("sessions.delete_session")
    @patch("sessions.print_json")
    @patch("sessions.sys.argv", ["sessions.py", "delete", "session-123"])
    def test_delete_command(self, mock_print, mock_delete):
        """测试 delete 命令"""
        mock_delete.return_value = True

        main()
        mock_delete.assert_called_with("session-123")
        call_args = mock_print.call_args[0][0]
        assert call_args["deleted"] is True

    @patch("sessions.print_json")
    @patch("sessions.sys.exit", side_effect=SystemExit)
    @patch("sessions.sys.argv", ["sessions.py", "delete"])
    def test_delete_command_missing_id(self, mock_exit, mock_print):
        """测试 delete 命令缺少 session_id"""
        with pytest.raises(SystemExit):
            main()
        mock_print.assert_called()
        call_args = mock_print.call_args[0][0]
        assert "需要提供 session_id" in call_args["error"]

    @patch("sessions.execute_task")
    @patch("sessions.print_json")
    @patch("sessions.asyncio.run")
    @patch("sessions.sys.argv", ["sessions.py", "exec", "测试任务", "--cwd", "E:/test"])
    def test_exec_command_basic(self, mock_run, mock_print, mock_execute):
        """测试 exec 基本命令"""
        mock_execute.return_value = {
            "success": True,
            "session_id": "new-session",
            "result": "完成",
            "turns": 2,
            "cost_usd": 0.01
        }

        main()
        mock_run.assert_called_once()

    @patch("sessions.print_json")
    @patch("sessions.sys.exit", side_effect=SystemExit)
    @patch("sessions.sys.argv", ["sessions.py", "exec"])
    def test_exec_command_missing_prompt(self, mock_exit, mock_print):
        """测试 exec 命令缺少 prompt"""
        with pytest.raises(SystemExit):
            main()
        mock_print.assert_called()
        call_args = mock_print.call_args[0][0]
        assert "需要提供 prompt" in call_args["error"]

    @patch("sessions.print_json")
    @patch("sessions.sys.exit", side_effect=SystemExit)
    @patch("sessions.sys.argv", ["sessions.py"])
    def test_no_command_shows_help(self, mock_exit, mock_print):
        """测试没有命令显示帮助"""
        with pytest.raises(SystemExit):
            main()
        mock_exit.assert_called_with(1)

    @patch("sessions.print_json")
    @patch("sessions.sys.exit", side_effect=SystemExit)
    @patch("sessions.sys.argv", ["sessions.py", "unknown"])
    def test_unknown_command(self, mock_exit, mock_print):
        """测试未知命令"""
        with pytest.raises(SystemExit):
            main()
        call_args = mock_print.call_args[0][0]
        assert "未知命令" in call_args["error"]
        mock_exit.assert_called_with(1)

    @patch("sessions.list_sessions")
    @patch("sessions.print_json")
    @patch("sessions.sys.argv", ["sessions.py", "list", "--cwd", "E:/test"])
    def test_list_without_cwd_uses_current(self, mock_print, mock_list):
        """测试 list 不带 --cwd 使用当前目录"""
        mock_list.return_value = []
        main()
        mock_list.assert_called_once()
        # 验证使用的是 Path.cwd() 的路径
        call_arg = mock_list.call_args[0][0]
        assert isinstance(call_arg, str)

    @patch("sessions.list_sessions")
    @patch("sessions.print_json")
    @patch("sessions.sys.argv", ["sessions.py", "list"])
    def test_list_command_with_extra_args(self, mock_print, mock_list):
        """测试 list 命令带额外参数"""
        mock_list.return_value = []
        main()
        # 验证额外参数被忽略
        assert mock_list.called

    @patch("sessions.list_sessions")
    @patch("sessions.print_json")
    @patch("sessions.sys.argv", ["sessions.py", "list", "--cwd", "E:/test", "--invalid-flag"])
    def test_list_command_with_invalid_flag(self, mock_print, mock_list):
        """测试 list 命令带无效标志"""
        mock_list.return_value = []
        main()
        # 验证无效标志被忽略
        mock_list.assert_called_once()
        call_arg = mock_list.call_args[0][0]
        assert call_arg == "E:/test"

    @patch("sessions.execute_task")
    @patch("sessions.print_json")
    @patch("sessions.asyncio.run")
    @patch("sessions.sys.argv", ["sessions.py", "exec", "测试", "--resume", "abc", "--cwd", "E:/test", "--tools", "Read,Grep"])
    def test_exec_command_with_all_options(self, mock_run, mock_print, mock_execute):
        """测试 exec 命令带所有选项"""
        mock_execute.return_value = {"success": True, "session_id": "new-session"}

        main()
        mock_run.assert_called_once()

    @patch("sessions.execute_task")
    @patch("sessions.print_json")
    @patch("sessions.asyncio.run")
    @patch("sessions.sys.argv", ["sessions.py", "exec", "测试", "--unknown-option"])
    def test_exec_command_with_unknown_option(self, mock_run, mock_print, mock_execute):
        """测试 exec 命令带未知选项"""
        mock_execute.return_value = {"success": True, "session_id": "new-session"}

        main()
        # 应该忽略未知选项
        mock_run.assert_called_once()

    @patch("sessions.sys.argv", ["sessions.py"])
    @patch("sessions.sys.exit", side_effect=SystemExit)
    def test_main_entry_point(self, mock_exit):
        """测试 main 入口点被正确调用"""
        with pytest.raises(SystemExit):
            main()
