#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileZen 安装脚本
"""

from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="filezen",
    version="1.0.0",
    author="gitstq",
    author_email="",
    description="🗂️ 零依赖轻量级智能终端文件管理器 | Zero-dependency Lightweight Intelligent Terminal File Manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/filezen",
    py_modules=["smartfile"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "filezen=smartfile:main",
            "fz=smartfile:main",
        ],
    },
    keywords="file-manager terminal tui cli filesystem file-browser zero-dependency",
    project_urls={
        "Bug Reports": "https://github.com/gitstq/filezen/issues",
        "Source": "https://github.com/gitstq/filezen",
    },
)
