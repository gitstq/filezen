#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileZen 单元测试
"""

import os
import sys
import tempfile
import shutil
import unittest

# 添加上级目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smartfile import (
    Terminal,
    Theme,
    FileInfo,
    SmartClassifier,
    PreviewEngine,
    SmartFileTUI,
)


class TestTerminal(unittest.TestCase):
    """测试终端控制类"""

    def test_color_generation(self):
        """测试颜色码生成"""
        reset = Terminal.color(reset=True)
        self.assertIn("0m", reset)

        bold = Terminal.color(bold=True)
        self.assertIn("1", bold)

        fg = Terminal.color(fg=31)
        self.assertIn("31", fg)

    def test_size_returns_tuple(self):
        """测试终端尺寸获取"""
        size = Terminal.size()
        self.assertIsInstance(size, tuple)
        self.assertEqual(len(size), 2)
        self.assertIsInstance(size[0], int)
        self.assertIsInstance(size[1], int)
        self.assertGreater(size[0], 0)
        self.assertGreater(size[1], 0)


class TestTheme(unittest.TestCase):
    """测试主题类"""

    def test_file_color_directory(self):
        """测试目录颜色"""
        color = Theme.get_file_color("test", is_dir=True)
        self.assertEqual(color, Theme.FILE_COLORS["dir"])

    def test_file_color_executable(self):
        """测试可执行文件颜色"""
        color = Theme.get_file_color("script.sh", is_exe=True)
        self.assertEqual(color, Theme.FILE_COLORS["exe"])

    def test_file_color_hidden(self):
        """测试隐藏文件颜色"""
        color = Theme.get_file_color(".hidden", is_hidden=True)
        self.assertEqual(color, Theme.FILE_COLORS["hidden"])

    def test_file_color_by_extension(self):
        """测试根据扩展名获取颜色"""
        color = Theme.get_file_color("test.py")
        self.assertEqual(color, Theme.FILE_COLORS["code"])

        color = Theme.get_file_color("readme.md")
        self.assertEqual(color, Theme.FILE_COLORS["doc"])

        color = Theme.get_file_color("image.png")
        self.assertEqual(color, Theme.FILE_COLORS["media"])

    def test_colored_output(self):
        """测试带颜色文本"""
        text = Theme.colored("hello", 31, bold=True)
        self.assertIn("hello", text)
        self.assertIn("\x1b[", text)


class TestFileInfo(unittest.TestCase):
    """测试文件信息类"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.testfile = os.path.join(self.tmpdir, "test.txt")
        with open(self.testfile, "w") as f:
            f.write("hello world")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_file_info_basic(self):
        """测试文件基本信息"""
        fi = FileInfo(self.testfile, "test.txt", self.tmpdir)
        self.assertEqual(fi.name, "test.txt")
        self.assertTrue(fi.is_file)
        self.assertFalse(fi.is_dir)
        self.assertEqual(fi.size, 11)

    def test_size_human(self):
        """测试人类可读大小"""
        fi = FileInfo(self.testfile, "test.txt", self.tmpdir)
        self.assertEqual(fi.size_human(), "11B")

    def test_mode_str(self):
        """测试权限字符串"""
        fi = FileInfo(self.testfile, "test.txt", self.tmpdir)
        mode = fi.mode_str()
        self.assertEqual(len(mode), 10)
        self.assertEqual(mode[0], "-")  # 普通文件

    def test_icon(self):
        """测试文件图标"""
        fi = FileInfo(self.testfile, "test.txt", self.tmpdir)
        self.assertEqual(fi.icon(), "📄")

        py_file = os.path.join(self.tmpdir, "test.py")
        with open(py_file, "w") as f:
            f.write("print()")
        fi_py = FileInfo(py_file, "test.py", self.tmpdir)
        self.assertEqual(fi_py.icon(), "🐍")


class TestSmartClassifier(unittest.TestCase):
    """测试智能分类器"""

    def test_classify_directory(self):
        """测试目录分类"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fi = FileInfo(tmpdir, os.path.basename(tmpdir), os.path.dirname(tmpdir))
            cat, info = SmartClassifier.classify(fi)
            self.assertEqual(cat, "directory")

    def test_classify_code(self):
        """测试代码文件分类"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.py")
            with open(path, "w") as f:
                f.write("pass")
            fi = FileInfo(path, "test.py", tmpdir)
            cat, info = SmartClassifier.classify(fi)
            self.assertEqual(cat, "source")
            self.assertEqual(info["icon"], "💻")

    def test_classify_document(self):
        """测试文档分类"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "readme.md")
            with open(path, "w") as f:
                f.write("# Test")
            fi = FileInfo(path, "readme.md", tmpdir)
            cat, info = SmartClassifier.classify(fi)
            self.assertEqual(cat, "document")

    def test_classify_directory_stats(self):
        """测试目录统计"""
        with tempfile.TemporaryDirectory() as tmpdir:
            files = []
            # 创建各类文件
            for name in ["a.py", "b.md", "c.jpg"]:
                path = os.path.join(tmpdir, name)
                with open(path, "w") as f:
                    f.write("x")
                files.append(FileInfo(path, name, tmpdir))

            stats = SmartClassifier.classify_directory(files)
            self.assertEqual(stats["source"], 1)
            self.assertEqual(stats["document"], 1)
            self.assertEqual(stats["media"], 1)


class TestPreviewEngine(unittest.TestCase):
    """测试预览引擎"""

    def test_preview_text_file(self):
        """测试文本文件预览"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.txt")
            with open(path, "w") as f:
                f.write("line1\nline2\nline3")
            fi = FileInfo(path, "test.txt", tmpdir)
            lines = PreviewEngine.preview(fi, 40, 20)
            self.assertTrue(len(lines) > 0)
            self.assertIn("line1", lines[0])

    def test_preview_directory(self):
        """测试目录预览"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建子文件
            with open(os.path.join(tmpdir, "a.txt"), "w") as f:
                f.write("x")
            fi = FileInfo(tmpdir, os.path.basename(tmpdir), os.path.dirname(tmpdir))
            lines = PreviewEngine.preview(fi, 40, 20)
            self.assertTrue(len(lines) > 0)
            self.assertIn("目录", lines[0])

    def test_preview_large_file(self):
        """测试大文件预览"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "large.bin")
            with open(path, "wb") as f:
                f.write(b"x" * (PreviewEngine.MAX_PREVIEW_SIZE + 1000))
            fi = FileInfo(path, "large.bin", tmpdir)
            lines = PreviewEngine.preview(fi, 40, 20)
            self.assertTrue(len(lines) > 0)
            self.assertIn("过大", lines[0])


class TestSmartFileTUI(unittest.TestCase):
    """测试主控制器"""

    def test_init(self):
        """测试初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = SmartFileTUI(tmpdir)
            self.assertEqual(app.path, os.path.abspath(tmpdir))
            self.assertEqual(app.cursor, 0)
            self.assertFalse(app.show_hidden)

    def test_load_files(self):
        """测试加载文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文件
            with open(os.path.join(tmpdir, "a.txt"), "w") as f:
                f.write("a")
            with open(os.path.join(tmpdir, "b.txt"), "w") as f:
                f.write("b")

            app = SmartFileTUI(tmpdir)
            app.load_files()
            self.assertEqual(len(app.files), 2)

    def test_hidden_files_toggle(self):
        """测试隐藏文件切换"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, ".hidden"), "w") as f:
                f.write("x")
            with open(os.path.join(tmpdir, "visible"), "w") as f:
                f.write("x")

            app = SmartFileTUI(tmpdir)
            app.load_files()
            self.assertEqual(len(app.files), 1)  # 不显示隐藏文件

            app.show_hidden = True
            app.load_files()
            self.assertEqual(len(app.files), 2)  # 显示隐藏文件

    def test_sort_by_name(self):
        """测试按名称排序"""
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ["c.txt", "a.txt", "b.txt"]:
                with open(os.path.join(tmpdir, name), "w") as f:
                    f.write("x")

            app = SmartFileTUI(tmpdir)
            app.load_files()
            names = [f.name for f in app.files]
            self.assertEqual(names, ["a.txt", "b.txt", "c.txt"])

    def test_sort_by_size(self):
        """测试按大小排序"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "small.txt"), "w") as f:
                f.write("x")
            with open(os.path.join(tmpdir, "large.txt"), "w") as f:
                f.write("x" * 1000)

            app = SmartFileTUI(tmpdir)
            app.sort_by = "size"
            app.load_files()
            self.assertEqual(app.files[0].name, "small.txt")
            self.assertEqual(app.files[1].name, "large.txt")

    def test_message(self):
        """测试消息设置"""
        import time
        app = SmartFileTUI(".")
        app.set_message("test message")
        self.assertEqual(app.message, "test message")
        self.assertTrue(app.message_time > time.time())


if __name__ == "__main__":
    unittest.main(verbosity=2)
