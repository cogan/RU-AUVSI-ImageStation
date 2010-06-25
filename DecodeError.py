class DecodeError(Exception):
    """exception generated during the NmeaDecoding process."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
