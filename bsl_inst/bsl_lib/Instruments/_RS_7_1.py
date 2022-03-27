from ..Interface._bsl_serial import bsl_serial
from .._bsl_inst_info import bsl_inst_info_list as inst
from .._bsl_type import bsl_type

import time
import enum
import numpy as np
from typing import Union
from numpy.typing import NDArray

from loguru import logger
from pycolorname.pantone.pantonepaint import PantonePaint
from skimage import color

logger_opt = logger.opt(ansi=True)

@logger.catch(exclude=(bsl_type.DeviceConnectionFailed,bsl_type.DeviceInconsistentError,bsl_type.DeviceOperationError))
class RS_7_1:
    class _SYSTEM_UNIT(enum.Enum):
        RADIOMETRIC = 0; PHOTOMETRIC = 1; PERCENTAGE = 2
    class _STM_MODE(enum.Enum):
        ASCII_COMMA = 0; ASCII_COLUMN = 1; PACKED_BINARY = 2
    class POWER_UNIT(enum.Enum):
        RADIANCE = 0; IRRADIANCE = 1; LUMINANCE = 2; ILLUMINANCE=3; PERCENTAGE=4
    class OBSERVER_ANGLE(enum.Enum):
        DEG_2 = 2; DEG_10 = 10
    class LED_CHANNELS(enum.Enum):
        LEN_CHANS = list([3,4,5,6,7,8,11,13,14,16,19,20,21,22,23,24,26,27,28,29,30,31,33,34,36,37,38,39,41,42,43,45,46,47,49,51,52,53,54,55,57,59,60,61,62,63])
        FWHM = list([0.0, 0.0, 13.62, 27.44, 13.62, 16.41, 30.97, 14.81, 0.0, 0.0, 22.25, 0.0, 18.07, 24.06, 0.0, 14.81, 0.0, 0.0, 35.15, 106.8, 106.8, 32.22, 25.21, 18.53, 0.0, 20.28, 79.39, 79.39, 24.06, 13.62, 0.0, 0.0, 40.32, 17.83, 0.0, 21.05, 16.15, 0.0, 33.17, 0.0, 19.7, 24.06, 21.86, 0.0, 24.06, 31.81, 16.94, 0.0, 21.27, 0.0, 20.94, 29.85, 52.46, 21.36, 21.36, 0.0, 18.53, 0.0, 15.1, 21.86, 27.68, 31.81, 0.0, 0.0])
        WAVELENGTH = list([0.0, 0.0, 590.35, 498.75, 590.35, 399.0, 521.85, 627.11, 0.0, 0.0, 769.71, 0.0, 657.0, 712.89, 0.0, 627.11, 0.0, 0.0, 845.9, 571.15, 571.15, 901.51, 746.37, 632.75, 0.0, 452.86, 610.19, 610.19, 712.89, 590.35, 5990.9, 0.0, 936.91, 426.01, 0.0, 688.43, 616.27, 2937.8, 531.37, 0.0, 445.77, 729.16, 495.49, 0.0, 729.16, 525.64, 667.09, 0.0, 407.85, 0.0, 753.59, 474.73, 959.3, 700.74, 700.74, 0.0, 632.75, 0.0, 426.8, 495.49, 802.68, 525.64, 2747.6, 0.0])
    
    def __init__(self, device_sn="") -> None:
        self._target_device_sn = device_sn
        self.inst = inst.RS_7_1
        self.device_id = ""
        logger.info(f"Initiating bsl_instrument - M69920({device_sn})...")
        self._pantone_keys = PantonePaint().keys()
        
        self._com = self._serial_connect()

        if self._com.serial_port is not None:
            self.device_id = self._com_query('USN')
            self._system_init()
            logger.success(f"READY - RS_7_1 ({self.device_id}) Tunable Light Source.\n\n\n")
        else:
            self._raise_error(f"FAILED to connect to RS_7_1 Tunable Light Source!\n\n\n")
        pass

    def __del__(self, *args, **kwargs) -> None:
        self.close()
        return None

    def _serial_connect(self) -> bsl_serial:
        try:
            com_port = bsl_serial(inst.RS_7_1, self._target_device_sn)
        except Exception as e:
            logger.error(f"{type(e)}")
        return com_port

    #checked
    def _system_restart(self) -> None:
        """
        Reboot the light source to reset all runtime variables.
        """
        self._raise_info("Rebooting System!")
        self._com.writeline('RST')
        time.sleep(5)
        self._raise_info("System Rebooted!")
        return None

    def _system_init(self) -> None:
        # self._system_restart()
        # self._run_integrity_check()
        # self._run_basic_assurance_test()
        self._set_wavelength_range(360,1100)
        self._set_spectrum_transfer_format(self._STM_MODE.ASCII_COMMA)
        return None

    def _run_integrity_check(self) -> None:
        """
        - Performs an internal check of all RS-7 parameters and calibration 
        data, and verifies that:
            a) all monitored internal power supply rail voltages 
                are within tolerance.
            b) all parameters are within range & structures are intact.
            c) stored calibration data matches the serial number of the 
                LED board for which they were generated d) all structures 
                have a valid CRC (CRC32).

        Raises:
        --------
            Failed Test : `bsl_type.DeviceInconsistentError`
                System failed its power-on integrity test.
        """
        if self._com_cmd('ICK',5) != 0:
            self._raise_error("failed its power-on integrity check!")
        else:
            logger.success(f'    PASS - {self.inst.MODEL} passed its power-on integrity check.')
        return None

    def _run_basic_assurance_test(self) -> None:
        """
        - Rapidly sequence through all channels in order to verify basic functionality. 
        This is intended to execute as quickly as possible and is not intended as a 
        comprehensive audit of each channel’s performance. 

        - The test criteria is that each channel, set at 50% of maximum power, 
        demonstrates output power of at least 90% of the expected value.
        
        Raises:
        --------
            Faild Test : `bsl_type.DeviceInconsistentError`
                System failed its power-on integrity test.
        """
        resp = self._com_cmd('BAT',5)
        if self._com_cmd('ICK',5) != 0:
            self._raise_error("failed its power-on basic assurance test!")
        else:
            logger.success(f'    PASS - {self.inst.MODEL} passed its power-on basic assurance test.')
        return None

    def _set_UNI_unit(self, unit:_SYSTEM_UNIT) -> None:
        """
        - Choose the system UNI power unit.

        Parameters
        -----------
        unit : `RS_7_1._SYSTEM_UNIT`
            Choose from _SYSTEM_UNIT.RADIOMETRIC, _SYSTEM_UNIT.PHOTOMETRIC, 
            and _SYSTEM_UNIT.PERCENTAGE
        """
        msg = f"UNI{unit}"
        self._com_cmd(msg)
        return None
    
    def _set_irr_distance(self, distance_mm:int=0) -> None:
        """
        - Set the imaging/output plane's distance from the output port
        of the light source. (i.e. front surface)

        - In conjunction with _set_UNI_unit(), one can dictates the power
        operation unit of the system from [radiance, irradiance, luminance, 
        illuminance, and percentage].

        - When set to 0, indicating system running in luminance/radiance mode.

        Parameters
        -----------
        distance_mm : `int`
            (default = 0)
            distance from the output port of the light source in mm.
        """
        msg = f"IRR{str(distance_mm)}"
        self._com_cmd(msg)
        return None

    def _set_power_unit(
        self, unit:POWER_UNIT, irr_distance_mm:int = 0) -> None:
        
        if unit==self.POWER_UNIT.PERCENTAGE:
            self._set_UNI_unit(self._SYSTEM_UNIT.PERCENTAGE.value)
            self._set_irr_distance(0)
        elif unit==self.POWER_UNIT.RADIANCE:
            self._set_UNI_unit(self._SYSTEM_UNIT.RADIOMETRIC.value)
            self._set_irr_distance(0)
        elif unit==self.POWER_UNIT.IRRADIANCE:
            self._set_UNI_unit(self._SYSTEM_UNIT.RADIOMETRIC.value)
            self._set_irr_distance(irr_distance_mm)
        elif unit==self.POWER_UNIT.LUMINANCE:
            self._set_UNI_unit(self._SYSTEM_UNIT.PHOTOMETRIC.value)
            self._set_irr_distance(0)
        elif unit==self.POWER_UNIT.ILLUMINANCE:
            self._set_UNI_unit(self._SYSTEM_UNIT.PHOTOMETRIC.value)
            self._set_irr_distance(irr_distance_mm)

        self._raise_info(f"Power Unit set to {unit} with Irradiance distance = {irr_distance_mm}")
        return None

    def _set_optical_feedback(self, FBK:bool=True) -> None:
        """
        - Enable/Disable the realtime optical feedback that ultilize
        an internal photodiode in the light source to dynamically matching
        output power to requested power instead of relying on computed power.

        Parameters
        -----------
        FBK : `bool`
            (default = Ture)
        """
        msg = f"FBK{int(FBK)}"
        self._com_cmd(msg)
        self._raise_info(f"Optical Feedbacl set to {FBK}")
        return None

    def _set_spectrum_transfer_format(self, mode:_STM_MODE = _STM_MODE.ASCII_COMMA) -> None:
        """
        - WARNING: Changing wavelength_range away from default will
        break the normal function of other provided functions such as
        `get_current_spectrum`, `set_spectrum_raw` etc.,

        Parameters
        -----------
        mode : `_STM_MODE`
            (default = _STM_MODE.ASCII_COMMA)
        """
        self._com_cmd(f"STM{mode.value}")
        self._raise_info(f"Spectrum transfer format set to {mode}.")
        return None

    def _set_wavelength_range(self, min:int=360, max:int=1100) -> None:
        """
        - Set the wavelength range for OSP (Output Specturm) and 
        TSP (Set Target Spectrum) operations.

        - WARNING: Changing wavelength_range away from default will
        break the normal function of other provided functions such as
        `get_current_spectrum`, `set_spectrum_raw` etc.,


        Parameters
        ----------
        min : `int`
            (default to 360)
            Minimum wavelength for spectrum operation in nm.
            
        max : `int`
            (default to 1100)
            Maximum wavelength for spectrum operation in nm.
        """
        self._wavelength_min = min
        self._wavelength_max = max
        self._com_cmd(f"WLR{min},{max}")
        self._raise_info(f"Spectrum operation wavelength range set to {min}nm to {max}nm.")
        return None

    def _black_body_spectrum(self, temp:int) -> list[float]:
        spec = [self._planck(x+360,temp) for x in range(741)]
        return spec

    def _planck(self, wav:Union[float, int], T:int) -> float:
        h = 6.626e-34
        c = 3.0e+8
        k = 1.38e-23
        wav = wav*1e-9
        a = 2.0*h*c**2
        b = h*c/(wav*k*T)
        intensity = a/ ( (wav**5) * (np.exp(b) - 1.0) )
        return intensity

    def _com_query(self, msg, timeout:float = 0.5) -> str:
        self._com.flush_read_buffer()
        self._com.write(msg+'\r\n')
        resp = self._com.readline()
        if resp == "":
            return self._com.readline()
        else:
            return resp

    def _com_cmd(self, msg, timeout:float = 0.5) -> int:
        self._com.flush_read_buffer()
        self._com.write(msg+'\r\n')
        resp = self._com.readline()
        if resp == "":
            resp = self._com.readline()
            if resp != "Ok":
                logger.error(f"ERROR - {self.inst.MODEL} ({self.device_id}) - message from device: \"{resp}\"")
                raise bsl_type.DeviceOperationError
            else:
                return 0
        elif resp != "Ok":
            logger.error(f"ERROR - {self.inst.MODEL} ({self.device_id}) - message from device: \"{resp}\"")
            raise bsl_type.DeviceOperationError

    def _raise_error(self, msg:str=""):
        logger.error(f"ERROR - {self.inst.MODEL} ({self.device_id}) - {msg}")
        raise bsl_type.DeviceOperationError

    def _raise_warning(self, msg:str=""):
        logger.warning(f"    WARNING - {self.inst.MODEL} ({self.device_id}) - {msg}")
        return

    def _raise_info(self, msg:str=""):
        logger.info(f"    {self.inst.MODEL} ({self.device_id}) - {msg}")
        return







    #checked
    def find_closest_chan(self, wavelength:float) -> tuple([list[int], float, float]):
        """
        Return the channels' number, its[their] corresponding wavelength,
        and the FWHM of the LED channel[s] with closest wavelength provided.

        Uses
        ---------
        >>> led_chans = light.find_closest_chan(wavelength=500)[0]
        >>> light.set_power_chans(led_chans, powers=40)

        Parameters
        -----------
        wavelength : `float`
            Wavelength of interest to be accquired.

        Returns
        ----------
        LED_index[es] : `list[int]`
            List of index/indexes of LED channels that match closest to the
            requrested wavelength in the parameter.
        
        LED_wavelength : `float`
            Wavelength of the LED[s] with the channel specified in the LED_index[es].

        LED_FWHM : `float`
            FWHM of the the LED[s] with the channel specified in the LED_index[es].
        """
        lst = np.asarray(self.LED_CHANNELS.WAVELENGTH.value)
        fwhm = self.LED_CHANNELS.FWHM.value
        idx = (np.abs(lst - wavelength)).argmin()
        list_idx = list(np.where(lst==lst[idx])[0]+1)
        self._raise_info(f"Found LED ({repr(list_idx)}) with wavelength {lst[idx]}nm, FWHM {fwhm[idx]}nm from requested wavelength {wavelength}nm.")
        return (list_idx, lst[idx], fwhm[idx])

    #checked
    def set_iris_position(self, percentage:int=0) -> None:
        """
        - Set iris position as percentage **closed** (0 ~ 100%).
        - Make sure to set iris before seting output power in irradiance mode.

        Parameters:
        -----------
        percentage : `int`
            (Defaults to 0)
            Percentage close, i.e. to fully open the iris, set to 0.
        """
        if (percentage<=0 and percentage >= 100):
            self._raise_error("Cannot set percentage smaller than 0 or greater than 100!")
        msg = f"IRI{percentage}"
        self._com_cmd(msg)
        self._raise_info(f"Iris position set to {percentage}% closed.")
        time.sleep(3)
        return None

    #checked
    def set_standard_observer_angle(
        self, angle:OBSERVER_ANGLE=OBSERVER_ANGLE.DEG_2) -> None:
        """
        - Sets the CIE Tristimulus Standard Observer Angle as 2 degrees or 10 degrees. 
        The default at power-on is always 2 degrees.

        Parameters
        ----------
        angle : `RS_7_1.OBSERVER_ANGLE`
            (default to DEG_2)
            CIE Tristimulus Standard Observer Angle.
        """
        msg = f"SOB{angle.value}"
        self._com_cmd(msg)
        self._raise_info(f"Standard Observer Angle set to {angle.value} degrees")
        return None


    #checked
    def set_power_all(
        self, power:float, unit:POWER_UNIT=POWER_UNIT.PERCENTAGE, 
        irr_distance_mm:int=0) -> None:
        """
        - Set the output power of the overall system to specified unit and power.

        Parameters:
        ----------
        power : `float`
            Power of all channel in percentage.

        unit : `RS_7_1.POWER_UNIT`
            (default to Percentage)
            Select the unit of the power from radiance, irradiance, luminance,
            illuminance, and percentage.

        irr_distance_mm : `int`
            (default to 0)
            Distance from the surface of the output port of the light source to
            the desired imaging plane. Only used for irradiance or illuminance
            power profile.
        """
        self._set_power_unit(unit, irr_distance_mm)
        msg = f"SCP 0,{power}"
        self._com_cmd(msg)
        self._raise_info(f"All LED channels' power set to {power}.")
        return None

    #checked
    def set_power_chans(self, chans:Union[list[int], NDArray[np.int_], int], powers:Union[list[float], NDArray[np.float_], float], unit:POWER_UNIT=POWER_UNIT.PERCENTAGE, irr_distance_mm:int=0) -> None:
        """
        - Set the output power of the individual LED channel[s] tothe 
        specified unit and power.

        Parameters
        ----------
        chans : `list[int]` or 'int' or 'NDArray[int]'
            A int list consists individual LED channel number with an
            one-to-one correspondence to the powers array.

        powers : `list[float]` or 'float' or 'NDArray[float]'
            A floating number NDArray consists individual power settings with 
            an one-to-one correspondence to the chans array.

        unit : `RS_7_1.POWER_UNIT`
            (default to Percentage)
            Select the unit of the power from radiance, irradiance, luminance,
            illuminance, and percentage.

        irr_distance_mm : `int`
            (default to 0)
            Distance from the surface of the output port of the light source to
            the desired imaging plane. ONLY used for irradiance or illuminance
            power profile.
        """
        self._set_power_unit(unit, irr_distance_mm)
        if type(powers) is np.ndarray:
            powers = list(powers) 
        if type(chans) is np.ndarray:
            chans = list(chans)
        if type(powers) is not list:
            powers = list([powers]) 
        if type(chans) is not list:
            chans = list([chans]) 
        if len(powers)==1:
            powers = powers * len(chans)

        if (len(chans)!=len(powers)):
            self._raise_error("Provided list of channels doesn't have same amount of elemets as the list of power!")

        for chan in chans:
            if (chan not in self.LED_CHANNELS.LEN_CHANS.value):
                self._raise_error(f"Provided LED channel {chan} is not installed!")
        
        str_chans = [str(x) for x in chans]
        str_powers = [str(x) for x in powers]
        combined = str_chans+str_powers
        combined[0::2] = str_chans
        combined[1::2] = str_powers
        combined_proc = ','.join(combined)
        msg = f"SCP{combined_proc}"
        self._raise_info("LED Channel[s] power set.")
        self._com_cmd(msg)

    #TO BE CHECK
    def set_power_led_random(self) -> list[float]:
        """
        - Set output spectrum to a random spectrum.

        Uses
        ----------
        >>> set_spectrum_random()
        >>> set_power_fitted_spectrum(power = 30)

        Returns
        --------
        Output_spectrum : `list[float]`
            Actual output spectrum with a.u. from 360nm to 1100nm with step size of 1nm.
        """
        spectrum = np.random.random([len(self.LED_CHANNELS.LEN_CHANS.value)])*80
        self.set_power_chans(self.LED_CHANNELS.LEN_CHANS.value,spectrum)
        self._raise_info("Output spectrum set to a randomly generated spectrum.")
        return self.get_spectrum_output()

    #TO BE CHECK
    def set_power_fitted_spectrum(
        self, power:float, unit:POWER_UNIT=POWER_UNIT.PERCENTAGE, 
        irr_distance_mm:int=0, match_chrom:bool=False) -> None:
        """
        - Set the output power of the overall system to specified unit and power
        with provided spectrum fitting.

        - WARNINGL: Unknown chromaticity/spectrum accuracy! Always use in 
        conjunction with `get_power_output()` and `get_spectrum_output()` functions 
        or with external powermeter and spectrometer! For better chromaticity/
        spectrum accuracy, set your desired absolute (photometric/radiometric) unit 
        in the `set_spectrum_raw()` functions! 
        
        - WARNING: For chromaticity/color based spectrum setting, follow instructions 
        in `set_spectrum_rgb()`, `set_spectrum_CIExy()`, and `set_spectrum_pantone()` 
        to ensure chromaticity precision!
        
        - if set `match_chrom = True`, the output intensity may be locked to the 
        intensity gives the closest chromaticity match if other intensity give
        large error. ALWAYS use `get_power_output()` to confirm actual output
        power after called with `match_chrom = True`!

        Parameters
        ----------
        power : `float`
            Power of all channel in percentage.

        unit : `RS_7_1.POWER_UNIT`
            (default to Percentage)
            Select the unit of the power from radiance, irradiance, luminance,
            illuminance, and percentage.

        irr_distance_mm : `int`
            (default to 0)
            Distance from the surface of the output port of the light source to
            the desired imaging plane. Only used for irradiance or illuminance
            power profile.

        match_chrom : `bool`
            (default to False)
            Note that changing the output level using match_chrom == False can 
            result in a  chromaticity shift in the final output spectrum OSP, as 
            OUT merely adjusts all channels’ power level to match the requested 
            setting without regard to any wavelength shift caused by the change in 
            drive current. To maintain the current chromaticity, use default instead.
        """
        self._set_power_unit(unit, irr_distance_mm)
        if match_chrom:
            msg = f'OUTC{power:.3f}'
        else:
            msg = f'OUT{power:.3f}'
        self._com_cmd(msg)
        self._raise_info(f"System's output spectrum power set to: {power}, with unit {unit}, with irradiance distance: {irr_distance_mm}, with chroma_correction: {match_chrom}")
        return None


    #TO BE CHECK
    def set_spectrum_raw(
        self, 
        spectrum:Union[list[float], NDArray[np.float_]], 
        *,
        power:float=100, 
        power_unit:POWER_UNIT=POWER_UNIT.RADIANCE, 
        include_white:bool=True, 
        fit_max_pwr:bool=False, 
        chroma_correction:bool = False,
        irr_distance_mm:int=0) -> float:
        """
        - Sets and fit the spectrum to be fitted by the light source, with 1nm step size, and unit
        of radiance or irradiance ONLY. Default range from 360nm to 1100nm i.e. 741 points.

        - For lot of applications, it's easier to provide a normalized spectrum with a.u. 
        and set the arg. "fit_max_pwr" to Ture to get maximum power output for a specific
        spectrum of interest.

        Parameters
        ----------
        spectrum : `list[float]` or `NDArray[float]`
            Specturm data in specified unit with 1nm step size.

        power : `float`
            (default = 100)
            A floating number of individual power settings.
        
        power_unit : 'RS_7_1.POWER_UNIT'
            (defalut = POWER_UNIT.RADIANCE)
        
        include_white : `bool`
            (defalut = True)
            Whether including white LEDs in the fitting process.
        
        fit_max_pwr : `bool`
            (defalut = False)
            Fit to maximum possible power of the light source or not.
        
        chroma_correction : `bool`
            (defalut = False)
            Whether run chromaticity correction to the fitted spectrum to the 
            chromaticity of the request spectrum.

        irr_distance_mm : `int`
            (default to 0)
            Distance from the surface of the output port of the light source to
            the desired imaging plane. Only used for irradiance or illuminance
            power profile.

        Returns
        --------
        RMS_Error : `float`
            Root-Mean-Square error for the fitted specturm vs. provided spectrum.
        """
        if (power_unit is not self.POWER_UNIT.IRRADIANCE) and (power_unit is not self.POWER_UNIT.RADIANCE):
            self._raise_error("Only radiance and irradiance are supported for spectrum setting!")
        self._set_power_unit(power_unit, irr_distance_mm)
        
        spectrum = list(spectrum)
        if len(spectrum) != (self._wavelength_max - self._wavelength_min + 1):
            self._raise_error("Provided spectrum data's length doesn't match current wavelength min_max setting!")
        msg_spectrum = ','.join(['{:.6f}'.format(x) for x in spectrum])
        self._com_cmd(f"TSP{msg_spectrum}")

        self._com_cmd(f"STS{power:.4f}")

        msg_cmd = "FTS"
        if include_white:
            msg_cmd = msg_cmd + "W"
        if fit_max_pwr:
            msg_cmd = msg_cmd + "M"

        self._com_cmd(f"{msg_cmd}")
        if chroma_correction:
            self._com_cmd("CCS")
        self._raise_info(f"Raw spectrum set with RMS Error:{self.get_E_rms_fitted_spectrum()}")
        return self.get_E_rms_fitted_spectrum()

    #TO BE CHECK
    def set_spectrum_CIExy(self, CIEx:float, CIEy:float) -> tuple[float, float]:
        """
        - Fit the output spectrum to a specified CIE 1931 x,y chromaticity setting.
        
        - WARNING: Always set requested output power level before calling 
        this function! (with `set_power_output()`)
        
        - Set `match_chrom = Ture` when calling set_`power_fitted_spectrum()`
        to maintain the chromaticity matching. 
        (SEE WARNING in `power_fitted_spectrum()`)

        Uses
        ----------
        >>> set_power_output(30)
        >>> set_CIE_chroma(0.125, 0.246)

        Parameters
        ----------
        CIEx : 'float'
            CIEx coordinate for chromaticity setting.

        CIEy : 'float'
            CIEy coordinate for chromaticity setting.

        Returns:
        ----------
        (A_CIEx, A_CIEy) : `[float, float]`
            Actual fitted CIEx,y chromaticity in CIE 1931 standard.
        """
        if self.get_power_output() <0.1:
            self._raise_warning(f"Output power cannot be zero before setting chromaticity based spectrum, forcing it to 0.1%.")
            self.set_power_all(0.1)
            
        self._com_cmd(f"CCS{CIEx:.6f},{CIEy:.6f}")
        self._raise_info(f"Set output spectrum to CIExy chromaticity {CIEx:.6f},{CIEy:.6f}.")
        return self.get_chromaticity_output()

    #TO BE CHECK
    def set_spectrum_black_body(
        self, temp:int, power:float=1, power_unit:POWER_UNIT=POWER_UNIT.PERCENTAGE, 
        irr_distance_mm:int=0) -> float:
        """
        - Sets and fit the spectrum to be fitted by the light source, with 
        1nm step size, and unit of radiance or irradiance ONLY. Default 
        range from 360nm to 1100nm i.e. 741 points.
        
        Uses
        ----------
        >>> set_specturm_black_body(temp=3000,30)

        Parameters
        ----------
        temp : `int`
            Requested black body temperature in Kelvins.
        
        power_unit : `RS_7_1.POWER_UNIT`
            (default to Percentage)
            Select the unit of the power from radiance, irradiance, luminance,
            illuminance. NO percentage setting available for spectrum based 
            output setting! 

        irr_distance_mm : `int`
            (default to 0)
            Distance from the surface of the output port of the light source to
            the desired imaging plane. ONLY used for irradiance or illuminance
            power profile.

        Returns
        --------
        RMS_Error : `float`
            Root-Mean-Square error for the fitted specturm.
        """
        spectrum = self._black_body_spectrum(temp)
        xmin=min(spectrum) 
        xmax=max(spectrum)
        for i, x in enumerate(spectrum):
            spectrum[i] = (x-xmin) / (xmax-xmin)
        
        self._raise_info(f"Setting Output spectrum to Black Body spectrum with temperature: {temp} Kelvins.")
        return self.set_spectrum_raw(spectrum, power=power, power_unit=power_unit, irr_distance_mm=irr_distance_mm)

    #TO BE CHECK
    def set_spectrum_rgb(self, r:np.uint8, g:np.uint8, b:np.uint8) -> float:
        """
        - Set output spectrum to a specified RGB color profile.
        
        - WARNING: Always set requested output power level before calling 
        this function! (with `set_power_output()`)
        
        - Set `match_chrom = Ture` when calling set_`power_fitted_spectrum()`
        to maintain the chromaticity matching. 
        (SEE WARNING in `power_fitted_spectrum()`)

        Uses
        ----------
        >>> set_power_output(30)
        >>> set_spectrum_rgb(125,250,85)

        Parameters
        ----------
        R : `int`
            RGB color Red, 8 bits color range from 0 to 255

        G : `int`
            RGB color Green, 8 bits color range from 0 to 255

        B : `int`
            RGB color Blue, 8 bits color range from 0 to 255
        
        Returns
        --------
        RMS_Error : `float`
            Root-Mean-Square error for the fitted specturm.
        """
        if ((r>255 or r<0) or (g>255 or g<0) or (b>255 or b<0)):
            self._raise_error("Provided RGB values are out of range!")
        CIExyz = color.rgb2xyz([r/255.0,g/255.0,b/255.0])
        X=CIExyz[0]
        Y=CIExyz[1]
        Z=CIExyz[2]
        x = X / (X + Y + Z)
        y = Y / (X + Y + Z)
        self.set_spectrum_CIExy(x,y)
        self._raise_info(f"Output spectrum set to match RGB color: ({r}, {g}, {b})")
        return self.get_E_rms_fitted_spectrum()

    #TO BE CHECK
    def set_spectrum_pantone(self, color_name:str) -> float:
        """
        - Set output spectrum to a specified pantone color profile.

        - WARNING: Always set requested output power level before calling 
        this function! (with `set_power_output()`)
        
        - Set `match_chrom = Ture` when calling set_`power_fitted_spectrum()`
        to maintain the chromaticity matching. 
        (SEE WARNING in `power_fitted_spectrum()`)

        Uses
        ----------
        >>> set_power_output(30)
        >>> set_spectrum_pantone('Orange Peel')

        Parameters
        ----------
        color_name : `str`
            Pantone Color name in `PEP8` naming convention, or a partial name
            can be provided for auto search in Pantone Color profile, a warning
            message will be raise no matter how many mathing[s] are found!
        
        Returns
        --------
        RMS_Error : `float`
            Root-Mean-Square error for the fitted specturm.
        """
        key = [s for s in self._pantone_keys if color_name.lower() in s.lower()]
        if len(key) == 0:
            self._raise_error(f"Color \"{color}\" is not found in Pantone Color set!")
        if key[0] != color:
            self._raise_warning(f"No exact match found, assuming color \"{key[0]}\"")
        (r, g, b) = (PantonePaint()[key[0]])
        self.set_spectrum_rgb(r,g,b)
        self._raise_info(f"Output spectrum set to match Pantone Color: {key[0]}.")
        return self.get_E_rms_fitted_spectrum()



    #checked
    def get_optical_feedback_gain(self) -> float:
        """
        Get latest optical feedback gain factor, nomnial close to 1.

        Returns:
        --------
            FBG : `float`
                Optical feedback gain
            
        """
        gain = float(self._com_query('FBG'))
        self._raise_info(f"Current system optical feedback gain: {gain:.3f}")
        return gain

    #checked
    def get_power_output(
        self, unit:POWER_UNIT=POWER_UNIT.PERCENTAGE, irr_distance_mm:int = 0) -> float:
        """
        - Get the output power of the overall system in specified unit.

        Parameters
        ----------
            unit : `RS_7_1.POWER_UNIT`
                (default to Percentage)
                Select the unit of the power from radiance, irradiance, luminance,
                illuminance, and percentage.
                
            irr_distance_mm : `int`
                (default to 0)
                Distance from the surface of the output port of the light source to
                the desired imaging plane. Only used for irradiance or illuminance
                power profile.
        
        Returns
        ---------
            Actual_Power : `float`
                Actual measured output power of the light source in requested unit.
        """
        self._set_power_unit(unit, irr_distance_mm)
        cmd = f"OUTA"
        pwr=float(self._com_query(cmd))
        self._raise_info(f"Total output power: {pwr}.")
        return pwr

    #TO BE CHECK
    def get_power_all_chans(
        self, unit:POWER_UNIT=POWER_UNIT.PERCENTAGE, irr_distance_mm:int = 0
        ) -> tuple([list[int], list[float]]):
        """
        - Return all the non-OFF channels' current output powers.

        Parameters
        ----------
        unit : `RS_7_1.POWER_UNIT`
            (default to Percentage)
            Select the unit of the power from radiance, irradiance, luminance,
            illuminance, and percentage.
            
        irr_distance_mm : `int`
            (default to 0)
            Distance from the surface of the output port of the light source to
            the desired imaging plane. Only used for irradiance or illuminance
            power profile.
    
        Returns
        ---------
        (chans, powers) : `tuple(list[int], list[float])`
            Two lists of individual channels' number and its corresponding power.
            ONLY currently ON LED's power will be returned.
        """
        chans = list()
        powers = list()
        self._set_power_unit(unit, irr_distance_mm)
        resp = self._com_query('SCP')
        
        if resp=="":
            self._raise_warning("All LED channels are currently OFF!")
            
        while(resp != ""):
            chans.append(resp.split(',')[0])
            powers.append(resp.split(',')[1])
            resp = self._com.readline()
            
            self._raise_info(f"All ON LEDs power info received.")
            return (chans,powers)

    #checked
    def get_color_temp(self) -> float:
        """
        - Return the Correlated Color Temperature of the current 
        output spectrum in degrees Kelvin.

        Returns:
        --------
        Color_temp : `float`
            Correlated Color Temperature in degree Kelvin.
        """
        temp = self._com_query('CCT')
        if temp != "":
            temp=float(temp)
        else:
            temp=0
        self._raise_info(f"Current output spectrum's equivalence color temperature: {temp:.1f} Kelvins.")
        return temp

    #checked
    def get_E_rms_fitted_spectrum(self) -> float:
        """
        - Get Root-Mean-Square error for the fitted specturm vs. provided spectrum.
        
        Returns
        --------
        RMS_Error : `float`
            Root-Mean-Square error for the fitted specturm vs. provided spectrum.
        """
        erms = float(self._com_query("RPE"))
        self._raise_info(f"Output spectrum matching RMS Error: {erms:.3f}.")
        return erms

    #checked
    def get_chromaticity_output(self) -> tuple[float, float]:
        """
        - Return the CIE 1931 chromaticity of the current output spectrum.

        Returns:
        ----------
        (A_CIEx, A_CIEy) : `[float, float]`
            Actual fitted CIEx,y chromaticity in CIE 1931 standard.
        """
        CIExy = list(map(float, self._com_query("OXY").split(',')))
        self._raise_info(f"Actual output spectrum in CIExy chromaticity {CIExy[0]},{CIExy[1]}.")
        return (CIExy[0], CIExy[1])

    #checked
    def get_tristimulus_output(self) -> tuple[float, float, float]:
        """
        - Return the tristimulus of the current output spectrum OSP using 
        theStandard Observer Angle as set by `set_standard_observer_angle`. 
        
        - Note that for 2 degree observer, the tristimulus Y value will 
        represent the output power level in photometric units (lm/m2, cd/m2), 
        identical to what the 'get_output_power_all()' function would return 
        when POWER_UNIT = LUMINANCE or ILLUMINANCE.

        Returns:
        ----------
        (A_CIEx, A_CIEy, A_CIEz) : `[float, float]`
            Actual fitted CIEx,y chromaticity in CIE 1931 standard.
        """
        CIExyz = list(map(float, self._com_query("OXYZ").split(',')))
        self._raise_info(f"Actual output spectrum in CIExyz space: {CIExyz[0]:.3f},{CIExyz[1]:.3f},{CIExyz[2]:.3f}")
        return (CIExyz[0], CIExyz[1], CIExyz[2])

    #checked
    def get_spectrum_output(self, power_unit:POWER_UNIT=POWER_UNIT.RADIANCE) -> list[float]:
        """
        - Get the fitted spectrum from the light source, with 1nm step size, and unit
        of radiance or irradiance ONLY. Default range from 360nm to 1100nm i.e. 741 points.

        Parameters
        ----------
        power_unit : 'RS_7_1.POWER_UNIT'
            (defalut = POWER_UNIT.RADIANCE)
        
        Returns
        --------
        spectrum : `list[float]`
            Specturm data in specified unit with 1nm step size.
        """
        if (power_unit is not self.POWER_UNIT.IRRADIANCE) and (power_unit is not self.POWER_UNIT.RADIANCE):
            self._raise_error("Only radiance and irradiance are supported for spectrum setting!")
        self._set_power_unit(power_unit)
        spectrum = self._com_query("OSP")
        spectrum = list(map(float, spectrum.split(',')))
        self._raise_info(f"Actual output spectrum received with power unit {power_unit}.")
        return spectrum

    #checked
    def get_spectrum_led(self, led_chan:int, power_unit:POWER_UNIT=POWER_UNIT.RADIANCE) -> list[float]:
        """
        - Get the specified LED's realtime power spectrum from the light source, 
        with 1nm step size, and unit of radiance or irradiance ONLY. Default range 
        from 360nm to 1100nm i.e. 741 points.

        Uses
        ----------
        >>> (led_chans,lambda,fwhm) = find_closest_chan(wavelength=650)
        >>> get_led_spectrum(led_chan[0])


        Parameters
        ----------
        led_chan : `int`
            LED channel number as listed in RS_7_1.LED_CHANNELS.LED_CHANS

        power_unit : 'RS_7_1.POWER_UNIT'
            (defalut = POWER_UNIT.RADIANCE)
        
        Returns
        --------
        spectrum : `list[float]`
            Specturm data in specified unit with 1nm step size.
        """
        if (power_unit is not self.POWER_UNIT.IRRADIANCE) and (power_unit is not self.POWER_UNIT.RADIANCE):
            self._raise_error("Only radiance and irradiance are supported for spectrum setting!")
        self._set_power_unit(power_unit)
        spectrum = self._com_query(f"OSP{led_chan}")
        spectrum = list(map(float, spectrum.split(',')))
        self._raise_info(f"Actual spectrum of LED channel {led_chan} in unit {power_unit} received.")
        return spectrum

    def close(self) -> None:
        if self._com is not None:
            self.set_power_all(0)
            self._com.close()
            del self._com
        logger.info(f"CLOSED - RS_7_1 ({self.device_id}) Tunable Light Source.\n\n\n")
        pass

    """
    <sorrow-blue>
    Just put something here to make it to the holy glory
    line of 1000th yeah.
    </sorrow-blue>
    """