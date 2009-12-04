#DebugInterface.py

from Interface import *
from NmeaEncoder import *
from NmeaDecoder import *

import time

class DebugInterface(Interface):
    """interface class to use when debugging."""
    
    def __init__(self, port="/dev/ttyUSB0", baud=9600):
        """constructor"""
        
        print "Using the debugging interface"
    
    #*
    #* Define Abstract functions
    #*
    
    def take_picture(self, picture_num):
        """snap a picture."""
        pass
    
    def resume_search(self):
        """have the camera resume it's search pattern."""
        pass
        
    def lock_target(self, xa, ya):
        """lock onto a target given pixels xa and ya."""
        pass
        
    def download_to_flc(self):
        """download pictures form the camera memory onto the
        flight linux computer."""
        pass

    def generate_crop(self, picture_num, xa, ya, xb, yb):
        """generate a crop of an image given the image number,
        xa, ya, xb, and yb. which represent the top left and bottom right
        corners of a rectangle."""
        pass
        
    def request_info(self, picture_num):
        """get all positional info about a picture
        i.e camera angles, plane angles, gps coordinates"""
        pass
        
    def request_size(self, picture_num, crop_num):
        """get the size of a crop"""
        return 10043
        
    def download_segment(self, picture_num, crop_num, segment_num): 
        """download a segment of an image"""
        time.sleep(1)
        
    def camera_pan_left(self, increment):
        """have the camera pan left."""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("CLT", increment)
                return self.tx_rx_decode(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")
        
    def camera_pan_right(self, increment):
        """have the camera pan right."""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("CRT", increment)
                return self.tx_rx_decode(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")
        
    def camera_tilt_up(self, increment):
        """have the camera tilt upwards."""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("CUP", increment)
                return self.tx_rx_decode(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")
        
    def camera_tilt_down(self, increment):
        """have the camera tilt down."""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("CDN", increment)
                return self.tx_rx_decode(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")
    
    def camera_reset(self):
        """have the camera set itself to it's home coordinates"""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("CRE")
                return self.tx_rx_decode(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")
                
    def ping(self):
        """ping the plane"""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("PNG")
                t1 = time.time()
                self.tx_rx_decode(msg_to_send)
                t2 = time.time()
                return (t2-t1)*1000.0
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")

    #*
    #* Non-Abstract functions
    #*

    def tx_rx_decode(self, msg_to_send):
        """transmit to the plane, recieve a response, and decode it."""
        attempts = 0
        while (attempts < 3):
            self.ser.write(msg_to_send)
            ### DEBUGGING ###
            print "sending msg: %s" % (msg_to_send,)
            ### /DEBUGGING ###
            response = self.ser.readline()
            if response:
                ### DEBUGGING ###
                print "received msg: %s" % (response,)
                ### /DEBUGGING ###
                try:
                    ### DEBUGGING ###
                    print "returned args array: %s" % (self.decoder.decode(response),)
                    ### /DEBUGGING ###
                    return self.decoder.decode(response)
                except DecodeError as e:
                    attempts += 1
                    error_msg = e.value
            else: #timeout
                attempts += 1
                error_msg = "waiting for response timed out"
                
        # attempts > 3, failure
        raise InterfaceError(error_msg)
        
    def tx_rx_decode_bin(self, msg_to_send):
        """transmit to the plane, recieve a response, and decode it.
        
        This should be used when decoding responses with binary arguments,
        in this case a random /r/n could appear, so a different decoding
        method must be used"""
        attempts = 0
        while (attempts < 3):
            # get and decode the message containing the length
            self.ser.write(msg_to_send)
            response1 = self.ser.readline()
            if response1:
                try:
                    length = self.decoder.decode_bin(response1)
                except DecodeError as e:
                    attempts += 1
                    error_msg = e.value
            else: #timeout
                attempts += 1
                error_msg = e.value
                
            # get and decode the message containing image data
            response2 = self.ser.read(length)
            if response2:
                try:
                    return self.decoder.decode_bin(response2)
                except DecodeError as e:
                    attempts += 1
                    error_msg = e.value
            else: #timeout
                attempts += 1
                error_msg = e.value
                
        # attempts > 3, failure
        raise InterfaceError(error_msg)
        
