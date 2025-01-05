import sys
import logging

__logger__ = logging.getLogger('logger')
__logger__.propagate = False
__logger__.setLevel(logging.INFO)

__console_handler__ = []

__LOG_LEVEL__ = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

def set_console_handler(level: str):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(__get_log_level(level))
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)8s] %(message)s",
                                           datefmt='%Y-%m-%d %H:%M:%S'))
    try:
        __logger__.addHandler(handler)
        try:
            if len(__console_handler__) ==1 :
                __logger__.removeHandler(__console_handler__.pop())
        except Exception as e:
            __logger__.removeHandler(handler)
    except Exception as e:
        raise e
    __console_handler__.append(handler)

def debug(msg: str, *args, **kwargs):
    __logger__.debug(msg, *args, **kwargs)

def info(msg: str, *args, **kwargs):
    __logger__.info(msg, *args, **kwargs)

def warning(msg: str, *args, **kwargs):
    __logger__.warning(msg, *args, **kwargs)

def error(msg: str, *args, **kwargs):
    __logger__.error(msg, *args, **kwargs)

def critical(msg: str, *args, **kwargs):
    __logger__.critical(msg, *args, **kwargs)

def __get_log_level(level: str) -> int:
    if level.lower() in __LOG_LEVEL__:
        return __LOG_LEVEL__[level.lower()]
