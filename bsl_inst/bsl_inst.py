from .bsl_lib.Instruments import _PM100D
from .bsl_lib.Instruments import _HR4000CG
from .bsl_lib.Instruments import _M69920
from .bsl_lib.Instruments import _RS_7_1

from loguru import logger
import sys


__is_logger_ready = False

@staticmethod
def init_logger(LOG_LEVEL:str="DEBUG"):
    global __is_logger_ready
    format_str = "<cyan>{time:MM-DD at HH:mm:ss}</cyan> | <level>{level:7}</level> | {file:15}:{line:4} | <level>{message}</level>"
    logger.remove()
    logger.add(sys.stdout, colorize=True, format=format_str, level=LOG_LEVEL, diagnose=False)
    logger.success(f"Logger initlized with LOG_LEVEL = \"{LOG_LEVEL}\".")
    __is_logger_ready = True
    return None

@staticmethod
def PM100D(device_sn:str="") -> _PM100D.PM100D:
    if not __is_logger_ready:
        init_logger()
    return _PM100D.PM100D(device_sn)

@staticmethod
def M69920(device_sn:str="") -> _M69920.M69920:
    if not __is_logger_ready:
        init_logger()
    return _M69920.M69920(device_sn)

@staticmethod
def HR4000CG(device_sn:str="") -> _HR4000CG.HR4000CG:
    if not __is_logger_ready:
        init_logger()
    return _HR4000CG.HR4000CG(device_sn)

@staticmethod
def RS_7_1(device_sn:str="") -> _RS_7_1.RS_7_1:
    if not __is_logger_ready:
        init_logger()
    return _RS_7_1.RS_7_1(device_sn)