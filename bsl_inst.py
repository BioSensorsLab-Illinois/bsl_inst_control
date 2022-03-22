import lib.Instruments._PM100D as _PM100D
import lib.Instruments._M69920 as _M69920
import lib.Instruments._HR4000CG as _HR4000CG
from loguru import logger
import sys

class bsl_instrument:
    __is_logger_ready = False

    @staticmethod
    def init_logger(LOG_LEVEL:str="DEBUG"):
        format_str = "<cyan>{time:MM-DD at HH:mm:ss}</cyan> | <level>{level:7}</level> | {file:15}:{line:4} | <level>{message}</level>"
        logger.remove()
        logger.add(sys.stdout, colorize=True, format=format_str, level=LOG_LEVEL, diagnose=False)
        logger.success(f"Logger initlized.")
        bsl_instrument.__is_logger_ready = True
        return None

    @staticmethod
    def PM100D(device_sn:str=""):
        if not bsl_instrument.__is_logger_ready:
            bsl_instrument.init_logger()
        return _PM100D.PM100D(device_sn)

    @staticmethod
    def M69920(device_sn:str=""):
        if not bsl_instrument.__is_logger_ready:
            bsl_instrument.init_logger()
        return _M69920.M69920(device_sn)

    @staticmethod
    def HR4000CG(device_sn:str=""):
        if not bsl_instrument.__is_logger_ready:
            bsl_instrument.init_logger()
        return _HR4000CG.spec(device_sn)