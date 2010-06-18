#DebugInterface.py

from Interface import *
from NmeaEncoder import *
from NmeaDecoder import *

import time
import subprocess

class FrameGrabberInterface(Interface):
    """interface class to use when debugging."""
    
    def __init__(self):
        """constructor"""
        print "Using the frame grabber interface"
        
        # fifo to communicate with mplayer
        self.fifo_name = "mplayer_fifo"
    
    #*
    #* Define Abstract functions
    #*
    
    def toggle_power(self):
        """toggle power on and off for the camera"""
        raise InterfaceError("This interface does not support that functionality")
    
    def set_mode(self, mode):
        """set the mode for the camera (0 for storage, 1 for camera mode)"""
        raise InterfaceError("This interface does not support that functionality")
    
    def take_picture(self, picture_num):
        """snap a picture."""
        subprocess.Popen(['./mplayer_screenshot.sh', self.fifo_name])
    
    def toggle_record(self):
        """toggle recording on and off for the camera"""
        raise InterfaceError("This interface does not support that functionality")
    
    def pan(self, value):
        """set the pan servo to position (-180 to 180)"""
        raise InterfaceError("This interface does not support that functionality")

    def tilt(self, value):
        """set the pan servo to position (-45 to 45)"""
        raise InterfaceError("This interface does not support that functionality")
    
    #def resume_search(self):
    #    """have the camera resume it's search pattern."""
    #    pass
        
    #def lock_target(self, xa, ya):
    #    """lock onto a target given pixels xa and ya."""
    #    pass
        
    def download_to_flc(self):
        """download pictures form the camera memory onto the
        flight linux computer."""
        raise InterfaceError("This interface does not support that functionality")

    def generate_crop(self, picture_num, xa, ya, xb, yb):
        """generate a crop of an image given the image number,
        xa, ya, xb, and yb. which represent the top left and bottom right
        corners of a rectangle."""
        raise InterfaceError("This interface does not support that functionality")
        
    def request_info(self, picture_num):
        """get all positional info about a picture
        returns gps_x, gps_y, pan, tilt, yaw, pitch, roll, orientation, altitude"""
        raise InterfaceError("This interface does not support that functionality")
               
    def request_size(self, picture_num, crop_num):
        """get the size of a crop"""
        raise InterfaceError("This interface does not support that functionality")
        
    def download_segment(self, picture_num, crop_num, segment_num): 
        """download a segment of an image"""
        raise InterfaceError("This interface does not support that functionality")

    
    #def camera_zoom_in(self, increment):
    #    """have the camera zoom in."""
    #    return True

    #def camera_zoom_out(self, increment):
    #    """have the camera zoom out."""
    #    return True
                
    def ping(self):
        """ping the plane"""
        pass