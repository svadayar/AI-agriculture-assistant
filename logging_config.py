"""
logging_config.py
Centralized logging configuration for the app.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# Read DEBUG level from environment
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO

# Create logger
logger = logging.getLogger("agri_assistant")
logger.setLevel(LOG_LEVEL)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)

# File handler (rotate every 5MB, keep 3 backups)
os.makedirs("logs", exist_ok=True)
file_handler = RotatingFileHandler(
    "logs/agri_assistant.log",
    maxBytes=5 * 1024 * 1024,  # 5MB
    backupCount=3
)
file_handler.setLevel(LOG_LEVEL)

# Formatter
formatter = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    return logging.getLogger(f"agri_assistant.{name}")
