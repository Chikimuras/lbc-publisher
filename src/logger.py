"""Logging configuration using loguru."""

from __future__ import annotations

import sys

from loguru import logger

# Remove default handler
logger.remove()

# Add custom handler with beautiful formatting
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# Add file handler for persistent logs
logger.add(
    "logs/lbc_publisher_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="00:00",  # Rotate at midnight
    retention="30 days",  # Keep logs for 30 days
    compression="zip",  # Compress old logs
)

__all__ = ["logger"]
