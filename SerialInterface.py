#SerialInterface.py

from Interface import *
from NmeaEncoder import *
from NmeaDecoder import *

import serial
import time

class SerialInterface(Interface):
    """interface class to use when there is no connection selected."""
    
    def __init__(self, port="/dev/ttyUSB0", baud=9600):
        """constructor"""
        
        #indicates whether there is a connection on the selected port
        self.enabled = False
        
        #create a connection on the selected port
        self.initialize_connection(port, baud)
        
        #try to open on ttyUSB1 if ttyUSB0 fails
        if self.enabled == False:
            self.initialize_connection("/dev/ttyUSB1", baud)
        
        #talker identifier = IS (ImageStation)
        self.identifier = "IS"
        
        #set encoder and decoder
        self.encoder = NmeaEncoder(self.identifier)
        self.decoder = NmeaDecoder()
        
        # FOR REFERENCE: Dictionary of sentence identifiers
        # 
        # "toggle_power" : "CPW"
        # "set_mode" : CMO"
        # "take_picture" : "CPT"
        # "toggle_record: "CRC"
        # "pan" : "CPA"
        # "tilt" : "CTI"
        # "resume_search" : ""
        # "lock_target" : "",
        # "acknowledge download_to_flc" : "FLC"
        # "download to FLC complete" : "FLD"
        # "generate_crop" : "CRP"
        # "request_info" : "INF"
        # "request_size" : "PSZ"
        # "download_segment" : "DPC"
        # "ping" : "PNG"
    
    #*
    #* Define Abstract functions
    #*

    def toggle_power(self):
        """toggle power on and off for the camera"""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("CPW")
                return self.tx_rx_decode(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")
    
    def set_mode(self, mode):
        """set the mode for the camera (0 for storage, 1 for camera mode)"""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("CMO", mode)
                return self.tx_rx_decode(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")
    
    def take_picture(self, picture_num):
        """snap a picture."""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("CPT", picture_num)
                return self.tx_rx_decode(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")
    
    def toggle_record(self):
        """toggle recording on and off for the camera"""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("CRC")
                return self.tx_rx_decode(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")
    
    def pan(self, value):
        """set the pan servo to position (-180 to 180)"""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("CPA", value)
                return self.tx_rx_decode(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")

    def tilt(self, value):
        """set the pan servo to position (-45 to 45)"""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("CTI", value)
                return self.tx_rx_decode(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")
    
    #def resume_search(self):
    #    """have the camera resume it's search pattern."""
    #    if self.enabled == True:
    #        try:
    #            msg_to_send = self.encoder.encode("")
    #            return self.tx_rx_decode(msg_to_send)
    #        except InterfaceError as e:
    #            raise InterfaceError(e.value)
    #    else:
    #        raise InterfaceError("no serial connection")
        
    #def lock_target(self, xa, ya):
    #    """lock onto a target given pixels xa and ya."""
    #    if self.enabled == True:
    #        try:
    #            msg_to_send = self.encoder.encode("", xa, ya)
    #            return self.tx_rx_decode(msg_to_send)
    #        except InterfaceError as e:
    #            raise InterfaceError(e.value)
    #    else:
    #        raise InterfaceError("no serial connection")
        
    def download_to_flc(self):
        """download pictures form the camera memory onto the
        flight linux computer."""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("FLC")
                self.tx_rx_decode(msg_to_send)
                return self.rx_decode()
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")

    def generate_crop(self, picture_num, xa, ya, xb, yb):
        """generate a crop of an image given the image number,
        xa, ya, xb, and yb. which represent the top left and bottom right
        corners of a rectangle."""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("CRP", picture_num, \
                                                    xa, ya, xb, yb)
                return self.tx_rx_decode(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")
        
    def request_info(self, picture_num):
        """get all positional info about a picture
        returns gps_x, gps_y, pan, tilt, yaw, pitch, roll, orientation, altitude"""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("INF", picture_num)
                return self.tx_rx_decode(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")
        
    def request_size(self, picture_num, crop_num):
        """get the size of a crop"""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("PSZ", picture_num, crop_num)
                return self.tx_rx_decode(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")
        
    def download_segment(self, picture_num, crop_num, segment_num): 
        """download a segment of an image"""
        if self.enabled == True:
            try:
                msg_to_send = self.encoder.encode("DPC", picture_num, \
                                                    crop_num, segment_num)
                return self.tx_rx_decode_bin(msg_to_send)
            except InterfaceError as e:
                raise InterfaceError(e.value)
        else:
            raise InterfaceError("no serial connection")

    #def camera_zoom_in(self, increment):
    #    """have the camera zoom in."""
    #    if self.enabled == True:
    #        try:
    #            msg_to_send = self.encoder.encode("CZI", increment)
    #            return self.tx_rx_decode(msg_to_send)
    #        except InterfaceError as e:
    #            raise InterfaceError(e.value)
    #    else:
    #        raise InterfaceError("no serial connection")

    #def camera_zoom_out(self, increment):
    #    """have the camera zoom out."""
    #    if self.enabled == True:
    #        try:
    #            msg_to_send = self.encoder.encode("CZO", increment)
    #            return self.tx_rx_decode(msg_to_send)
    #        except InterfaceError as e:
    #            raise InterfaceError(e.value)
    #    else:
    #        raise InterfaceError("no serial connection")
                
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
    
    def initialize_connection(self, port, baud):
        """try to create a connection on the specified serial port."""
        try:
            self.ser = serial.Serial(port)
            self.ser.baudrate = baud
            self.ser.bytesize = 8
            self.ser.stopbits = 1
            self.ser.rtscts = 1
            self.ser.timeout = 1
            self.enabled = True
            print "serial connection successful on port %s at %d baud" % (port, baud,)
        except serial.serialutil.SerialException as e:
            self.enabled = False
            print "serial connection failed on port %s" % (port,)
            print e

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
                    #flush the serial line
            else: #timeout
                attempts += 1
                error_msg = "waiting for response timed out"
                #flush the serial line
                
        # attempts > 3, failure
        raise InterfaceError(error_msg)
        
    def tx_rx_decode_bin(self, msg_to_send):
        """transmit to the plane, recieve a response, and decode it.
        
        This should be used when decoding responses with binary arguments,
        in this case a random /r/n could appear, so a different decoding
        method must be used"""
        attempts = 0
        while (attempts < 3):
            length = 0
            # get and decode the message containing the length
            self.ser.write(msg_to_send)
            ### DEBUGGING ###
            print "sending msg: %s" % (msg_to_send,)
            ### /DEBUGGING ###
            response1 = self.ser.readline()
            if response1:
                ### DEBUGGING ###
                print "received msg1: %s" % (response1,)
                ### /DEBUGGING ###
                try:
                    ### DEBUGGING ###
                    print "returned args array: %s" % (self.decoder.decode(response1),)
                    ### /DEBUGGING ###
                    (length_str,) = self.decoder.decode(response1)
                    length = int(length_str)
                except DecodeError as e:
                    attempts += 1
                    error_msg = e.value
                    #flush the serial line
            else: #timeout
                attempts += 1
                error_msg = "waiting for response timed out"
                #flush the serial line
                
            # get and decode the message containing image data
            response2 = self.ser.read(length)
            if response2:
                ### DEBUGGING ###
                print "received msg2: %s" % (response2,)
                ### /DEBUGGING ###
                try:
                    ### DEBUGGING ###
                    print "returned args array: %s" % (repr(self.decoder.decode_bin(response2)),)
                    ### /DEBUGGING ###
                    return self.decoder.decode_bin(response2)
                except DecodeError as e:
                    attempts += 1
                    error_msg = e.value
                    #flush the serial line
            else: #timeout
                attempts += 1
                error_msg = "waiting for response timed out"
                #flush the serial line
                
        # attempts > 3, failure
        raise InterfaceError(error_msg)
        
    def rx_decode(self):
        """recieve a response and decode it."""
        print "in rx_decode"
        attempts = 0
        MAX_ATTEMPTS = 999
        while (attempts < MAX_ATTEMPTS):
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
                    #flush the serial line
            else: #timeout
                attempts += 1
                error_msg = "waiting for response timed out"
                #flush the serial line
                
        # attempts > 3, failure
        raise InterfaceError(error_msg)
        
