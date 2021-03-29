class FFInvalidLink(Exception):
    def __init__(self, message):
        super().__init__(message)
        pass

class CloudflareError(Exception):
    def __init__(self, message):
        super().__init__(message)
        pass

class InvalidChapterID(Exception):
    def __init__(self, message):
        super().__init__(message)
        pass

class InvalidSearchType(Exception):
    def __init__(self, message):
        super().__init__(message)
        pass