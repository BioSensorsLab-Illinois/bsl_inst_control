from loguru import logger
from ._bsl_inst_list import bsl_instrument_list
import re
try:
    import pyvisa as pyvisa
except ImportError:
    pass
logger = logger.opt(ansi=True)

@logger.catch
class bsl_visa:
    class CustomError(Exception):
        pass
    class DeviceConnectionFailed(CustomError):
        pass
    
    def __init__(self, target_inst:bsl_instrument_list, device_sn:str="") -> None:
        #Init logger by inherit from parent process or using a new one if no parent logger
        logger.info("    Initiating bsl_visa_service...")
        self.visa_resource_manager = pyvisa.ResourceManager()

        self.inst = target_inst
        self.target_device_sn = device_sn
        self._connect_visa_device()
        if self.com_port is None:
            logger.error(f"<light-blue><italic>{self.inst.MODEL} ({self.target_device_sn})</italic></light-blue> not found on VISA/SCPI ports.")
        pass

    def _find_device_vpid(self) -> None:
        resource_list = self.visa_resource_manager.list_resources()
        logger.debug(f"    bsl_VISA - Currently opened devices: {repr(self.visa_resource_manager.list_opened_resources())}")
        for port in resource_list:
            logger.debug(f"    Found bus device <light-blue><italic>{port}</italic></light-blue>")
            if port in str(self.visa_resource_manager.list_opened_resources()):
                logger.warning(f"    BUSY - Device <light-blue><italic>{port}</italic></light-blue> is busy, moving to next available device...")
                continue
            if (self.inst.USB_PID in port) and (self.inst.USB_VID in port):
                logger.debug(f"    {self.inst.MODEL} is found with USB_PID/VID search.")
                temp_com_port = self.visa_resource_manager.open_resource(port)
                device_id = re.search(self.inst.SN_REG, temp_com_port.query(self.inst.QUERY_CMD).strip()).group(0)
                if self.target_device_sn not in device_id:
                    temp_com_port.close()
                    logger.warning(f"    S/N Mismatch - Device <light-blue><italic>{port}</italic></light-blue> with S/N <light-blue><italic>{device_id}</italic></light-blue> found, not <light-blue><italic>{self.target_device_sn}</italic></light-blue> as requested, moving to next available device...")
                    continue
                temp_com_port.close()
                return port
            if ( str(int(self.inst.USB_PID,16)) in port and str(int(self.inst.USB_VID,16)) in port):
                logger.debug(f"    {self.inst.MODEL} is found with USB_PID/VID search.")
                temp_com_port = self.visa_resource_manager.open_resource(port)
                device_id = re.search(self.inst.SN_REG, temp_com_port.query(self.inst.QUERY_CMD).strip()).group(0)
                if self.target_device_sn not in device_id:
                    temp_com_port.close()
                    logger.warning(f"    S/N Mismatch - Device <light-blue><italic>{port}</italic></light-blue> with S/N <light-blue><italic>{device_id}</italic></light-blue> found, not <light-blue><italic>{self.target_device_sn}</italic></light-blue> as requested, moving to next available device...")
                    continue
                temp_com_port.close()
                return port
        return None

    def _connect_visa_device(self) -> None:
        port = self._find_device_vpid()
        self.com_port = None
        if port is not None:
            self.com_port = self.visa_resource_manager.open_resource(port)
        if self.com_port is not None:
            self.device_id = self.query(self.inst.QUERY_CMD).strip()
            if self.inst.QUERY_E_RESP not in self.device_id:
                logger.error(f"    FAILED - Wrong device identifier (E_RESP) is returned!")
                raise self.DeviceConnectionFailed
            self.device_id = re.search(self.inst.SN_REG, self.device_id).group(0)
            logger.success(f"    {self.inst.MODEL} with DEVICE_ID: <light-blue><italic>{self.device_id}</italic></light-blue> found and connected!")
        pass

    def query(self, cmd:str):
        logger.trace(f"        {self.inst.MODEL} - com-VISA - Query to {self.inst.MODEL} with {cmd}")
        resp = self.com_port.query(cmd)
        logger.trace(f"        {self.inst.MODEL} - com-VISA - Resp from {self.inst.MODEL} with {repr(resp)}")
        return resp
    
    def write(self, cmd:str) -> None:
        logger.trace(f"        {self.inst.MODEL} - com-VISA - Write to {self.inst.MODEL} with {cmd}")
        self.com_port.write(cmd)
        pass

    def set_timeout_ms(self, timeout:int) -> None:
        self.com_port.timeout = timeout
        pass

    def terminate(self) -> None:
        self.com_port.close()
        pass


        