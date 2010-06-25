###############################################################################
#
# file: DebugInterface.py 
# author: Cogan Noll
# email: colgate360@gmail.com
# last modified: 2010
#
###############################################################################

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
    
    def toggle_power(self):
        """toggle power on and off for the camera"""
        pass
    
    def set_mode(self, mode):
        """set the mode for the camera (0 for storage, 1 for camera mode)"""
        pass
    
    def take_picture(self, picture_num):
        """snap a picture."""
        pass
    
    def toggle_record(self):
        """toggle recording on and off for the camera"""
        pass
    
    def pan(self, value):
        """set the pan servo to position (-180 to 180)"""
        pass

    def tilt(self, value):
        """set the pan servo to position (-45 to 45)"""
        pass
    
    #def resume_search(self):
    #    """have the camera resume it's search pattern."""
    #    pass
        
    #def lock_target(self, xa, ya):
    #    """lock onto a target given pixels xa and ya."""
    #    pass
        
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
        returns gps_x, gps_y, pan, tilt, yaw, pitch, roll, orientation, altitude"""
        return ["54.33", "65.44", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "100.0"]
               
    def request_size(self, picture_num, crop_num):
        """get the size of a crop"""
        return ["1500",]
        
    def download_segment(self, picture_num, crop_num, segment_num): 
        """download a segment of an image"""
        time.sleep(.01)
        return ["",]
    
    #def camera_zoom_in(self, increment):
    #    """have the camera zoom in."""
    #    return True

    #def camera_zoom_out(self, increment):
    #    """have the camera zoom out."""
    #    return True
                
    def ping(self):
        """ping the plane"""
        return True
