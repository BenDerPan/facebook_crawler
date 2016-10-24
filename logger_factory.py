import logging
import logging.handlers
import traceback
import sys

DEFAULT_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s[%(lineno)d] - %(message)s"
DEFAULT_LOG_FILE_SIZE = 1024 * 1024
DEFAULT_LOG_FILE_NUM = 5
DEFAULT_LOG_FILE_NAME = "logs/crawler.log"

handler = logging.handlers.RotatingFileHandler(filename=DEFAULT_LOG_FILE_NAME, \
                                               maxBytes=DEFAULT_LOG_FILE_SIZE, \
                                               backupCount=DEFAULT_LOG_FILE_NUM, \
                                               encoding="utf-8", mode="a+")
handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
handler.setLevel(logging.DEBUG)

stdout = logging.StreamHandler(stream=sys.stdout)
stdout.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
stdout.setLevel(logging.DEBUG)

def getLogger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    try:
        logger.addHandler(handler)
        logger.addHandler(stdout)
    except Exception as err:
        traceback.print_exc(file=sys.stderr)
    return logger
