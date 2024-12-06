import logging
import os
from app.config.config import Config

cfg = Config()

def get_logger(name="app"):
    log_level = getattr(logging, cfg.get("logging.level").upper(), logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # StreamHandler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_format)

    # FileHandler
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logs')
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
    file_handler.setLevel(log_level)
    file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
