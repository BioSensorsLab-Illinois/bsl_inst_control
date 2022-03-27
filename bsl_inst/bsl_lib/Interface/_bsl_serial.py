from xml.dom import NoModificationAllowedErr
from loguru import logger
from .._bsl_inst_info import bsl_inst_info_list

import time
from serial.tools.list_ports import comports
import serial
import re
logger_opt = logger.opt(ansi=True)


@logger_opt.catch
class bsl_serial:
    def __init__(self, target_inst:bsl_inst_info_list , device_sn:str="") -> None:
        logger_opt.info("    Initiating bsl_serial_service...")
        self.device_id=""
        self.inst = target_inst
        self.target_device_sn = device_sn
        self.serial_port = self._connect_serial_device()
        if self.serial_port is None:
            logger_opt.error(f"<light-blue><italic>{self.inst.MODEL} ({self.target_device_sn})</italic></light-blue> not found on serial ports.")
        pass
              
    def __del__(self) -> None:
        self.close()
        return None

    def _connect_serial_device(self) -> serial.Serial:
        if self._find_device():
            logger_opt.success(f"    {self.inst.MODEL} with DEVICE_ID: <light-blue><italic>{self.device_id}</italic></light-blue> found and connected!")
            return serial.Serial(self.serial_port_name, self.baudrate)
        return None

    def _find_device(self) -> serial.tools.list_ports_common.ListPortInfo:
    # Find first available target device by searching Serial COM ports.
    # Return serial port object.

        #Aquire all available Serial COM ports.
        com_ports_list = list(comports())
        target_port = None
        logger_opt.trace(f"    Devices found on bus:{str([port_name[0] for port_name in comports()])}")
        #Search for target device with the name of the USB device.
        for port in com_ports_list:
            temp_port = None
            
            if self.inst.SERIAL_NAME in port[1]:
                logger_opt.debug(f"    Specified device <light-blue><italic>{self.inst.MODEL}</italic></light-blue> with Serial_Name <light-blue><italic>{self.inst.SERIAL_NAME}</italic></light-blue> found on port <light-blue><italic>{port[0]}</italic></light-blue> by Device name search.")
                temp_port = port[0]
            
            if (self.inst.USB_PID in port[2]) or (str(int(self.inst.USB_PID,16)) in port[2]):
                logger_opt.debug(f"    Specified device <light-blue><italic>{self.inst.MODEL}</italic></light-blue> with USB_PID: <light-blue><italic>{self.inst.USB_PID}</italic></light-blue> found on port <light-blue><italic>{port[0]}</italic></light-blue> by USB_PID search.")
                temp_port = port[0]
            
            if temp_port is not None:
                (temp_port, baudrate) = self._check_device_resp(temp_port)
                if temp_port is not None:
                    self.baudrate = baudrate
                    self.serial_port_name = temp_port
                    return True
                continue
        
        logger.warning(f"    No device found based on USB_PID/VID or Serial Name search!")
        
        # Failed to find device with either USB_PID or device name
        # Now try to foreach every signle serial device
        for port in com_ports_list:
            temp_port = None
            (temp_port, baudrate) = self._check_device_resp(port[0])
            if temp_port is not None:
                self.baudrate = baudrate
                self.serial_port_name = temp_port
                return True
        return None
                
    def _check_device_resp(self, temp_port) -> serial.Serial:
        # Set baudrate to common baudrates if not provided
        if self.inst.BAUDRATE != 0:
            baudrates = list([self.inst.BAUDRATE])
        else:
            baudrates = list([4800,9600,19200,28800,38400,115200])

        # Try to communicate with the device with each possible baudrate
        try:
            for baudrate in baudrates:
                logger_opt.debug(f"    Inquiring serial port <light-blue><italic>{temp_port}</italic></light-blue> with Baudrate={baudrate}")
                # Try to open the serial port
                with serial.Serial(temp_port, baudrate, timeout=0.5) as device:
                    logger_opt.trace(f"        Connected to <light-blue><italic>{device.name}</italic></light-blue> on port <light-blue><italic>{temp_port}</italic></light-blue>")
                    # Query the device with QUERY_CMD
                    device.reset_input_buffer()
                    device.write(bytes(self.inst.QUERY_CMD,'ascii'))
                    logger_opt.trace(f"        Querry <light-blue><italic>{repr(self.inst.QUERY_CMD)}</italic></light-blue> sent to <light-blue><italic>{device.name}</italic></light-blue>")
                    time.sleep(0.1)
                    resp = repr(device.read(100).decode("ascii")).strip('\n\r')
                    logger_opt.trace(f"        Response from <light-blue><italic>{device.name}</italic></light-blue>: {resp}")
                    # Check if the response contains expected string and s/n number, if true, port found.
                    if self.inst.QUERY_E_RESP in resp:
                        logger_opt.info(f"        <light-blue><italic>{self.inst.MODEL}</italic></light-blue> found on serial bus on port <light-blue><italic>{temp_port}</italic></light-blue>.")
                        # Check S/N to confirm matching
                        device.reset_input_buffer()
                        device.write(bytes(self.inst.QUERY_SN_CMD,'ascii'))
                        logger_opt.trace(f"        Querry <light-blue><italic>{repr(self.inst.QUERY_SN_CMD)}</italic></light-blue> sent to <light-blue><italic>{device.name}</italic></light-blue>")
                        time.sleep(0.1)
                        resp = (device.read(100).decode("ascii")).strip('\n\r')
                        logger_opt.trace(f"        Response from <light-blue><italic>{device.name}</italic></light-blue>: {resp}")
                        # Use provided regular expression to extract device S/N number
                        device_id = re.search(self.inst.SN_REG, resp).group(0)
                        device.close()
                        # Return device_port and current baudrate if a positive match is confirmed
                        if self.target_device_sn in device_id:
                            self.device_id = device_id.strip('\r\n')
                            return (temp_port, baudrate) 
                        # Able to confirm device model number, but mismatch S/N number
                        logger_opt.warning(f"    S/N Mismatch - Device <light-blue><italic>{temp_port}</italic></light-blue> with S/N <light-blue><italic>{device_id} found, not {self.target_device_sn} as requested, moving to next available device...")
                        break
                    device.close()
        except serial.SerialException:
            logger_opt.warning(f"    BUSY - Device <light-blue><italic>{temp_port}</italic></light-blue> is busy, moving to next available device...")
            return None,None
        return None,None

    def readline(self) -> str:
        resp = self.serial_port.readline().decode("ascii")
        logger_opt.trace(f"        {self.inst.MODEL} - com-Serial - Resp from {self.inst.MODEL} with {repr(resp)}")
        return resp.strip('\n\r')
    
    def read(self, n_bytes:int) -> str:
        resp = self.serial_port.read(n_bytes).decode("ascii")
        logger_opt.trace(f"        {self.inst.MODEL} - com-Serial - Resp from {self.inst.MODEL} with {repr(resp)}")
        return resp.strip('\n\r')

    def write(self, msg:str) -> int:
        logger_opt.trace(f"        {self.inst.MODEL} - com-Serial - Write to {self.inst.MODEL} with {repr(msg)}")
        return self.serial_port.write(bytes(msg, 'ascii'))
    
    def writeline(self, msg:str) -> int:
        msg = msg +'\r\n'
        logger_opt.trace(f"        {self.inst.MODEL} - com-Serial - Write to {self.inst.MODEL} with {repr(msg)}")
        return self.serial_port.write(bytes(msg, 'ascii'))

    def query(self, cmd:str) -> str:
        self.flush_read_buffer()
        self.writeline(cmd)
        return self.readline()
        
    def flush_read_buffer(self) -> None:
        self.serial_port.reset_input_buffer()
        pass

    def close(self) -> None:
        if self.serial_port is not None:
            self.serial_port.close()
        pass
        