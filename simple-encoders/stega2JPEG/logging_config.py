import logging
import sys

_date = "%y-%m-%d"
_time = "%H:%M:%S"
_dt_verb = "%Y-%m-%d %H:%M:%S"
_dt_spam = "%y%m%d_%H%M%S"

_log_spam = "{levelname:.4} {module:>8}:{funcName:.12}:{lineno:<3}\t | {message:.100}"
_log_verb = "{asctime} [{levelname:.4}] {module:>8}:{funcName:.10}:{lineno:<3}\t | {message}"

def get_file_handler():
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(logging.DEBUG)
    # file_handler.setFormatter(logging.Formatter(_log, _dt_spam))
    file_handler.setFormatter(logging.Formatter(_log_verb, _dt_spam, style="{"))
    return file_handler

def get_stdout_handler():
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(logging.Formatter(_log_spam, style="{"))
    return stdout_handler

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stdout_handler())
    return logger