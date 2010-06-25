from Interface import *

class NoneInterface(Interface):
    """interface class to use when there is no connection selected."""
    
    #*
    #* Define Abstract functions (all should just raise exception)
    #*
    
    def toggle_power(self):
        """toggle power on and off for the camera"""
        raise InterfaceError("no interface selected")
    
    def set_mode(self, mode):
        """set the mode for the camera (0 for storage, 1 for camera mode)"""
        raise InterfaceError("no interface selected")
        
    def take_picture(self, picture_num):
        """snap a picture."""
        raise InterfaceError("no interface selected")
        
    def toggle_record(self):
        """toggle recording on and off for the camera"""
        raise InterfaceError("no interface selected")
    
    def pan(self, value):
        """set the pan servo to position (-180 to 180)"""
        raise InterfaceError("no interface selected")
            
    def tilt(self, value):
        """set the pan servo to position (-45 to 45)"""
        raise InterfaceError("no interface selected")
    
    #def resume_search(self):
    #    """have the camera resume it's search pattern."""
    #    raise InterfaceError("no interface selected")
        
    #def lock_target(self, xa, ya):
    #    """lock onto a target given pixels xa and ya."""
    #    raise InterfaceError("no interface selected")
        
    def download_to_flc(self):
        """download pictures form the camera memory onto the
        flight linux computer."""
        raise InterfaceError("no interface selected")

    def generate_crop(self, picture_num, xa, ya, xb, yb):
        """generate a crop of an image given the image number,
        xa, ya, xb, and yb. which represent the top left and bottom right
        corners of a rectangle."""
        raise InterfaceError("no interface selected")
        
    def request_info(self, picture_num):
        """get all positional info about a picture
        returns gps_x, gps_y, pan, tilt, yaw, pitch, roll, orientation, altitude"""
        raise InterfaceError("no interface selected")
        
    def request_size(self, picture_num, crop_num):
        """get the size of a crop"""
        raise InterfaceError("no interface selected")
        
    def download_segment(self, picture_num, crop_num, segment_num): 
        """download a segment of an image"""
        raise InterfaceError("no interface selected")
    
    #def camera_zoom_in(self, increment):
    #    """have the camera zoom in."""
    #    raise InterfaceError("no interface selected")

    #def camera_zoom_out(self, increment):
    #    """have the camera zoom out."""
    #    raise InterfaceError("no interface selected")
                
    def ping(self):
        """ping the plane"""
        return 0
