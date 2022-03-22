from loguru import logger
import time
from .. import _bsl_visa as bsl_visa
from .. import _bsl_inst_list as inst

logger = logger.opt(ansi=True)

@logger.catch
class PM100D:
    class CustomError(Exception):
        pass
    class DeviceOperationError(CustomError):
        pass
    class DeviceInconsistentError(CustomError):
        pass

    def __init__(self, device_sn:str="") -> None:
        logger.info(f"Initiating bsl_instrument - PM100D({device_sn})...")

        if self._com_connect(device_sn):
            self.run_update_power_meter()
            logger.success(f"READY - Thorlab PM100D Power Meter \"{self.device_id}\" with sensor \"{self.sensor_id}\".\n\n")
        else:
            logger.error(f"FAILED to connect to Thorlab PM100D ({device_sn}) Power Meter!\n\n")
            raise bsl_visa.DeviceConnectionFailed
        pass

    def _com_connect(self, device_sn:str) -> bool:
        self.com = bsl_visa(inst.PM100D, device_sn)
        if self.com.com_port is None:
            return False
        self.device_id = self.com.device_id
        return True

    def close(self) -> None:
        self.com.terminate()
        pass

    def run_update_power_meter(self) -> None:
        self.get_preset_wavelength()
        self.get_attenuation_dB()
        self.get_average_count()
        self.get_measured_power()
        self.get_power_measuring_range()
        self.get_auto_range_status()
        self.get_measured_frequency()
        self.get_zero_magnitude()
        self.get_zero_state()
        self.get_photodiode_response()
        self.get_current_range()
        self.get_sensor_id()
        self.get_measured_current()
        pass

    def run_zero(self) -> None:
        resp = self.com.write("SENS:CORR:COLL:ZERO:INIT")
        time.sleep(0.2)
        logger.info("    PM100D({self.device_id}) - Power Meter Zeroed")
        return None

    def get_preset_wavelength(self) -> float:
        try_count = 0
        while True:
            try:
                self.wavelength = float(self.com.query("SENS:CORR:WAV?"))
                logger.debug( f"    PM100D({self.device_id}) - read wavelength at {repr(self.wavelength)}nm")
                break
            except:
                if try_count > 9:
                    logger.error( "    PM100D({self.device_id}) - FAILED to get wavelength." )
                    break
                else:
                    time.sleep(0.1)  #take a rest..
                    try_count = try_count + 1
                    logger.debug( "    PM100D({self.device_id}) - trying to get the wavelength again.." )
        return self.wavelength
    
    def set_preset_wavelength(self, wl:float) -> float:
        try_count = 0
        while True:
            try:
                self.com.write("SENS:CORR:WAV %f" % wl)
                time.sleep(0.005) # Sleep for 5 ms before rereading the wl.
                logger.info(f"    PM100D({self.device_id}) - wavelength set to {wl:.1f}nm")
                break
            except:
                if try_count > 9:
                    logger.error( "    PM100D({self.device_id}) - Failed to set wavelength." )
                    time.sleep(0.005) # Sleep for 5 ms before rereading the wl.
                    break
                else:
                    time.sleep(0.1)  #take a rest..
                    try_count = try_count + 1
                    logger.debug( "    PM100D({self.device_id}) - trying to set wavelength again.." )

        return self.get_preset_wavelength()
    
    def get_attenuation_dB(self) -> float:
        # in dB (range for 60db to -60db) gain or attenuation, default 0 dB
        self.attenuation_dB = float( self.com.query("SENS:CORR:LOSS:INP:MAGN?") )
        logger.debug(f"    PM100D({self.device_id}) - attenuation at {self.attenuation_dB}dB")
        return self.attenuation_dB

    def get_average_count(self) -> int:
        """each measurement is approximately 3 ms.
        returns the number of measurements
        the result is averaged over"""
        self.average_count = int( self.com.query("SENS:AVER:COUNt?") )
        logger.debug( f"    PM100D({self.device_id}) - average count: {self.average_count}")
        return self.average_count
    
    def set_average_count(self, cnt:int) -> int:
        """each measurement is approximately 3 ms.
        sets the number of measurements
        the result is averaged over"""
        self.com.write("SENS:AVER:COUNT %i" % cnt)
        logger.debug(f"    PM100D({self.device_id}) - average count is set to {cnt}")
        return self.get_average_count()
            
    def get_measured_power(self) -> float:
        self.power = float(self.com.query("MEAS:POW?"))
        logger.debug(f"    PM100D({self.device_id}) - Power measured: {self.power*1000:.2f}mW")
        return self.power
        
    def get_power_measuring_range(self) -> int:
        #un tested
        self.power_range = float(self.com.query("SENS:POW:RANG:UPP?")) # CHECK RANGE
        logger.debug(f"    PM100D({self.device_id}) - Power measuring range: {self.power_range*1000:.1f}mW")
        return self.power_range

    def set_power_range(self, range:float) -> None:
        #un tested
        self.com.write("SENS:POW:RANG:UPP {}".format(range))
        logger.debug(f"    PM100D({self.device_id}) - Power_measuring_range set to {range}mW")
        pass

    def get_auto_range_status(self) -> bool:
        resp = self.com.query("SENS:POW:RANG:AUTO?")
        self.auto_range = bool(int(resp))
        logger.debug(f"    PM100D({self.device_id}) - Get_auto_range status result: {self.auto_range}")
        return self.auto_range
    
    def set_auto_range(self, auto:bool = True) -> None:
        logger.debug( f"    PM100D({self.device_id}) - Set_auto_range: {auto}")
        if auto:
            self.com.write("SENS:POW:RANG:AUTO ON") # turn on auto range
        else:
            self.com.write("SENS:POW:RANG:AUTO OFF") # turn off auto range
    
    def get_measured_frequency(self) -> float:
        self.frequency = float(self.com.query("MEAS:FREQ?"))
        logger.debug(f"    PM100D({self.device_id}) - Frequency readout: {self.frequency:.1f}Hz")
        return self.frequency

    def get_zero_magnitude(self) -> float:
        resp = self.com.query("SENS:CORR:COLL:ZERO:MAGN?")
        self.zero_magnitude = float(resp)
        logger.debug(f"    PM100D({self.device_id}) - zero_magnitude: {self.zero_magnitude*1000:.2f}mW")
        return self.zero_magnitude
        
    def get_zero_state(self) -> bool: 
        resp = self.com.query("SENS:CORR:COLL:ZERO:STAT?")
        self.zero_state = bool(int(resp))
        logger.debug(f"    PM100D({self.device_id}) - zero_state: {self.zero_state}")
        return self.zero_state

    def get_photodiode_response(self) -> float:
        resp = self.com.query("SENS:CORR:POW:PDIOde:RESP?")
        #resp = self.ask("SENS:CORR:VOLT:RANG?")
        #resp = self.ask("SENS:CURR:RANG?")
        self.photodiode_response = float(resp) # A/W
        logger.debug(f"    PM100D({self.device_id}) - Photodiode_response: {self.photodiode_response*1000:.1f}mA/W")
        return self.photodiode_response 
    
    def get_measured_current(self) -> float:
        resp = self.com.query("MEAS:CURR?")
        self.current = float(resp)
        logger.debug(f"    PM100D({self.device_id}) - Measured current: {self.current*1000:.1f}mA")
        return self.current
    
    def get_current_range(self) -> float:
        resp = self.com.query("SENS:CURR:RANG:UPP?")
        self.current_range = float(resp)
        logger.debug(f"    PM100D({self.device_id}) - Preset current_range: {self.current_range*1000:.1f}mA")
        return self.current_range

    def get_sensor_id(self) -> str:
        self.sensor_id = self.com.query("SYST:SENS:IDN?").split(",")[0]
        logger.debug(f"    PM100D({self.device_id}) - Current connected sensor: {self.sensor_id}")
        return self.sensor_id