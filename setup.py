"""AgentScribe - 安装配置"""
from setuptools import setup, find_packages

setup(
    name="agentscribe",
    version="0.1.0",
    description="AI编码代理会话记录与智能分析工具",
    long_description=open("README.md", encoding="utf-8").read() if __import__("os").path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="AgentScribe Team",
    url="https://github.com/gitstq/agentscribe",
    license="MIT",
    packages=find_packages(include=["agentscribe", "agentscribe.*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "jinja2>=3.1.0",
        "matplotlib>=3.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentscribe=agentscribe.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ],
    keywords="ai, developer-tools, cli, productivity, session-recorder, code-analysis",
)