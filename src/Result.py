class Result:
    """ A class to encapsulate the result of  grade management operations.
    This class provides a standardized way to return operation results that can be easily
    serialized and transmitted over a network or API
    
    Attributes:
        success (bool): True if operation successful.
        message (str):  A descriptive message.
        data (any):     Optional data payload returned.
    """
    def __init__(self, success:bool, message: str="", data:any=None):
        self.success = success
        self.message = message
        self.data = data
    def to_dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data
        }