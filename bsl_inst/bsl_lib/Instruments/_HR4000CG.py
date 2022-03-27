import seabreeze.spectrometers as sb
from .._bsl_inst_info import bsl_inst_info_list as inst
from .._bsl_type import bsl_type
import numpy
from numpy.typing import NDArray
from loguru import logger

logger_opt = logger.opt(ansi=True)
    
@logger.catch(exclude=(bsl_type.DeviceConnectionFailed,bsl_type.DeviceInconsistentError,bsl_type.DeviceOperationError))
class HR4000CG:
    def __init__(self, device_sn:str=None) -> None:
        logger.info(f"Initiating bsl_instrument - SPEC({device_sn})...")
        self.inst = inst.HR4000CG
        self.target_device_sn = device_sn
        self.device_id=""
        self.device_model=""
        
        self.__connect_spectrometer()
            
        if self.spec is not None:
            logger.success(f"READY - OceanOptics PM100D Spectrometer \"{self.device_id}\"\n\n")
        return None

    def __del__(self, *args, **kwargs) -> None:
        self.close()
        return None

    def __connect_spectrometer(self) -> None:
        """
        - Try to connect to spectrometer based on the s/n provided, if no
        s/n is provided, connect to the next available spectrometer on the bus.

        Raises:
            self.DeviceConnectionFailed: Failed to connect to spectrometer.
        """
        self.spec = None
        if len(sb.list_devices()) == 0:
            logger.opt(ansi=True).error(f"<light-blue><italic>{self.inst.MODEL} ({self.target_device_sn})</italic></light-blue> not found on communication bus.\n\n\n")
            raise bsl_type.DeviceConnectionFailed
        
        logger.trace(f"    Devices found on bus: {str(sb.list_devices())}")
        try:
            if self.target_device_sn is (None or ""):
                # with sb.Spectrometer.from_first_available() as spec_device:
                self.spec = sb.Spectrometer.from_first_available()
            elif self.target_device_sn in str(sb.list_devices()):
                # with sb.Spectrometer.from_serial_number(self.target_device_sn) as spec_device:
                self.spec = sb.Spectrometer.from_serial_number(self.target_device_sn)
            else:
                logger.error(f"FAILED - Device[s] found on the bus, but failed to find requested device with s/n: \"{self.target_device_sn}\".\n\n\n")
                raise bsl_type.DeviceConnectionFailed
        except:
            logger.error(f"FAILED - Device[s] found on the communication bus, but failed to make connection.\n\n\n")
            raise bsl_type.DeviceConnectionFailed
            
        self.device_id = self.spec.serial_number
        self.device_model = self.spec.model
        return None

    def get_wavelength(self) -> NDArray[numpy.float_]:
        """
        - wavelength array of the spectrometer
        - wavelengths in (nm) corresponding to each pixel of the spectrometer

        Returns
        -------
        wavelengths : `numpy.ndarray`
            wavelengths in (nm)
        """
        return self.spec.wavelengths()

    def get_intensity(self, correct_dark_counts: bool = False, correct_nonlinearity: bool = False) -> NDArray[numpy.float_]:
        """
        - measured intensity array in (a.u.)

        Measured intensities as numpy array returned by the spectrometer.
        The measuring behavior can be adjusted by setting the trigger mode.
        Pixels at the start and end of the array might not be optically
        active so interpret their returned measurements with care. Refer
        to the spectrometer's datasheet for further information.

        Parameters
        ----------
        correct_dark_counts : `bool`
            If requested and supported the average value of electric dark
            pixels on the ccd of the spectrometer is subtracted from the
            measurements to remove the noise floor in the measurements
            caused by non optical noise sources.
        correct_nonlinearity : `bool`
            Some spectrometers store non linearity correction coefficients
            in their eeprom. If requested and supported by the spectrometer
            the readings returned by the spectrometer will be linearized
            using the stored coefficients.

        Returns
        -------
        intensities : `numpy.ndarray`
            measured intensities in (a.u.)
        """
        return self.spec.intensities(correct_dark_counts, correct_nonlinearity)

    def get_spectrum(self) -> NDArray[numpy.float_]:
        """
        - returns wavelengths and intensities as single array

        Uses
        ----------
        >>> (wavelengths, intensities) = spec.spectrum()

        Parameters
        ----------
        correct_dark_counts : `bool`
            see `Spectrometer.intensities`
        correct_nonlinearity : `bool`
            see `Spectrometer.intensities`

        Returns
        -------
        spectrum : `numpy.ndarray`
            combined array of wavelengths and measured intensities
        """
        return self.spec.spectrum()

    def set_integration_time_micros(self, exp_us:int) -> None:
        """
        - set the integration time in microseconds

        Parameters
        ----------
        integration_time_micros : `int`
            integration time in microseconds
        """
        self.spec.integration_time_micros(exp_us)
        return None

    @property
    def integration_time_limit_us(self) -> tuple[int,int]:
        """
        - return the hardcoded minimum and maximum integration time

        Returns
        -------
        integration_time_micros_min_max : `tuple[int, int]`
            min and max integration time in micro seconds
        """
        return self.spec.integration_time_micros_limits
    
    @property
    def device_max_intensity(self) -> float:
        """
        - return the maximum intensity of the spectrometer

        Returns
        -------
        max_intensity : `float`
            the maximum intensity that can be returned by the spectrometer in (a.u.)
            It's possible that the spectrometer saturates already at lower values.
        """
        return self.spec.max_intensity

    @property
    def device_pixel_count(self) -> int:
        """the spectrometer's number of pixels"""
        return self.spec.pixels

    def close(self) -> None:
        if self.spec is not None:
            self.spec.close()
            del self.spec
        logger.info(f"CLOSED - OceanOptics PM100D Spectrometer \"{self.device_id}\"\n\n\n")
        return None

