from _bsl_inst_info_class import bsl_inst_info_class

class bsl_inst_info_list:
    PM100D = bsl_inst_info_class(
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

    M69920 = bsl_inst_info_class(
        MANUFACTURE="Newport",
        MODEL="M69920",
        TYPE="Power Supply",
        INTERFACE="Serial",
        BAUDRATE=0,
        SERIAL_NAME="M69920",
        QUERY_CMD="IDN?",
        QUERY_E_RESP="69920"
    )

    HR4000CG = bsl_inst_info_class(
        MANUFACTURE="Ocean Optics",
        MODEL="HR4000CG",
        TYPE="Spectrometer",
        SERIAL_NAME="???",
        INTERFACE="USB-SDK",
        USB_PID="???",
        USB_VID="???"
    )

    TEST_DEVICE_NO_BAUD = bsl_inst_info_class(
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

    TEST_DEVICE_BAUD = bsl_inst_info_class(
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

