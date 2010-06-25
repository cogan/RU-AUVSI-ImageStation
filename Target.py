###############################################################################
#
# file: Target.py 
# author: Cogan Noll
# email: colgate360@gmail.com
# last modified: 2010
#
###############################################################################

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
    
    def calculate_gps(self, M_int, x_im, y_im, gps_x, gps_y, pan, tilt, \
                        yaw, pitch, roll, plane_orientation, altitude):
        
        if 0:
            # TODO: implement this code
            #
            # get the angles of the target in the camera view
            #  ________________
            # |         x      |
            # |       ---->    |
            # |     y |        |
            # |       \/       |
            # |________________|
            #
            M_int_inv = M_int.I
            p_im = matrix([ [x_im] ,\
                            [y_im] ,\
                            [1   ] ])
            
            p_c = M_int_inv * p_im
            f = M_int[0,0]
            p_c = p_c * f
            
            angle_y = math.atan( p_c[1,0] / p_c[2,0] )
            angle_x = math.atan( p_c[0,0] / p_c[2,0] )
            
            #
            # solve for Z using trig
            #
            
            Z = altitude
            
            #
            # multiply p_c by Z to get P_c
            # PS if at this point you think my notation is confusing... too bad.
            #
            
            # TODO: change this code to account for slanted landscape
            P_c = p_c * (Z / f)
            P_c = matrix([[ P_c[0,0] ],\
                          [ P_c[1,0] ],\
                          [ P_c[2,0] ],\
                          [ 1        ]])
            
            #
            # determine transformation matrix M_ext
            #
            #  M_ext = wMc= [   R   T ]
            #  camera wrt W [ 0 0 0 1 ]
            #
            # T = gps coords of camera (plane)
            # R = rotation matrix
            
            #
            # Obtain R
            #
            
            # Start with coordinate system oriented with GPS
            # x is North (longitude), y is East (latitude), z is downward (hell)
            
            # 1) rotate about Z axis by the heading to orient the system
            theta_heading = plane_orientation
            R_orient = matrix([[ math.cos(theta_heading), -math.sin(theta_heading), 0 ],\
                               [ math.sin(theta_heading),  math.cos(theta_heading), 0 ],\
                               [ 0,                        0,                       1 ]])
            
            # 2) rotate the system for yaw, pitch, and roll
            theta_yaw = yaw
            R_yaw = matrix([[ math.cos(theta_yaw), -math.sin(theta_yaw), 0 ],\
                            [ math.sin(theta_yaw),  math.cos(theta_yaw), 0 ],\
                            [ 0,                    0,                   1 ]])
            
            theta_pitch = pitch
            R_pitch = matrix([[  math.cos(theta_pitch), 0, math.sin(theta_pitch)],\
                              [  0,                     1, 0                    ],\
                              [ -math.sin(theta_pitch), 0, math.cos(theta_pitch)]])
            
            theta_roll = roll
            R_roll = matrix([[ 1, 0,                     0                    ],\
                             [ 0, math.cos(theta_roll), -math.sin(theta_roll) ],\
                             [ 0, math.sin(theta_roll),  math.cos(theta_roll) ]])
            
            # 3) rotate the system about Z to align with the camera frame
            # x goes left to right across the image, y goes down the image, z into
            # fuck i wrote this down somewhere, i believe its a 90 degree rotation
            theta_image = 0
            R_image = matrix([[ math.cos(theta_image), -math.sin(theta_image), 0 ],\
                              [ math.sin(theta_image),  math.cos(theta_image), 0 ],\
                              [ 0,                      0,                     1 ]])
            
            # 4) rotate about Z to account for pan
            theta_pan = pan
            R_pan = matrix([[ math.cos(theta_pan), -math.sin(theta_pan), 0 ],\
                            [ math.sin(theta_pan),  math.cos(theta_pan), 0 ],\
                            [ 0,                    0,                   1 ]])
            
            # 5) rotate about X to account for tilt
            theta_tilt = tilt
            R_tilt = matrix([[ 1, 0,                  0                 ],\
                          [ 0, math.cos(theta_tilt), -math.sin(theta_tilt) ],\
                          [ 0, math.sin(theta_tilt),  math.cos(theta_tilt) ]])
            
            R = R_tilt * R_pan * R_image * R_roll * R_pitch * R_yaw * R_orient
    
            #
            # Obtain T
            #
    
            T = matrix([[  gps_x    ],\
                        [  gps_y    ],\
                        [ -altitude ]])
    
            M_ext = matrix([[ R[0,0], R[0,1], R[0,2], T[0,0] ],\
                            [ R[1,0], R[1,1], R[2,1], T[1,0] ],\
                            [ R[2,0], R[2,1], R[2,2], T[2,0] ],\
                            [ 0,      0,      0,      1      ]])
            
            P_gps = M_ext * P_c        
            
        #
        # Convert P_gps into latitude and longitude in proper format
        #
            
        self.latitude = self.gps_lat_dec2dms(gps_x)
        self.longitude = self.gps_long_dec2dms(gps_y)

    def gps_lat_dec2dms(self, gps_decimal):
        gps_dms_str = ""
        if (gps_decimal < 0):
            gps_dms_str += "W"
        else:
            gps_dms_str += "E"
        
        gps_decimal_abs = math.fabs(gps_decimal * 1000000.0)
        
        degrees = int(math.floor(gps_decimal_abs/1000000.0))
        gps_dms_str += "%02d" % (degrees,)
        gps_dms_str += ' '
        
        minutes = int(math.floor(((gps_decimal_abs/1000000.0) - math.floor(gps_decimal_abs/1000000.0)) * 60.0))
        gps_dms_str += "%02d" % (minutes,)
        gps_dms_str += ' '
        
        seconds = math.floor(((((gps_decimal_abs/1000000.0) - math.floor(gps_decimal_abs/1000000.0)) * 60.0) - math.floor(((gps_decimal_abs/1000000.0) - math.floor(gps_decimal_abs/1000000.0)) * 60.0)) * 100000.0) * 60.0/100000.0
        gps_dms_str += "%.3f" % (seconds,)
        
        return gps_dms_str
    
    def gps_long_dec2dms(self, gps_decimal):
        gps_dms_str = ""
        if (gps_decimal < 0):
            gps_dms_str += "S"
        else:
            gps_dms_str += "N"
        
        gps_decimal_abs = math.fabs(gps_decimal * 1000000.0)
        
        degrees = int(math.floor(gps_decimal_abs/1000000.0))
        gps_dms_str += "%02d" % (degrees,)
        gps_dms_str += ' '
        
        minutes = int(math.floor(((gps_decimal_abs/1000000.0) - math.floor(gps_decimal_abs/1000000.0)) * 60.0))
        gps_dms_str += "%02d" % (minutes,)
        gps_dms_str += ' '
        
        seconds = math.floor(((((gps_decimal_abs/1000000.0) - math.floor(gps_decimal_abs/1000000.0)) * 60.0) - math.floor(((gps_decimal_abs/1000000.0) - math.floor(gps_decimal_abs/1000000.0)) * 60.0)) * 100000.0) * 60.0/100000.0
        gps_dms_str += "%.3f" % (seconds,)
        
        return gps_dms_str
        
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
        target_str += "\t"
        
        # Field 2:  Latitude in the following format, first character N or S, 
        # two digit degrees (use leading zeros if necessary), followed by space 
        # two digit minutes, followed by space, two digit seconds followed by 
        # decimal point and up to 3 digits (thousandths of a second)
        target_str += self.latitude
        target_str += "\t"
        
        # Field 3:  Longitude in the following format, first character E or W,
        # three digit degrees (use leading zeros if necessary), followed by 
        # space, two digit minutes, followed by space, two digit seconds 
        # followed by decimal point and up to 3 digits (thousandths of a secon)
        target_str += self.longitude
        target_str += "\t"
        
        # Field 4:  Target orientation, up to two characters:  
        # N, NE, E, SE, S, SW, W, NW
        target_str += self.orientation
        target_str += "\t"
                
        # Field 5:  Target shape, list geometric shape as appropriate:
        target_str += self.shape
        target_str += "\t"
        
        # Field 6:  Target color, as appropriate.
        target_str += self.color
        target_str += "\t"
        
        # Field 7:  Alphanumeric, as appropriate
        target_str += self.alpha
        target_str += "\t"
        
        # Field 8:  Alphanumeric color, as appropriate
        target_str += self.alphacolor
        target_str += "\t"
        
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
