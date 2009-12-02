from NmeaEncoder import *
from NmeaDecoder import *
from Interface import *


encoder = NmeaEncoder("IS")
decoder = NmeaDecoder()

def tx_rx_decode(func_name, msg_to_send):
    """transmit to the plane, recieve a response, and decode it."""
    attempts = 0
    while (attempts < 3):
        response = "$PVCPT,arg1,arg2,1160\r\n"
        # might put this in to work with my decoder
        # response += "\n"
        if response:
            try:
                return decoder.decode(response)
            except DecodeError as e:
                attempts += 1
                error_msg = e.value
        else: #timeout
            attempts += 1
            error_msg = e.value
    raise InterfaceError(error_msg)

try:
    msg_to_send = encoder.encode("CPT", "picture_num")
    print "msg to send is:"
    print repr(msg_to_send)
    x1, x2 = tx_rx_decode("take_picture", msg_to_send)
    print "resp is:"
    print x1
    print x2
except InterfaceError as e:
    raise InterfaceError(e.value)


