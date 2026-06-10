<div align="center">

# 🗂️ FileZen

**零依赖轻量级智能终端文件管理器**
*Zero-dependency Lightweight Intelligent Terminal File Manager*

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="简体中文"></a>
## 🎉 项目介绍

FileZen 是一款**零依赖、纯Python实现的轻量级智能终端文件管理器**，专为追求效率的开发者与系统管理员设计。在终端环境下，FileZen 提供媲美图形界面的文件浏览体验，同时保持极低的资源占用与极高的响应速度。

### 💡 灵感来源

本项目受到以下优秀开源项目的启发：
- **[yazi](https://github.com/sxyazi/yazi)** - 极速异步文件管理器（Rust），启发我们追求极致性能
- **[nnn](https://github.com/jarun/nnn)** - 极简终端文件浏览器，启发我们保持零依赖理念
- **[Ranger](https://github.com/ranger/ranger)** - Vim风格文件管理器，启发我们设计键盘驱动交互

### ✨ 自研差异化亮点

| 特性 | 传统终端文件管理器 | FileZen |
|------|-------------------|---------|
| 依赖 | 需安装多个第三方库 | ✅ **纯Python零依赖** |
| 兼容性 | Python 3.9+ | ✅ **Python 3.7+ 全兼容** |
| 智能分类 | 仅按扩展名着色 | ✅ **8大类文件智能分类+图标** |
| 文件预览 | 简单文本显示 | ✅ **目录内容统计+文本预览** |
| 跨平台 | 部分功能受限 | ✅ **Linux/macOS/Windows全支持** |
| 启动速度 | 依赖加载慢 | ✅ **毫秒级冷启动** |

---

## ✨ 核心特性

### 🚀 零依赖纯Python核心
- **无需pip install任何包**，单文件即可运行
- 仅使用Python标准库（os, sys, shutil, stat, time等）
- 兼容Python 3.7/3.8/3.9/3.10/3.11/3.12

### 🎨 现代化TUI界面
- 256色ANSI终端色彩支持
- 文件类型彩色高亮（目录黄、可执行绿、代码蓝、媒体粉等）
- 文件类型emoji图标（🐍Python、📝Markdown、🖼️图片等）
- 自适应终端尺寸，支持窄屏与宽屏

### 🤖 智能文件分类
- **8大智能分类**：源代码💻、文档📚、媒体🎭、压缩包📦、数据📊、配置🔧、可执行⚙️、其他📎
- 支持100+文件扩展名自动识别
- 目录内容实时统计与预览

### 📖 实时文件预览
- 文本文件内容预览（支持语法感知）
- 目录内容概览（文件数量、分类统计）
- 符号链接追踪与状态检测
- 大文件智能跳过（>50KB）

### ⌨️ 类Vim快捷键
- 全键盘操作，双手不离开主键区
- hjkl导航、Space选择、/搜索
- 批量复制/剪切/粘贴/删除
- 快速新建文件/目录

### ⚡ 高性能设计
- 毫秒级目录加载
- 流畅的滚动与导航
- 内存占用极低（<10MB）

---

## 🚀 快速开始

### 环境要求

- **Python** 3.7 或更高版本
- **操作系统**: Linux / macOS / Windows
- **终端**: 支持ANSI颜色的终端（推荐：iTerm2、Windows Terminal、GNOME Terminal）

### 安装方式

#### 方式一：单文件直接运行（推荐）

```bash
# 下载单文件
curl -O https://raw.githubusercontent.com/gitstq/filezen/main/smartfile.py

# 直接运行
python3 smartfile.py
```

#### 方式二：通过 pip 安装

```bash
pip install filezen
```

#### 方式三：从源码安装

```bash
git clone https://github.com/gitstq/filezen.git
cd filezen
pip install -e .
```

### 启动命令

```bash
# 基本启动
filezen

# 或简写
fz

# 指定起始目录
filezen /path/to/directory

# 显示版本
filezen --version
```

---

## 📖 详细使用指南

### ⌨️ 快捷键一览

#### 导航操作
| 快捷键 | 功能 |
|--------|------|
| `↑` / `k` | 向上移动 |
| `↓` / `j` | 向下移动 |
| `←` / `h` | 返回上级目录 |
| `→` / `l` / `Enter` | 进入目录/打开文件 |
| `g` | 跳到首项 |
| `G` | 跳到末项 |
| `Ctrl+U` / `PageUp` | 上翻10项 |
| `Ctrl+D` / `PageDown` | 下翻10项 |

#### 选择与搜索
| 快捷键 | 功能 |
|--------|------|
| `Space` | 选择/取消选择当前项 |
| `a` | 全选/取消全选 |
| `/` | 搜索文件（实时过滤） |
| `.` | 切换显示/隐藏隐藏文件 |

#### 排序
| 快捷键 | 功能 |
|--------|------|
| `s` | 切换排序方式（名称→大小→修改时间） |
| `S` | 切换升序/降序 |

#### 文件操作
| 快捷键 | 功能 |
|--------|------|
| `c` | 复制选中项到剪贴板 |
| `x` | 剪切选中项到剪贴板 |
| `p` | 粘贴剪贴板内容 |
| `d` | 删除选中项（需确认） |
| `r` | 重命名当前项 |
| `n` | 新建文件/目录 |
| `o` | 用系统默认程序打开 |

#### 其他
| 快捷键 | 功能 |
|--------|------|
| `q` / `Esc` | 退出 |
| `?` | 显示帮助 |

### 🖥️ 界面说明

```
┌─────────────────────────────────────┬──────────────────┐
│ 📂 /home/user/projects              │  预览             │
│  共12项 | 排序: 名称↑               │  文件信息         │
├─────────────────────────────────────┤                  │
│ 📁 src          <DIR>    2天前      │  名称: README.md │
│ 📄 README.md     2K      刚刚       │  类型: 文件       │
│ 🐍 main.py       5K      1小时前    │  大小: 2K        │
│ ⚙️ build.sh      1K      3天前      │  权限: -rw-r--r--│
│ 📦 dist.tar.gz   15M     1周前      │  修改: 2026-06-10│
│ 📝 docs.md       8K      2天前      │  分类: 📚 文档    │
│                                     │                  │
│                                     │  ─────────────── │
│                                     │  # FileZen       │
│                                     │  零依赖文件管理器 │
│                                     │                  │
└─────────────────────────────────────┴──────────────────┘
 ↑↓移动 Enter进入 Space选择 /搜索 .隐藏 q退出 d删除 ?帮助
```

---

## 💡 设计思路与迭代规划

### 🎯 设计理念

FileZen 的设计遵循三个核心原则：

1. **零依赖优先**：在受限环境（如无网络的服务器、嵌入式设备）中也能直接使用
2. **键盘驱动**：减少鼠标依赖，让文件操作像Vim编辑一样流畅
3. **智能感知**：通过文件扩展名与属性自动分类，降低认知负担

### 🔧 技术选型原因

| 技术决策 | 原因 |
|---------|------|
| 纯Python标准库 | 零安装成本，跨平台一致性 |
| ANSI 256色 | 兼顾兼容性（非True Color终端）与视觉效果 |
| 同步I/O | 文件操作本身受磁盘限制，异步收益有限，同步代码更简洁 |
| 单文件架构 | 便于直接下载使用，降低分发复杂度 |

### 📅 后续迭代计划

- [ ] **v1.1.0** - 添加书签功能（快速跳转常用目录）
- [ ] **v1.2.0** - 添加文件内容搜索（集成ripgrep）
- [ ] **v1.3.0** - 添加批量重命名（正则表达式支持）
- [ ] **v1.4.0** - 添加Git状态集成（显示文件修改状态）
- [ ] **v1.5.0** - 添加可配置主题与键位绑定

### 🤝 社区贡献方向

- 欢迎提交Issue报告bug或建议新功能
- 欢迎提交PR扩展文件类型识别规则
- 欢迎改进多语言文档

---

## 📦 打包与部署指南

### 构建源码分发包

```bash
make build
```

### 本地安装测试

```bash
make install
filezen --version
```

### 运行测试

```bash
make test
```

### 清理构建产物

```bash
make clean
```

---

## 🤝 贡献指南

### 提交Issue

- 使用清晰的标题描述问题
- 提供复现步骤与环境信息（OS、Python版本、终端类型）
- 如可能，附上截图或录屏

### 提交PR

1. Fork本仓库
2. 创建功能分支：`git checkout -b feat/amazing-feature`
3. 提交更改：`git commit -m 'feat: add amazing feature'`
4. 推送分支：`git push origin feat/amazing-feature`
5. 提交Pull Request

### 代码规范

- 遵循PEP 8编码规范
- 所有新功能需附带单元测试
- 保持零依赖原则（标准库 only）

---

## 📄 开源协议说明

本项目采用 [MIT License](LICENSE) 开源协议。

您可以自由使用、修改、分发本软件，只需在副本中包含原始版权声明即可。

---

<a name="繁體中文"></a>
# 繁體中文

## 🎉 專案介紹

FileZen 是一款**零依賴、純Python實現的輕量級智慧終端檔案管理器**，專為追求效率的開發者與系統管理員設計。在終端環境下，FileZen 提供媲美圖形介面的檔案瀏覽體驗，同時保持極低的資源佔用與極高的回應速度。

### ✨ 自研差異化亮點

| 特性 | 傳統終端檔案管理器 | FileZen |
|------|-------------------|---------|
| 依賴 | 需安裝多個第三方庫 | ✅ **純Python零依賴** |
| 相容性 | Python 3.9+ | ✅ **Python 3.7+ 全相容** |
| 智慧分類 | 僅按副檔名著色 | ✅ **8大類檔案智慧分類+圖示** |
| 檔案預覽 | 簡單文字顯示 | ✅ **目錄內容統計+文字預覽** |
| 跨平台 | 部分功能受限 | ✅ **Linux/macOS/Windows全支援** |

### 🚀 快速開始

```bash
# 單檔案直接執行
curl -O https://raw.githubusercontent.com/gitstq/filezen/main/smartfile.py
python3 smartfile.py

# 或透過 pip 安裝
pip install filezen
filezen
```

### ⌨️ 快速鍵一覽

| 快速鍵 | 功能 |
|--------|------|
| `↑` / `k`, `↓` / `j` | 上下移動 |
| `←` / `h`, `→` / `l` | 返回/進入目錄 |
| `Space` | 選擇/取消選擇 |
| `/` | 搜尋檔案 |
| `c` / `x` / `p` | 複製/剪下/貼上 |
| `d` | 刪除（需確認） |
| `q` | 退出 |
| `?` | 顯示說明 |

### 📄 開源協議

本專案採用 [MIT License](LICENSE) 開源協議。

---

<a name="english"></a>
# English

## 🎉 Introduction

FileZen is a **zero-dependency, pure Python lightweight intelligent terminal file manager** designed for developers and system administrators who value efficiency. In terminal environments, FileZen provides a file browsing experience comparable to GUI file managers while maintaining extremely low resource usage and high responsiveness.

### ✨ Differentiation Highlights

| Feature | Traditional Terminal File Managers | FileZen |
|---------|-----------------------------------|---------|
| Dependencies | Multiple third-party libraries required | ✅ **Pure Python, Zero Dependencies** |
| Compatibility | Python 3.9+ | ✅ **Python 3.7+ Fully Compatible** |
| Smart Classification | Extension-only coloring | ✅ **8-Category Smart Classification + Icons** |
| File Preview | Simple text display | ✅ **Directory Stats + Text Preview** |
| Cross-Platform | Limited functionality | ✅ **Full Linux/macOS/Windows Support** |

### 🚀 Quick Start

```bash
# Single-file direct execution
curl -O https://raw.githubusercontent.com/gitstq/filezen/main/smartfile.py
python3 smartfile.py

# Or install via pip
pip install filezen
filezen
```

### ⌨️ Key Bindings

| Key | Action |
|-----|--------|
| `↑` / `k`, `↓` / `j` | Move up/down |
| `←` / `h`, `→` / `l` | Go back/enter directory |
| `Space` | Select/deselect |
| `/` | Search files |
| `c` / `x` / `p` | Copy/cut/paste |
| `d` | Delete (with confirmation) |
| `q` | Quit |
| `?` | Show help |

### 📄 License

This project is licensed under the [MIT License](LICENSE).
