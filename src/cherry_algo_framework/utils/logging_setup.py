import sys
import os
from pathlib import Path
from loguru import logger
from .config_loader import app_config

INITIALIZED_LOGGING = False

def setup_logging():
    global INITIALIZED_LOGGING
    if INITIALIZED_LOGGING:
        return

    logger.remove()

    log_level = app_config.get("Logging", "LOG_LEVEL", "INFO").upper()
    
    log_format_template = app_config.get(
        "Logging", 
        "LOG_FORMAT",
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <7} | {name}.{function}:{line} - {message}"
    )

    project_root_marker = "src" 
    current_path = Path(__file__).resolve()
    project_root = current_path
    while project_root.name != project_root_marker and project_root.parent != project_root:
        project_root = project_root.parent
    project_root = project_root.parent # one level up from 'src'

    log_file_path_str = app_config.get("Logging", "LOG_FILE_PATH", "logs/cherry_algo_framework.log")
    log_file_full_path = project_root / log_file_path_str
    
    try:
        log_file_full_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        sys.stderr.write(f"Warning: Could not create log directory {log_file_full_path.parent}. File logging might fail. Error: {e}\n")


    log_rotation = app_config.get("Logging", "LOG_ROTATION_SIZE", "10 MB")
    log_retention = app_config.get("Logging", "LOG_RETENTION_PERIOD", "7 days")
    log_compression = app_config.get("Logging", "LOG_COMPRESSION_FORMAT", "zip")

    try:
        logger.add(
            sys.stderr,
            level=log_level,
            format=log_format_template,
            colorize=True,
            backtrace=True,
            diagnose=True 
        )

        logger.add(
            log_file_full_path,
            level=log_level,
            format=log_format_template,
            rotation=log_rotation,
            retention=log_retention,
            compression=log_compression,
            enqueue=True,
            backtrace=True,
            diagnose=True,
            encoding="utf-8"
        )
        INITIALIZED_LOGGING = True
        logger.info(f"Logging initialized. Level: {log_level}. Outputting to console and file: {log_file_full_path}")
    
    except Exception as e:
        sys.stderr.write(f"Critical error during logging setup: {e}\n")
        sys.stderr.write("Logging to file might not be available. Basic console logging will be used.\n")
        logger.add(sys.stderr, level="INFO", format=log_format_template, colorize=True) # Fallback to console
        INITIALIZED_LOGGING = True  

if not INITIALIZED_LOGGING and __name__ != "__main__":
    setup_logging()

if __name__ == '__main__':
    setup_logging()
    logger.debug("This is a debug message from logging_setup.")
    logger.info("This is an info message from logging_setup.")
    logger.warning("This is a warning from logging_setup.")
    logger.error("This is an error from logging_setup.")
    logger.critical("This is a critical message from logging_setup.")
    
    try:
        result = 10 / 0
    except ZeroDivisionError:
        logger.exception("A ZeroDivisionError occurred!")
    
    logger.info(f"Log file should be at: {app_config.get('Logging', 'LOG_FILE_PATH', 'logs/cherry_algo_framework.log')}")
