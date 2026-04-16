"""
Logging utilities for ECS management.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    name: str = "ecs",
    verbose: bool = False,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Configure logging with console and optional file output.
    
    Args:
        name: Logger name
        verbose: Enable verbose (DEBUG) output
        log_file: Optional log file path (defaults to {name}.log in script directory)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    # File handler (if log_file provided)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

    # Formatters
    console_format = logging.Formatter("%(message)s")
    file_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    if log_file:
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger
