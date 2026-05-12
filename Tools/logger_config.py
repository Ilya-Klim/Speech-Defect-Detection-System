import logging
import os
import sys

from loguru import logger

LOG_FOLDER = "logs"


class InterceptHandler(logging.Handler):
    """
    Интеграция loguru с uvicorn.
    Default handler from examples in loguru documentation.
    """

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    def write(self, message):
        if message.strip():
            logger.info(message.strip())


def setup_logger(log_file=None):
    logger.remove()

    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>|<level>{level}</level>| {message}",
    )

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        logger.add(
            log_file,
            colorize=True,
            format="{time} | {level} | {message}",
            rotation="10 MB",
            retention="10 days",
            compression="zip",
        )


def configure_client_logging(log_folder=LOG_FOLDER):
    setup_logger(os.path.join(log_folder, "client.log"))


def configure_server_logging(log_folder=LOG_FOLDER):
    setup_logger(os.path.join(log_folder, "server.log"))
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logging.basicConfig(
        handlers=[InterceptHandler()], level=logging.INFO
    )
    sys.stderr = InterceptHandler()