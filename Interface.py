#Interface.py

from InterfaceError import *

class Interface:
    """abstract class that defines methods to communicate with the plane.
    It uses the syntax methodname(self): abstract defined in the Python IAQ.
    This will raise a NameError if the method is not defined"""
    
    def take_picture(self, picture_num):
        """snap a picture."""
        abstract
        
    def resume_search(self):
        """have the camera resume it's search pattern."""
        abstract
        
    def lock_target(self, xa, ya):
        """lock onto a target given pixels xa and ya."""
        abstract
        
    def download_to_flc(self):
        """download pictures form the camera memory onto the
        flight linux computer."""
        abstract

    def generate_crop(self, picture_num, xa, ya, xb, yb):
        """generate a crop of an image given the image number,
        xa, ya, xb, and yb. which represent the top left and bottom right
        corners of a rectangle."""
        abstract
        
    def request_info(self, picture_num):
        """get all positional info about a picture
        returns gps_x, gps_y, pan, tilt, yaw, pitch, roll, orientation"""
        abstract
        
    def request_size(self, picture_num, crop_num):
        """get the size of a crop."""
        abstract
        
    def download_image(self, picture_num, crop_num, segment_num):
        """download a segment of an image."""
        abstract
    
    def camera_zoom_in(self, increment):
        """have the camera zoom in."""
        abstract

    def camera_zoom_out(self, increment):
        """have the camera zoom out."""
        abstract
        
    def camera_pan_left(self, increment):
        """have the camera pan left."""
        abstract
        
    def camera_pan_right(self, increment):
        """have the camera pan right."""
        abstract
        
    def camera_tilt_up(self, increment):
        """have the camera tilt upwards."""
        abstract
        
    def camera_tilt_down(self, increment):
        """have the camera tilt down."""
        abstract
    
    def camera_reset(self):
        """have the camera set itself to its home coordinates"""
        abstract

    def ping(self):
        """ping the plane"""
        abstract
