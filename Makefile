# Makefile for AgentScribe

.PHONY: install test clean build

install:
	pip install -e . --break-system-packages

install-dev:
	pip install -e ".[dev]" --break-system-packages

test:
	python -m pytest tests/ -v --tb=short

build:
	python -m build

clean:
	rm -rf build/ dist/ *.egg-info/
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

run:
	agentscribe --help

lint:
	python -m flake8 agentscribe/