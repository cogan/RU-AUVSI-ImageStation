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
        
        # check for garbage
        for char in sentence:
            if not (33 <= ord(char) <= 126):
                raise DecodeError("received garbage message containing illegal characters")
        
        # parse args out of sentence
        args = sentence.split(',')

        # if code is $PVERR raise exception 
        if args[0] == "$PVERR":
            raise DecodeError("received $PVERR message from plane")

        # if the header is not the proper length raise an exeception
        if len(args[0]) != 6:
            raise DecodeError("received garbage message containing an illegal header")

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
            
    def decode_bin(self, sentence):
        """decode an NMEA message containing binary data"""
        
        # strip \r\n at end of message
        sentence = sentence[:-2]
        
        # first strip the header and then strip its comma
        header = sentence[:7]
        header = header[:-1]
        
        # now create a correct args list
        args = sentence[7:].rsplit(',', 1)
        args.insert(0, header)
        
        # if code is $PVERR raise exception
        if args[0] == "$PVERR":
            raise DecodeError("received $PVERR message from plane")
        
        # if the header is not the proper length raise an exeception
        if len(args[0]) != 6:
            raise DecodeError("received garbage message containing an illegal header")

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
