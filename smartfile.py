#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileZen 🗂️
零依赖轻量级智能终端文件管理器 | Zero-dependency Lightweight Intelligent Terminal File Manager
纯Python核心 | Pure Python Core | Python 3.7+

核心特性:
- 纯Python实现，零第三方依赖
- 类Vim快捷键导航
- 智能文件分类高亮
- 实时文件预览
- 批量操作支持
- 跨平台兼容 (Linux/macOS/Windows)
"""

import os
import sys
import shutil
import stat
import time
import subprocess
import fnmatch
from pathlib import Path

# ---------------------------------------------------------------------------
# 平台检测与终端控制
# ---------------------------------------------------------------------------
IS_WINDOWS = sys.platform.startswith("win")
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")


class Terminal:
    """跨平台终端控制"""

    ESC = "\x1b["

    @classmethod
    def clear(cls):
        sys.stdout.write(cls.ESC + "2J" + cls.ESC + "H")
        sys.stdout.flush()

    @classmethod
    def hide_cursor(cls):
        sys.stdout.write(cls.ESC + "?25l")
        sys.stdout.flush()

    @classmethod
    def show_cursor(cls):
        sys.stdout.write(cls.ESC + "?25h")
        sys.stdout.flush()

    @classmethod
    def move(cls, row, col=1):
        sys.stdout.write(cls.ESC + f"{row};{col}H")
        sys.stdout.flush()

    @classmethod
    def size(cls):
        """获取终端尺寸 (rows, cols)"""
        try:
            if IS_WINDOWS:
                import ctypes
                h = ctypes.windll.kernel32.GetStdHandle(-11)
                csbi = ctypes.create_string_buffer(22)
                res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
                if res:
                    import struct
                    (_, _, _, _, _, left, top, right, bottom, _, _) = struct.unpack(
                        "hhhhHhhhhhh", csbi.raw
                    )
                    return (bottom - top + 1, right - left + 1)
            else:
                import fcntl, termios, struct
                th, tw, _, _ = struct.unpack(
                    "HHHH", fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0))
                )
                return (th, tw)
        except Exception:
            pass
        return (24, 80)

    @classmethod
    def color(cls, fg=None, bg=None, bold=False, dim=False, underline=False, reset=False):
        """生成ANSI颜色码"""
        if reset:
            return cls.ESC + "0m"
        codes = []
        if bold:
            codes.append("1")
        if dim:
            codes.append("2")
        if underline:
            codes.append("4")
        if fg is not None:
            if fg < 8:
                codes.append(str(30 + fg))
            else:
                codes.append(f"38;5;{fg}")
        if bg is not None:
            if bg < 8:
                codes.append(str(40 + bg))
            else:
                codes.append(f"48;5;{bg}")
        return cls.ESC + ";".join(codes) + "m" if codes else ""

    @classmethod
    def write(cls, text):
        sys.stdout.write(text)
        sys.stdout.flush()

    @classmethod
    def writeln(cls, text=""):
        sys.stdout.write(text + "\n")
        sys.stdout.flush()

    @classmethod
    def read_key(cls):
        """读取单个按键（跨平台）"""
        if IS_WINDOWS:
            import msvcrt
            ch = msvcrt.getch()
            if ch == b"\x00" or ch == b"\xe0":
                ch = msvcrt.getch()
                keymap = {
                    b"H": "UP", b"P": "DOWN", b"K": "LEFT", b"M": "RIGHT",
                    b"S": "DELETE", b"G": "HOME", b"O": "END",
                    b"I": "PAGEUP", b"Q": "PAGEDOWN",
                }
                return keymap.get(ch, f"UNKNOWN-{ch}")
            if ch == b"\x03":
                return "CTRL_C"
            if ch == b"\r":
                return "ENTER"
            if ch == b"\x08":
                return "BACKSPACE"
            if ch == b"\x1b":
                return "ESC"
            if ch == b"\t":
                return "TAB"
            try:
                return ch.decode("utf-8")
            except Exception:
                return "UNKNOWN"
        else:
            import tty, termios
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == "\x1b":
                    seq = sys.stdin.read(2)
                    if seq == "[A":
                        return "UP"
                    if seq == "[B":
                        return "DOWN"
                    if seq == "[C":
                        return "RIGHT"
                    if seq == "[D":
                        return "LEFT"
                    if seq == "[3~":
                        return "DELETE"
                    if seq == "[H":
                        return "HOME"
                    if seq == "[F":
                        return "END"
                    if seq == "[5~":
                        return "PAGEUP"
                    if seq == "[6~":
                        return "PAGEDOWN"
                    if seq == "[1;5A":
                        return "CTRL_UP"
                    if seq == "[1;5B":
                        return "CTRL_DOWN"
                    if seq.startswith("["):
                        extra = ""
                        while seq and seq[-1] not in "ABCDEFGH~":
                            extra_c = sys.stdin.read(1)
                            if not extra_c:
                                break
                            seq += extra_c
                        return f"ESC-{seq}"
                    return "ESC"
                if ch == "\x03":
                    return "CTRL_C"
                if ch == "\x04":
                    return "CTRL_D"
                if ch == "\r" or ch == "\n":
                    return "ENTER"
                if ch == "\x7f":
                    return "BACKSPACE"
                if ch == "\t":
                    return "TAB"
                if ch == "\x00":
                    return "CTRL_SPACE"
                if ord(ch) < 32:
                    return f"CTRL_{chr(ord(ch) + 64)}"
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ---------------------------------------------------------------------------
# 颜色主题
# ---------------------------------------------------------------------------
class Theme:
    """终端颜色主题"""

    # ANSI 256色
    RESET = Terminal.color(reset=True)
    BOLD = Terminal.color(bold=True)
    DIM = Terminal.color(dim=True)
    UNDERLINE = Terminal.color(underline=True)

    # 文件类型颜色映射
    FILE_COLORS = {
        "dir": 33,      # 黄色 - 目录
        "exe": 82,      # 亮绿 - 可执行文件
        "link": 51,     # 青色 - 符号链接
        "hidden": 245,  # 灰色 - 隐藏文件
        "code": 81,     # 天蓝 - 代码文件
        "doc": 223,     # 暖黄 - 文档
        "media": 213,   # 粉色 - 媒体
        "archive": 208, # 橙色 - 压缩包
        "data": 156,    # 浅绿 - 数据
        "config": 229,  # 浅黄 - 配置
        "default": 252, # 浅灰 - 默认
    }

    # 扩展名映射
    EXT_MAP = {
        "code": [
            ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp",
            ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala", ".r", ".m", ".mm",
            ".cs", ".vb", ".fs", ".fsx", ".erl", ".ex", ".exs", ".clj", ".cljs",
            ".lua", ".pl", ".pm", ".t", ".sh", ".bash", ".zsh", ".fish", ".ps1",
            ".sql", ".html", ".htm", ".css", ".scss", ".sass", ".less", ".xml", ".json",
            ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".cmake", ".make", ".mk",
        ],
        "doc": [
            ".md", ".markdown", ".rst", ".txt", ".rtf", ".pdf", ".doc", ".docx",
            ".odt", ".epub", ".mobi", ".tex", ".org",
        ],
        "media": [
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico", ".webp", ".avif",
            ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma",
            ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v",
        ],
        "archive": [
            ".zip", ".tar", ".gz", ".tgz", ".bz2", ".tbz2", ".xz", ".txz", ".7z",
            ".rar", ".cab", ".iso", ".dmg", ".deb", ".rpm", ".pkg", ".msi", ".apk",
        ],
        "data": [
            ".csv", ".tsv", ".xls", ".xlsx", ".ods", ".db", ".sqlite", ".sqlite3",
            ".parquet", ".feather", ".h5", ".hdf5", ".pickle", ".pkl", ".npy", ".npz",
        ],
        "config": [
            ".gitignore", ".gitattributes", ".editorconfig", ".dockerignore",
            ".env", ".envrc", ".nvmrc", ".python-version", ".ruby-version",
            ".babelrc", ".eslintrc", ".prettierrc", ".stylelintrc",
            ".npmrc", ".yarnrc", ".piprc", ".condarc",
        ],
    }

    @classmethod
    def get_file_color(cls, name, is_dir=False, is_link=False, is_exe=False, is_hidden=False):
        """根据文件属性返回颜色码"""
        if is_dir:
            return cls.FILE_COLORS["dir"]
        if is_link:
            return cls.FILE_COLORS["link"]
        if is_exe:
            return cls.FILE_COLORS["exe"]
        if is_hidden:
            return cls.FILE_COLORS["hidden"]

        ext = os.path.splitext(name)[1].lower()
        basename = name.lower()

        for ftype, exts in cls.EXT_MAP.items():
            if ext in exts or basename in exts:
                return cls.FILE_COLORS.get(ftype, cls.FILE_COLORS["default"])

        return cls.FILE_COLORS["default"]

    @classmethod
    def colored(cls, text, color_code, bold=False):
        return Terminal.color(fg=color_code, bold=bold) + text + cls.RESET


# ---------------------------------------------------------------------------
# 文件信息
# ---------------------------------------------------------------------------
class FileInfo:
    """文件/目录信息封装"""

    SIZE_UNITS = ["B", "K", "M", "G", "T", "P"]

    def __init__(self, path, name, parent):
        self.path = path
        self.name = name
        self.parent = parent
        self.fullpath = os.path.join(parent, name)
        self._stat = None
        self._lstat = None

    def _get_stat(self):
        if self._stat is None:
            try:
                self._stat = os.stat(self.fullpath)
            except OSError:
                self._stat = None
        return self._stat

    def _get_lstat(self):
        if self._lstat is None:
            try:
                self._lstat = os.lstat(self.fullpath)
            except OSError:
                self._lstat = None
        return self._lstat

    @property
    def is_dir(self):
        st = self._get_lstat()
        return st is not None and stat.S_ISDIR(st.st_mode)

    @property
    def is_file(self):
        st = self._get_lstat()
        return st is not None and stat.S_ISREG(st.st_mode)

    @property
    def is_link(self):
        st = self._get_lstat()
        return st is not None and stat.S_ISLNK(st.st_mode)

    @property
    def is_exe(self):
        st = self._get_lstat()
        if st is None:
            return False
        return stat.S_ISREG(st.st_mode) and (st.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))

    @property
    def is_hidden(self):
        return self.name.startswith(".")

    @property
    def size(self):
        st = self._get_stat()
        return st.st_size if st else 0

    @property
    def mtime(self):
        st = self._get_stat()
        return st.st_mtime if st else 0

    @property
    def mode(self):
        st = self._get_lstat()
        return st.st_mode if st else 0

    def size_human(self):
        size = self.size
        if size == 0:
            return "0B"
        idx = 0
        while size >= 1024 and idx < len(self.SIZE_UNITS) - 1:
            size /= 1024.0
            idx += 1
        if idx == 0:
            return f"{int(size)}B"
        return f"{size:.1f}{self.SIZE_UNITS[idx]}"

    def mtime_str(self):
        mt = self.mtime
        if mt == 0:
            return "?"
        now = time.time()
        diff = now - mt
        if diff < 60:
            return "刚刚"
        if diff < 3600:
            return f"{int(diff / 60)}分钟前"
        if diff < 86400:
            return f"{int(diff / 3600)}小时前"
        if diff < 604800:
            return f"{int(diff / 86400)}天前"
        return time.strftime("%Y-%m-%d", time.localtime(mt))

    def mode_str(self):
        st = self._get_lstat()
        if st is None:
            return "?????????"
        m = st.st_mode
        perms = ""
        perms += "d" if stat.S_ISDIR(m) else "-"
        perms += "l" if stat.S_ISLNK(m) else ("d" if stat.S_ISDIR(m) else "-")
        # 简化权限显示
        perms = ""
        perms += "d" if stat.S_ISDIR(m) else ("l" if stat.S_ISLNK(m) else "-")
        perms += "r" if m & stat.S_IRUSR else "-"
        perms += "w" if m & stat.S_IWUSR else "-"
        perms += "x" if m & stat.S_IXUSR else "-"
        perms += "r" if m & stat.S_IRGRP else "-"
        perms += "w" if m & stat.S_IWGRP else "-"
        perms += "x" if m & stat.S_IXGRP else "-"
        perms += "r" if m & stat.S_IROTH else "-"
        perms += "w" if m & stat.S_IWOTH else "-"
        perms += "x" if m & stat.S_IXOTH else "-"
        return perms

    def icon(self):
        """返回文件类型图标"""
        if self.is_dir:
            return "📁"
        if self.is_link:
            return "🔗"
        if self.is_exe:
            return "⚙️"
        ext = os.path.splitext(self.name)[1].lower()
        icon_map = {
            ".py": "🐍", ".js": "📜", ".ts": "📘", ".html": "🌐", ".css": "🎨",
            ".md": "📝", ".txt": "📄", ".pdf": "📕", ".zip": "🗜️", ".tar": "🗜️",
            ".jpg": "🖼️", ".png": "🖼️", ".gif": "🖼️", ".mp3": "🎵", ".mp4": "🎬",
            ".json": "📋", ".yaml": "⚙️", ".yml": "⚙️", ".xml": "📰", ".sql": "🗃️",
            ".c": "🔧", ".cpp": "🔧", ".h": "🔧", ".go": "🔵", ".rs": "🦀",
            ".java": "☕", ".rb": "💎", ".php": "🐘", ".sh": "🔲", ".ps1": "🔲",
        }
        return icon_map.get(ext, "📄")

    def color_code(self):
        return Theme.get_file_color(
            self.name, self.is_dir, self.is_link, self.is_exe, self.is_hidden
        )


# ---------------------------------------------------------------------------
# 智能文件分类器
# ---------------------------------------------------------------------------
class SmartClassifier:
    """基于规则的文件智能分类器"""

    CATEGORIES = {
        "source": {"name": "源代码", "exts": Theme.EXT_MAP["code"], "icon": "💻"},
        "document": {"name": "文档", "exts": Theme.EXT_MAP["doc"], "icon": "📚"},
        "media": {"name": "媒体", "exts": Theme.EXT_MAP["media"], "icon": "🎭"},
        "archive": {"name": "压缩包", "exts": Theme.EXT_MAP["archive"], "icon": "📦"},
        "data": {"name": "数据", "exts": Theme.EXT_MAP["data"], "icon": "📊"},
        "config": {"name": "配置", "exts": Theme.EXT_MAP["config"], "icon": "🔧"},
        "executable": {"name": "可执行", "exts": [], "icon": "⚙️"},
        "other": {"name": "其他", "exts": [], "icon": "📎"},
    }

    @classmethod
    def classify(cls, file_info):
        """分类单个文件"""
        if file_info.is_dir:
            return "directory", {"name": "目录", "icon": "📁"}
        if file_info.is_link:
            return "link", {"name": "链接", "icon": "🔗"}
        if file_info.is_exe:
            return "executable", cls.CATEGORIES["executable"]

        ext = os.path.splitext(file_info.name)[1].lower()
        basename = file_info.name.lower()

        for cat, info in cls.CATEGORIES.items():
            if ext in info["exts"] or basename in info["exts"]:
                return cat, info

        return "other", cls.CATEGORIES["other"]

    @classmethod
    def classify_directory(cls, files):
        """统计目录中各类文件数量"""
        stats = {cat: 0 for cat in list(cls.CATEGORIES.keys()) + ["directory", "link"]}
        for f in files:
            cat, _ = cls.classify(f)
            stats[cat] = stats.get(cat, 0) + 1
        return stats


# ---------------------------------------------------------------------------
# 文件预览引擎
# ---------------------------------------------------------------------------
class PreviewEngine:
    """文件内容预览引擎"""

    MAX_PREVIEW_SIZE = 50 * 1024  # 50KB
    MAX_LINES = 100

    @classmethod
    def preview(cls, file_info, max_width, max_height):
        """生成文件预览内容"""
        if file_info.is_dir:
            return cls._preview_dir(file_info, max_width, max_height)
        if file_info.is_link:
            return cls._preview_link(file_info, max_width)

        path = file_info.fullpath
        size = file_info.size

        if size == 0:
            return ["(空文件)"]
        if size > cls.MAX_PREVIEW_SIZE:
            return [f"(文件过大: {file_info.size_human()}, 无法预览)"]

        ext = os.path.splitext(file_info.name)[1].lower()

        # 二进制文件
        if ext in Theme.EXT_MAP["media"] + Theme.EXT_MAP["archive"]:
            return [f"(二进制文件: {file_info.size_human()})"]

        # 文本文件预览
        return cls._preview_text(path, max_width, max_height)

    @classmethod
    def _preview_dir(cls, file_info, max_width, max_height):
        """预览目录内容"""
        try:
            entries = os.listdir(file_info.fullpath)
            lines = [f"📁 目录: {file_info.name} ({len(entries)} 项)"]
            lines.append("-" * min(max_width - 2, 40))

            # 分类统计
            files = []
            for e in entries[:50]:  # 最多显示50项
                fp = os.path.join(file_info.fullpath, e)
                try:
                    files.append(FileInfo(fp, e, file_info.fullpath))
                except Exception:
                    pass

            stats = SmartClassifier.classify_directory(files)
            for cat, count in stats.items():
                if count > 0:
                    lines.append(f"  {SmartClassifier.CATEGORIES.get(cat, {}).get('icon', '📄')} {cat}: {count}")

            lines.append("-" * min(max_width - 2, 40))
            for f in sorted(files, key=lambda x: (not x.is_dir, x.name.lower()))[:max_height - len(lines) - 1]:
                icon = f.icon()
                name = f.name[:max_width - 8]
                lines.append(f"  {icon} {name}")

            return lines
        except PermissionError:
            return ["(无权限访问此目录)"]
        except Exception as e:
            return [f"(读取错误: {e})"]

    @classmethod
    def _preview_link(cls, file_info, max_width):
        """预览符号链接"""
        try:
            target = os.readlink(file_info.fullpath)
            lines = [f"🔗 符号链接: {file_info.name}"]
            lines.append(f"   指向: {target}")
            if os.path.exists(file_info.fullpath):
                lines.append("   状态: ✅ 有效")
            else:
                lines.append("   状态: ❌ 失效")
            return lines
        except Exception as e:
            return [f"(读取链接错误: {e})"]

    @classmethod
    def _preview_text(cls, path, max_width, max_height):
        """预览文本文件"""
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= cls.MAX_LINES or len(lines) >= max_height - 2:
                        lines.append(f"... ({i}+ 行)")
                        break
                    line = line.rstrip("\n\r")
                    if len(line) > max_width - 4:
                        line = line[: max_width - 7] + "..."
                    lines.append(line)
                return lines
        except Exception as e:
            return [f"(读取错误: {e})"]


# ---------------------------------------------------------------------------
# 主文件管理器
# ---------------------------------------------------------------------------
class SmartFileTUI:
    """FileZen 主控制器"""

    def __init__(self, start_path=None):
        self.path = os.path.abspath(start_path or os.getcwd())
        self.files = []
        self.cursor = 0
        self.scroll_top = 0
        self.selected = set()
        self.show_hidden = False
        self.sort_by = "name"  # name, size, mtime
        self.sort_reverse = False
        self.search_query = ""
        self.search_mode = False
        self.message = ""
        self.message_time = 0
        self.clipboard = []
        self.clipboard_action = None  # copy, cut
        self.rows, self.cols = Terminal.size()

    def set_message(self, msg, duration=3):
        self.message = msg
        self.message_time = time.time() + duration

    def load_files(self):
        """加载当前目录文件列表"""
        try:
            entries = os.listdir(self.path)
        except PermissionError:
            self.files = []
            self.set_message("❌ 无权限访问此目录")
            return
        except Exception as e:
            self.files = []
            self.set_message(f"❌ 错误: {e}")
            return

        self.files = []
        for e in entries:
            if not self.show_hidden and e.startswith("."):
                continue
            fp = os.path.join(self.path, e)
            try:
                self.files.append(FileInfo(fp, e, self.path))
            except Exception:
                pass

        # 排序
        sort_key = {
            "name": lambda f: (not f.is_dir, f.name.lower()),
            "size": lambda f: f.size,
            "mtime": lambda f: f.mtime,
        }.get(self.sort_by, lambda f: f.name.lower())

        self.files.sort(key=sort_key, reverse=self.sort_reverse)

        # 搜索过滤
        if self.search_query:
            self.files = [f for f in self.files if self.search_query.lower() in f.name.lower()]

        # 确保光标有效
        if self.files:
            self.cursor = max(0, min(self.cursor, len(self.files) - 1))
        else:
            self.cursor = 0

    def draw(self):
        """绘制TUI界面"""
        Terminal.clear()
        self.rows, self.cols = Terminal.size()

        if self.rows < 10 or self.cols < 40:
            Terminal.writeln("终端尺寸过小，请调整窗口大小")
            return

        # 计算布局
        header_height = 2
        footer_height = 2
        list_height = self.rows - header_height - footer_height
        preview_width = min(40, self.cols // 3) if self.cols >= 80 else 0
        list_width = self.cols - preview_width - 1

        # 绘制头部
        self._draw_header(list_width, preview_width)

        # 绘制文件列表
        self._draw_file_list(list_width, list_height, header_height)

        # 绘制预览
        if preview_width > 0:
            self._draw_preview(preview_width, list_height, header_height, list_width + 1)

        # 绘制底部
        self._draw_footer(self.cols, self.rows - 1)

    def _draw_header(self, list_width, preview_width):
        """绘制头部信息栏"""
        # 路径栏
        path_display = self.path
        if len(path_display) > list_width - 4:
            path_display = "..." + path_display[-(list_width - 7):]

        header = f" 📂 {path_display}"
        padding = list_width - len(header) - 1
        if padding > 0:
            header += " " * padding

        Terminal.write(Terminal.color(bg=24, fg=252) + header[:list_width] + Theme.RESET)

        # 信息栏
        info = f" 共{len(self.files)}项"
        if self.search_query:
            info += f" | 搜索: {self.search_query}"
        if self.selected:
            info += f" | 已选{len(self.selected)}项"

        sort_icon = "↓" if self.sort_reverse else "↑"
        sort_name = {"name": "名称", "size": "大小", "mtime": "修改时间"}.get(self.sort_by, "名称")
        info += f" | 排序: {sort_name}{sort_icon}"

        if self.show_hidden:
            info += " | 显示隐藏"

        padding = list_width - len(info) - 1
        if padding > 0:
            info += " " * padding

        Terminal.write(Terminal.color(bg=235, fg=245) + info[:list_width] + Theme.RESET)

        # 预览头部
        if preview_width > 0:
            preview_header = " 预览 "
            padding = preview_width - len(preview_header) - 1
            if padding > 0:
                preview_header += " " * padding
            Terminal.move(1, list_width + 2)
            Terminal.write(Terminal.color(bg=24, fg=252) + preview_header[:preview_width] + Theme.RESET)

            preview_sub = " 文件信息 "
            padding = preview_width - len(preview_sub) - 1
            if padding > 0:
                preview_sub += " " * padding
            Terminal.move(2, list_width + 2)
            Terminal.write(Terminal.color(bg=235, fg=245) + preview_sub[:preview_width] + Theme.RESET)

    def _draw_file_list(self, width, height, start_row):
        """绘制文件列表"""
        if not self.files:
            Terminal.move(start_row + 1, 2)
            Terminal.write(Theme.DIM + "(空目录)" + Theme.RESET)
            return

        # 滚动调整
        if self.cursor < self.scroll_top:
            self.scroll_top = self.cursor
        elif self.cursor >= self.scroll_top + height:
            self.scroll_top = self.cursor - height + 1

        visible = self.files[self.scroll_top : self.scroll_top + height]

        for i, f in enumerate(visible):
            row = start_row + i + 1
            idx = self.scroll_top + i
            is_cursor = idx == self.cursor
            is_selected = idx in self.selected

            # 构建行内容
            icon = f.icon()
            name = f.name
            max_name_len = width - 18
            if len(name) > max_name_len:
                name = name[: max_name_len - 2] + ".."

            size_str = f.size_human() if f.is_file else "<DIR>"
            time_str = f.mtime_str()

            line = f" {icon} {name:<{max_name_len}} {size_str:>6} {time_str:>8}"

            # 截断到宽度
            if len(line) > width - 1:
                line = line[: width - 2]

            padding = width - len(line) - 1
            if padding > 0:
                line += " " * padding

            # 颜色
            color = f.color_code()
            if is_cursor and is_selected:
                bg = 24
                fg = 226
            elif is_cursor:
                bg = 24
                fg = color
            elif is_selected:
                bg = 236
                fg = color
            else:
                bg = None
                fg = color

            Terminal.move(row, 1)
            if bg is not None:
                Terminal.write(Terminal.color(bg=bg, fg=fg, bold=is_cursor) + line[:width] + Theme.RESET)
            else:
                Terminal.write(Terminal.color(fg=fg) + line[:width] + Theme.RESET)

    def _draw_preview(self, width, height, start_row, start_col):
        """绘制文件预览面板"""
        if not self.files or self.cursor >= len(self.files):
            return

        f = self.files[self.cursor]

        # 文件信息
        info_lines = [
            f" 名称: {f.name[:width-8]}",
            f" 类型: {'目录' if f.is_dir else ('链接' if f.is_link else '文件')}",
            f" 大小: {f.size_human()}",
            f" 权限: {f.mode_str()}",
            f" 修改: {time.strftime('%Y-%m-%d %H:%M', time.localtime(f.mtime)) if f.mtime else '?'}",
        ]

        # 智能分类
        cat, cat_info = SmartClassifier.classify(f)
        info_lines.append(f" 分类: {cat_info['icon']} {cat_info['name']}")

        # 预览内容
        preview_lines = PreviewEngine.preview(f, width - 2, height - len(info_lines) - 3)

        # 绘制分隔线
        for i in range(height):
            Terminal.move(start_row + i + 1, start_col)
            Terminal.write(Terminal.color(fg=240) + "│" + Theme.RESET)

        # 绘制信息
        for i, line in enumerate(info_lines):
            if i >= height:
                break
            Terminal.move(start_row + i + 1, start_col + 1)
            truncated = line[:width - 1]
            padding = width - len(truncated) - 1
            if padding > 0:
                truncated += " " * padding
            Terminal.write(truncated[:width])

        # 绘制预览内容
        sep_row = start_row + len(info_lines) + 1
        if sep_row < start_row + height:
            Terminal.move(sep_row, start_col + 1)
            sep = "─" * (width - 1)
            Terminal.write(Terminal.color(fg=240) + sep + Theme.RESET)

        for i, line in enumerate(preview_lines):
            row = sep_row + 1 + i
            if row >= start_row + height:
                break
            Terminal.move(row, start_col + 1)
            truncated = line[:width - 1]
            padding = width - len(truncated) - 1
            if padding > 0:
                truncated += " " * padding
            Terminal.write(truncated[:width])

    def _draw_footer(self, width, row):
        """绘制底部状态栏"""
        # 消息或快捷键提示
        if self.message and time.time() < self.message_time:
            msg = f" {self.message}"
        elif self.search_mode:
            msg = f" 搜索: {self.search_query}_"
        else:
            msg = " ↑↓移动 Enter进入 Space选择 /搜索 .隐藏 q退出 d删除 r重命名 c复制 x剪切 p粘贴"

        padding = width - len(msg) - 1
        if padding > 0:
            msg += " " * padding

        Terminal.move(row, 1)
        Terminal.write(Terminal.color(bg=235, fg=252) + msg[:width] + Theme.RESET)

    def run(self):
        """主事件循环"""
        self.load_files()
        Terminal.hide_cursor()

        try:
            while True:
                self.draw()
                key = Terminal.read_key()

                if self.search_mode:
                    self._handle_search(key)
                else:
                    self._handle_normal(key)

        except KeyboardInterrupt:
            pass
        finally:
            Terminal.show_cursor()
            Terminal.clear()

    def _handle_search(self, key):
        """搜索模式按键处理"""
        if key == "ESC" or key == "ENTER":
            self.search_mode = False
            self.load_files()
        elif key == "BACKSPACE":
            self.search_query = self.search_query[:-1]
            self.load_files()
        elif key == "CTRL_C":
            self.search_mode = False
            self.search_query = ""
            self.load_files()
        elif len(key) == 1 and key.isprintable():
            self.search_query += key
            self.load_files()

    def _handle_normal(self, key):
        """普通模式按键处理"""
        if key == "q" or key == "Q" or key == "CTRL_C":
            raise KeyboardInterrupt

        elif key == "UP" or key == "k":
            if self.cursor > 0:
                self.cursor -= 1

        elif key == "DOWN" or key == "j":
            if self.cursor < len(self.files) - 1:
                self.cursor += 1

        elif key == "HOME" or key == "g":
            self.cursor = 0

        elif key == "END" or key == "G":
            self.cursor = max(0, len(self.files) - 1)

        elif key == "PAGEUP" or key == "CTRL_U":
            self.cursor = max(0, self.cursor - 10)

        elif key == "PAGEDOWN" or key == "CTRL_D":
            self.cursor = min(len(self.files) - 1, self.cursor + 10)

        elif key == "ENTER" or key == "l" or key == "RIGHT":
            if self.files and self.cursor < len(self.files):
                f = self.files[self.cursor]
                if f.is_dir:
                    try:
                        os.chdir(f.fullpath)
                        self.path = os.getcwd()
                        self.cursor = 0
                        self.scroll_top = 0
                        self.load_files()
                    except Exception as e:
                        self.set_message(f"❌ 无法进入: {e}")
                elif f.is_link and os.path.isdir(f.fullpath):
                    try:
                        os.chdir(f.fullpath)
                        self.path = os.getcwd()
                        self.cursor = 0
                        self.scroll_top = 0
                        self.load_files()
                    except Exception as e:
                        self.set_message(f"❌ 无法进入: {e}")

        elif key == "h" or key == "LEFT" or key == "BACKSPACE":
            parent = os.path.dirname(self.path)
            if parent != self.path:
                try:
                    os.chdir(parent)
                    self.path = os.getcwd()
                    self.cursor = 0
                    self.scroll_top = 0
                    self.load_files()
                except Exception as e:
                    self.set_message(f"❌ 无法返回: {e}")

        elif key == " ":
            if self.files and self.cursor < len(self.files):
                if self.cursor in self.selected:
                    self.selected.discard(self.cursor)
                else:
                    self.selected.add(self.cursor)
                self.cursor = min(self.cursor + 1, len(self.files) - 1)

        elif key == "a" and not self.search_mode:
            # 全选/取消全选
            if len(self.selected) == len(self.files):
                self.selected.clear()
            else:
                self.selected = set(range(len(self.files)))

        elif key == "/":
            self.search_mode = True
            self.search_query = ""

        elif key == ".":
            self.show_hidden = not self.show_hidden
            self.cursor = 0
            self.load_files()
            self.set_message("👁️ 已" + ("显示" if self.show_hidden else "隐藏") + "隐藏文件")

        elif key == "s":
            # 切换排序
            sorts = ["name", "size", "mtime"]
            idx = sorts.index(self.sort_by)
            self.sort_by = sorts[(idx + 1) % len(sorts)]
            self.load_files()
            self.set_message(f"📊 按{ {'name':'名称','size':'大小','mtime':'修改时间'}[self.sort_by] }排序")

        elif key == "S":
            self.sort_reverse = not self.sort_reverse
            self.load_files()
            self.set_message(f"📊 {'降序' if self.sort_reverse else '升序'}排列")

        elif key == "c":
            self._copy_selected()

        elif key == "x":
            self._cut_selected()

        elif key == "p":
            self._paste()

        elif key == "d":
            self._delete_selected()

        elif key == "r":
            self._rename_selected()

        elif key == "n":
            self._create_new()

        elif key == "o":
            self._open_with_default()

        elif key == "?":
            self._show_help()

    def _copy_selected(self):
        """复制选中文件到剪贴板"""
        if not self.selected and self.files:
            self.selected = {self.cursor}

        self.clipboard = []
        for idx in sorted(self.selected):
            if idx < len(self.files):
                self.clipboard.append(self.files[idx].fullpath)
        self.clipboard_action = "copy"
        self.set_message(f"📋 已复制 {len(self.clipboard)} 项")
        self.selected.clear()

    def _cut_selected(self):
        """剪切选中文件到剪贴板"""
        if not self.selected and self.files:
            self.selected = {self.cursor}

        self.clipboard = []
        for idx in sorted(self.selected):
            if idx < len(self.files):
                self.clipboard.append(self.files[idx].fullpath)
        self.clipboard_action = "cut"
        self.set_message(f"✂️ 已剪切 {len(self.clipboard)} 项")
        self.selected.clear()

    def _paste(self):
        """粘贴剪贴板内容"""
        if not self.clipboard:
            self.set_message("📋 剪贴板为空")
            return

        success = 0
        errors = []
        for src in self.clipboard:
            basename = os.path.basename(src)
            dst = os.path.join(self.path, basename)

            # 处理重名
            counter = 1
            orig_dst = dst
            while os.path.exists(dst):
                name, ext = os.path.splitext(orig_dst)
                dst = f"{name} ({counter}){ext}"
                counter += 1

            try:
                if self.clipboard_action == "copy":
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                else:  # cut
                    shutil.move(src, dst)
                success += 1
            except Exception as e:
                errors.append(f"{basename}: {e}")

        if self.clipboard_action == "cut":
            self.clipboard = []
            self.clipboard_action = None

        self.load_files()
        if errors:
            self.set_message(f"⚠️ 成功{success}项, 失败{len(errors)}项")
        else:
            self.set_message(f"✅ 成功粘贴 {success} 项")

    def _delete_selected(self):
        """删除选中文件"""
        if not self.selected and self.files:
            self.selected = {self.cursor}

        targets = [self.files[i].fullpath for i in sorted(self.selected) if i < len(self.files)]
        if not targets:
            return

        self.set_message(f"⚠️ 确认删除 {len(targets)} 项? [y/N]")
        self.draw()

        confirm = Terminal.read_key()
        if confirm.lower() == "y":
            success = 0
            errors = []
            for path in targets:
                try:
                    if os.path.isdir(path) and not os.path.islink(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    success += 1
                except Exception as e:
                    errors.append(f"{os.path.basename(path)}: {e}")

            self.selected.clear()
            self.load_files()
            if errors:
                self.set_message(f"⚠️ 删除{success}项, 失败{len(errors)}项")
            else:
                self.set_message(f"🗑️ 已删除 {success} 项")
        else:
            self.set_message("❎ 已取消删除")
            self.selected.clear()

    def _rename_selected(self):
        """重命名选中文件"""
        if not self.files or self.cursor >= len(self.files):
            return

        f = self.files[self.cursor]
        self.set_message(f"重命名 '{f.name}' 为: ")
        self.draw()

        # 简单输入
        new_name = ""
        while True:
            self.set_message(f"重命名 '{f.name}' 为: {new_name}_")
            self.draw()
            key = Terminal.read_key()
            if key == "ENTER":
                break
            elif key == "ESC" or key == "CTRL_C":
                self.set_message("❎ 已取消重命名")
                return
            elif key == "BACKSPACE":
                new_name = new_name[:-1]
            elif len(key) == 1 and key.isprintable():
                new_name += key

        if new_name and new_name != f.name:
            new_path = os.path.join(self.path, new_name)
            try:
                os.rename(f.fullpath, new_path)
                self.load_files()
                self.set_message(f"✅ 已重命名为 '{new_name}'")
            except Exception as e:
                self.set_message(f"❌ 重命名失败: {e}")

    def _create_new(self):
        """创建新文件或目录"""
        self.set_message("[f]文件 [d]目录 [c]取消")
        self.draw()
        key = Terminal.read_key()

        if key == "c" or key == "ESC":
            self.set_message("❎ 已取消")
            return

        is_dir = key == "d"
        type_name = "目录" if is_dir else "文件"

        self.set_message(f"新建{type_name}名: ")
        self.draw()

        name = ""
        while True:
            self.set_message(f"新建{type_name}名: {name}_")
            self.draw()
            k = Terminal.read_key()
            if k == "ENTER":
                break
            elif k == "ESC" or k == "CTRL_C":
                self.set_message("❎ 已取消")
                return
            elif k == "BACKSPACE":
                name = name[:-1]
            elif len(k) == 1 and k.isprintable():
                name += k

        if name:
            new_path = os.path.join(self.path, name)
            try:
                if is_dir:
                    os.makedirs(new_path, exist_ok=False)
                else:
                    with open(new_path, "w") as f:
                        pass
                self.load_files()
                self.set_message(f"✅ 已创建{type_name} '{name}'")
            except Exception as e:
                self.set_message(f"❌ 创建失败: {e}")

    def _open_with_default(self):
        """使用系统默认程序打开文件"""
        if not self.files or self.cursor >= len(self.files):
            return

        f = self.files[self.cursor]
        try:
            if IS_WINDOWS:
                os.startfile(f.fullpath)
            elif IS_MACOS:
                subprocess.Popen(["open", f.fullpath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(["xdg-open", f.fullpath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.set_message(f"🚀 已打开 '{f.name}'")
        except Exception as e:
            self.set_message(f"❌ 打开失败: {e}")

    def _show_help(self):
        """显示帮助信息"""
        help_text = [
            "",
            " 🗂️  FileZen 快捷键帮助",
            "",
            " 导航:",
            "   ↑/k, ↓/j     上下移动",
            "   ←/h, →/l     返回/进入目录",
            "   g, G         跳到首项/末项",
            "   Ctrl+U/D     上翻/下翻10项",
            "",
            " 操作:",
            "   Space        选择/取消选择",
            "   a            全选/取消全选",
            "   /            搜索文件",
            "   .            切换显示隐藏文件",
            "   s            切换排序方式",
            "   S            切换升序/降序",
            "",
            " 文件操作:",
            "   c            复制选中项",
            "   x            剪切选中项",
            "   p            粘贴",
            "   d            删除选中项",
            "   r            重命名",
            "   n            新建文件/目录",
            "   o            用默认程序打开",
            "",
            " 其他:",
            "   q, Esc       退出",
            "   ?            显示此帮助",
            "",
            " 按任意键返回...",
        ]

        Terminal.clear()
        for line in help_text:
            Terminal.writeln(line)

        Terminal.read_key()


# ---------------------------------------------------------------------------
# 入口点
# ---------------------------------------------------------------------------
def main():
    """程序入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="🗂️ FileZen - 零依赖轻量级智能终端文件管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python smartfile.py              # 在当前目录启动
  python smartfile.py /home/user   # 在指定目录启动
  python smartfile.py --version    # 显示版本

快捷键:
  ↑↓/jk 移动  Enter/l 进入  h/← 返回  Space 选择  / 搜索
  . 隐藏文件  s 排序  c 复制  x 剪切  p 粘贴  d 删除  q 退出
        """,
    )
    parser.add_argument("path", nargs="?", default=".", help="起始目录路径 (默认: 当前目录)")
    parser.add_argument("--version", action="store_true", help="显示版本信息")

    args = parser.parse_args()

    if args.version:
        print("FileZen v1.0.0")
        print("零依赖轻量级智能终端文件管理器 | Zero-dependency Lightweight Intelligent Terminal File Manager")
        print("MIT License | https://github.com/gitstq/filezen")
        sys.exit(0)

    start_path = os.path.abspath(args.path)
    if not os.path.isdir(start_path):
        print(f"错误: '{start_path}' 不是有效的目录", file=sys.stderr)
        sys.exit(1)

    app = SmartFileTUI(start_path)
    app.run()


if __name__ == "__main__":
    main()
