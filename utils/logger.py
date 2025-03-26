import logging
from config import config


def setup_logger():
    logger = logging.getLogger("blogforge")
    level = config.LOG_LEVEL
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(config.LOG_FORMAT)

    # Create console handler and set level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # Add console handler to logger
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()
