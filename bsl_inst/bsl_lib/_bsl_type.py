class bsl_type:
    class CustomError(Exception):
        pass
    class DeviceConnectionFailed(CustomError):
        pass
    class DeviceOperationError(CustomError):
        pass
    class DeviceInconsistentError(CustomError):
        pass