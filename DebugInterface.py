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
        return [1000,]
        
    def download_segment(self, picture_num, crop_num, segment_num): 
        """download a segment of an image"""
        time.sleep(.01)
        return ["",]
        
    def camera_pan_left(self, increment):
        """have the camera pan left."""
        return True
        
    def camera_pan_right(self, increment):
        """have the camera pan right."""
        return True
        
    def camera_tilt_up(self, increment):
        """have the camera tilt upwards."""
        return True
        
    def camera_tilt_down(self, increment):
        """have the camera tilt down."""
        return True
    
    def camera_reset(self):
        """have the camera set itself to it's home coordinates"""
        return True
                
    def ping(self):
        """ping the plane"""
        return True
