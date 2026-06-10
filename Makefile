.PHONY: help install uninstall test clean lint build run

PYTHON ?= python3
PIP ?= pip3

help:
	@echo "FileZen 构建工具"
	@echo ""
	@echo "可用命令:"
	@echo "  make install     安装到当前Python环境"
	@echo "  make uninstall   卸载"
	@echo "  make test        运行测试"
	@echo "  make lint        代码检查"
	@echo "  make build       构建分发包"
	@echo "  make run         直接运行"
	@echo "  make clean       清理构建产物"

install:
	$(PIP) install -e .

uninstall:
	$(PIP) uninstall -y filezen

test:
	$(PYTHON) -m pytest tests/ -v || $(PYTHON) tests/test_smartfile.py

lint:
	$(PYTHON) -m py_compile smartfile.py
	@echo "✅ 语法检查通过"

build: clean
	$(PYTHON) setup.py sdist bdist_wheel

run:
	$(PYTHON) smartfile.py

clean:
	rm -rf build/ dist/ *.egg-info __pycache__ .pytest_cache
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -delete
