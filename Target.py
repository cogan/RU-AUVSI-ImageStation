#Target.py

import os.path
from numpy import matrix
import math

class Target(object):
    """contains target attributes"""
    
    def __init__(self, crop):
        """constructor"""
        
        # the crop that this target belongs to
        self.crop = crop
        
        # mission relevant attributes
        self._latitude = "uncalculated"
        self._longitude = "uncalculated"
        self._shape = "unknown"
        self._alpha = "unknown"
        self._alphacolor = "unknown"
        self._color = "unknown"
        self._orientation = "unknown"
        
        # target location in image (pixels)
        self._x_coord = 0
        self._y_coord = 0
        
        # whether the target should be included
        self._included = False
        self._number = -1
    
    def calculate_gps(self):
        #self.latitude = "1234.12.12"
        #self.longitude = "9876.98.98"
        
        # things
        ## m_int
        ## x_im, y_im
        ## altitude
        ## tilt
        
        #
        # get the angles of the target in the camera view
        #  ________________
        # |         x      |
        # |       ---->    |
        # |     y |        |
        # |       \/       |
        # |________________|
        #
        #
        M_int_inv = M_int.I
        p_im = matrix([ [x_im] ,\
                        [y_im] ,\
                        [1   ] ])
        
        p = M_int_inv * p_im
        
        angle_y = math.atan( p[1,0] / p[2,0] )
        angle_x = math.atan( p[0,0] / p[2,0] )
        
        #
        # solve for Z using trig
        #
        # Z =   alt * cos(angle_y)
        #     -----------------------
        #     cos(tilt + (-angle_y) )
        #
        Z = ( altitude * math.cos(angle_y) ) / math.cos(tilt - angle_y)
        
        #
        # multiply p by Z to get P
        #
        
        P = p * Z
        
        #
        # determine transformation matrix M_ext
        #
        #  M_ext = wMc= [   R   T ]
        #  camera wrt W [ 0 0 0 1 ]
        #
        # T = gps coords of camera (plane)
        # 
        
        
    def format_info(self):
        """return target info in string format specified by 2010 UAVSI
        competition rules
        
        ex. 01 N30 35 34.123 W075 48 47.123 rectangle red A orange Img01.jpeg
        ex. 02 S34 00 12.345 E002 01 12.345 square orange 4 yellow pic02.jpeg"""
        target_str = ""
        
        # Field 1:  Target Number, two digits, starting at 01 
        # and increment by one for each additional target.
        if self.number < 10:
            target_str += "0" + str(self.number)
        else:
            target_str += str(self.number)
        target_str += " "
        
        # Field 2:  Latitude in the following format, first character N or S, 
        # two digit degrees (use leading zeros if necessary), followed by space 
        # two digit minutes, followed by space, two digit seconds followed by 
        # decimal point and up to 3 digits (thousandths of a second)
        target_str += self.latitude
        target_str += " "
        
        # Field 3:  Longitude in the following format, first character E or W,
        # three digit degrees (use leading zeros if necessary), followed by 
        # space, two digit minutes, followed by space, two digit seconds 
        # followed by decimal point and up to 3 digits (thousandths of a secon)
        target_str += self.longitude
        target_str += " "
        
        # Field 4:  Target orientation, up to two characters:  
        # N, NE, E, SE, S, SW, W, NW
        target_str += self.orientation
        target_str += " "
                
        # Field 5:  Target shape, list geometric shape as appropriate:
        target_str += self.shape
        target_str += " "
        
        # Field 6:  Target color, as appropriate.
        target_str += self.color
        target_str += " "
        
        # Field 7:  Alphanumeric, as appropriate
        target_str += self.alpha
        target_str += " "
        
        # Field 8:  Alphanumeric color, as appropriate
        target_str += self.alphacolor
        target_str += " "
        
        # Field 9:  File name of image (include extension)
        target_str += os.path.basename(self.crop.path)
        
        # return the completed string
        return target_str
    
    #*
    #* Get and set functions for basic properties
    #*
    
    def get_latitude(self):
        return self._latitude
    
    def set_latitude(self, value):
        self._latitude = value
        
    def get_longitude(self):
        return self._longitude
    
    def set_longitude(self, value):
        self._longitude = value
        
    def get_shape(self):
        return self._shape
    
    def set_shape(self, value):
        self._shape = value
    
    def get_alpha(self):
        return self._alpha
    
    def set_alpha(self, value):
        self._alpha = value
        
    def get_color(self):
        return self._color
    
    def set_color(self, value):
        self._color = value
        
    def get_alphacolor(self):
        return self._alphacolor
    
    def set_alphacolor(self, value):
        self._alphacolor = value
    
    def get_orientation(self):
        return self._orientation
    
    def set_orientation(self, value):
        self._orientation = value
        
    def get_x_coord(self):
        return self._x_coord
    
    def set_x_coord(self, value):
        self._x_coord = value
    
    def get_y_coord(self):
        return self._y_coord
    
    def set_y_coord(self, value):
        self._y_coord = value
    
    def get_included(self):
        return self._included
    
    def set_included(self, value):
        self._included = value
    
    def get_number(self):
        return self._number
    
    def set_number(self, value):
        self._number = value
    
    latitude = property(get_latitude, set_latitude)
    longitude = property(get_longitude, set_longitude)
    shape = property(get_shape, set_shape)
    alpha = property(get_alpha, set_alpha)
    color = property(get_color, set_color)
    alphacolor = property(get_alphacolor, set_alphacolor)
    orientation = property(get_orientation, set_orientation)
    x_coord = property(get_x_coord, set_x_coord)
    y_coord = property(get_y_coord, set_y_coord)
    included = property(get_included, set_included)
    number = property(get_number, set_number)
