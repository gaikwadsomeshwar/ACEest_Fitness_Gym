"""
Logging configuration module for ACEest Fitness Gym application.

Sets up structured logging with file and console handlers.
Logs include application events, database operations, and errors.
"""

import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(log_dir="logs", log_level=logging.INFO):
    """
    Configure application logging with file and console handlers.

    Args:
        log_dir (str): Directory for log files. Defaults to 'logs'.
        log_level (int): Logging level. Defaults to logging.INFO.

    Returns:
        logging.Logger: Configured root logger.
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create logger
    logger = logging.getLogger("aceest")
    logger.setLevel(log_level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Log format
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler - general log
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    # File handler - error log
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "error.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    logger.addHandler(error_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    logger.info(f"Logging initialized at {datetime.now()}")
    return logger


# Initialize logger at module import
logger = setup_logging()
