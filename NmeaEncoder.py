#NmeaEncoder.py

class NmeaEncoder:
    """class used for encoding messages into NMEA format"""
    
    def __init__(self, identifier):
        """constructor"""
        
        # used to determine who originated each message
        self.talker_identifier = identifier
        
    def encode(self, sentence_type, *args):
        """encode a message in NMEA format.
        
        i.e. $ttsss<CR><LF>
        i.e. $ttsss,arg1,arg2,chksum<CR><LF>"""
        
        # create the header for the message
        tt = self.talker_identifier
        sss = sentence_type
        encoded_msg = "$" + tt + sss
        
        # append any additional arguments and determine if chksum is required
        chksum_required = False
        for arg in args:
            chksum_required = True
            encoded_msg += "," + str(arg)
        
        # if chksum is required, generate it and append it
        if chksum_required:
            chksum = 0
            for char in encoded_msg:
                chksum += ord(char)
            encoded_msg += "," + str(chksum)
        
        # append the ending characters
        encoded_msg += "\r\n"
        
        # return the encoded message
        return encoded_msg
