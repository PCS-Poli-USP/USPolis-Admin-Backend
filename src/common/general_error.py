class GeneralError(Exception):
    message: str
    code: int

    def __init__(self, message, code):
        self.message = message
        self.code = code

    def __str__(self):
        return self.message

    def get_tuple(self):
        return {"message": self.message}, self.code
