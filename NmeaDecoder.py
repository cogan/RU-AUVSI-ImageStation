#NmeaDecoder.py

from DecodeError import *

class NmeaDecoder:
    """class used for decoding messages sent in the NMEA format"""
    
    def __init__(self):
        """constructor"""
        pass
        
    def decode(self, sentence):
        """decode an NMEA message"""
        
        # remove trailing characters
        sentence = sentence.replace('\r', '')
        sentence = sentence.replace('\n', '')
        
        # parse args out of sentence
        args = sentence.split(',')

        # if there are arguments a checksum is required
        if len(args) > 1:
            
            # get the given checksum
            chksum = int(args[-1])
            
            # calculate expected checksum (not including commas)
            calc_chksum = 0
            for arg in args[0:-1]:
                for char in arg:
                    calc_chksum += ord(char)
                calc_chksum += ord(',')
                    
            # subtract one comma value in order to be consistent
            calc_chksum -= ord(',')
                    
            # compare and return arguments if correct
            if chksum == calc_chksum:
                return args[1:-1]
            else:
                raise DecodeError("chksum mismatch: calculated " \
                    + str(calc_chksum) + " but received " + str(chksum))
        else:
            return True
