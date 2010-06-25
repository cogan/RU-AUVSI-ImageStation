###############################################################################
#
# file: InterfaceError.py 
# author: Cogan Noll
# email: colgate360@gmail.com
# last modified: 2010
#
###############################################################################

class InterfaceError(Exception):
    """exception generated by an interface, usually due to a communications
    failure."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
