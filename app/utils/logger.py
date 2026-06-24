"""
日志工具模块

提供结构化日志记录功能
"""
import logging
import sys
from pathlib import Path
from typing import Optional

from pythonjsonlogger import jsonlogger


def setup_logger(
    name: str = "payguard",
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    enable_file_logging: bool = True,
) -> logging.Logger:
    """
    设置结构化日志记录器

    Args:
        name: 日志记录器名称
        log_level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        log_dir: 日志文件目录，默认为项目根目录的 logs/
        enable_file_logging: 是否启用文件日志

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # JSON 格式化器
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(funcName)s %(lineno)d %(message)s',
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "funcName": "function",
            "lineno": "line"
        },
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件输出
    if enable_file_logging:
        if log_dir is None:
            from app.config import PROJECT_ROOT
            log_dir = PROJECT_ROOT / "logs"

        log_dir.mkdir(parents=True, exist_ok=True)

        # 常规日志文件
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{name}.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 错误日志文件
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{name}_error.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

    return logger


# 导入 RotatingFileHandler
import logging.handlers

# 全局日志实例
logger = setup_logger()
