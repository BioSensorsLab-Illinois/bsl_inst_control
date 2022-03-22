class bsl_instrument:
    def __init__(self, *, MANUFACTURE:str="N/A", MODEL:str="N/A", TYPE:str="N/A", INTERFACE:str="Serial", BAUDRATE:int=0, SERIAL_NAME:str="N/A", USB_PID:str="N/A", USB_VID:str="N/A", QUERY_CMD:str="N/A", QUERY_E_RESP:str="N/A", SN_REG=".*", QUERY_SN_CMD=""):
        self.MANUFACTURE            =   MANUFACTURE
        self.MODEL                  =   MODEL              
        self.TYPE                   =   TYPE               
        self.BAUDRATE               =   BAUDRATE           
        self.SERIAL_NAME            =   SERIAL_NAME          
        self.USB_PID                =   USB_PID  
        self.USB_VID                =   USB_VID     
        self.QUERY_CMD              =   QUERY_CMD   
        self.QUERY_E_RESP           =   QUERY_E_RESP
        self.QUERY_SN_CMD           =   QUERY_SN_CMD
        self.INTERFACE              =   INTERFACE
        self.SN_REG                 =   SN_REG

class bsl_instrument_list:
    PM100D = bsl_instrument(
        MANUFACTURE="THORLAB",
        MODEL="PM100D",
        TYPE="Power Meter",
        INTERFACE="VISA",
        USB_PID="0x8078",
        USB_VID="0x1313",
        QUERY_CMD="*IDN?",
        QUERY_SN_CMD="*IDN?",
        QUERY_E_RESP="PM100D",
        SN_REG="(?<=,)P[0-9]+(?=,)"
    )

    M69920 = bsl_instrument(
        MANUFACTURE="Newport",
        MODEL="M69920",
        TYPE="Power Supply",
        INTERFACE="Serial",
        BAUDRATE=0,
        SERIAL_NAME="M69920",
        QUERY_CMD="IDN?",
        QUERY_E_RESP="69920"
    )

    HR4000CG = bsl_instrument(
        MANUFACTURE="Ocean Optics",
        MODEL="HR4000CG",
        TYPE="Spectrometer",
        SERIAL_NAME="???",
        INTERFACE="USB-SDK",
        USB_PID="???",
        USB_VID="???"
    )

    TEST_DEVICE_NO_BAUD = bsl_instrument(
        MANUFACTURE="BSL",
        MODEL="TEST_DEVICE_BAUD",
        TYPE="TEST_DEVICE_BAUD",
        SERIAL_NAME="Incoming",
        INTERFACE="Serial",
        USB_PID="0x8078",
        USB_VID="0x1313",
        QUERY_CMD="*IDN?",
        QUERY_SN_CMD="*IDN?",
        QUERY_E_RESP="PM100D",
        SN_REG="(?<=,)P[0-9]+(?=,)"
    )

    TEST_DEVICE_BAUD = bsl_instrument(
        MANUFACTURE="BSL",
        MODEL="TEST_DEVICE_NO_BAUD",
        TYPE="TEST_DEVICE_BAUD",
        BAUDRATE=115200,
        SERIAL_NAME="Incoming",
        INTERFACE="Serial",
        USB_PID="0x8078",
        USB_VID="0x1313",
        QUERY_CMD="*IDN?",
        QUERY_SN_CMD="*IDN?",
        QUERY_E_RESP="PM100D",
        SN_REG="(?<=,)P[0-9]+(?=,)"
    )

