class bsl_inst_info_class:
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
