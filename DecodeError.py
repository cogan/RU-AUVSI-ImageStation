###############################################################################
#
# file: DecodeError.py 
# author: Cogan Noll
# email: colgate360@gmail.com
# last modified: 2010
#
###############################################################################

class DecodeError(Exception):
    """exception generated during the NmeaDecoding process."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
