#Picture.py

from Crop import *
from Camera import *

class Picture(object):
    """contains picture attributes and crop list"""
    
    def __init__(self):
        """constructor"""
        
        # mission relevant attributes
        # TODO: move these to target class
        self._latitude = "uncalculated"
        self._longitude = "uncalculated"
        self._shape = "unknown"
        self._alpha = "unknown"
        self._alphacolor = "unknown"
        self._color = "unknown"
        self._orientation = "unknown"
        
        # "intermediate" attributes
        self._gps_x = 0.0
        self._gps_y = 0.0
        self._pan = 0.0
        self._tilt = 0.0
        self._yaw = 0.0
        self._pitch = 0.0
        self._roll = 0.0
        self._plane_orientation = 0.0
        self._altitude = 0.0
        self._pan = 0.0
        
        # representation of camera used to take picture
        self.bloggie = Camera()
        self.bloggie.set_params(fc1 = 3224.35414, \
                                fc2 = 3202.87322, \
                                cc1 = 1396.72711, \
                                cc2 = 975.48995, \
                                alpha_c = 0.0)
        
        # various crops of pictures
        # we want to start with index 1, so we put an dud in crop_list[0]
        self.crop_list = [0]
        
        # resolution fields
        self.x_thumbnail_resolution = 800
        self.y_thumbnail_resolution = 600
        self.x_resolution = 2400
        self.y_resolution = 1800
        
    def add_crop(self, x_offset=0, y_offset=0):
        """append a new crop to the end of the crop list"""
        crop_num = len(self.crop_list)
        self.crop_list.append(Crop(self, x_offset=x_offset, y_offset=y_offset, name="crop_" + str(crop_num)))
        
        #return the number of the crop added
        return len(self.crop_list)-1
        
    def get_crop(self, crop_num):
        """return the crop with matching crop num"""
        return self.crop_list[crop_num]
        
    def num_crops(self):
        return len(self.crop_list)
    
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
        
    def get_gps_x(self):
        return self._gps_x
    
    def set_gps_x(self, value):
        self._gps_x = value
        
    def get_gps_y(self):
        return self._gps_y
    
    def set_gps_y(self, value):
        self._gps_y = value
        
    def get_pan(self):
        return self._pan
    
    def set_pan(self, value):
        self._pan = value
        
    def get_tilt(self):
        return self._tilt
    
    def set_tilt(self, value):
        self._tilt = value
        
    def get_yaw(self):
        return self._yaw
    
    def set_yaw(self, value):
        self._yaw = value

    def get_pitch(self):
        return self._pitch
    
    def set_pitch(self, value):
        self._pitch = value
        
    def get_roll(self):
        return self._roll
    
    def set_roll(self, value):
        self._roll = value
        
    def get_plane_orientation(self):
        return self._plane_orientation
    
    def set_plane_orientation(self, value):
        self._plane_orientation = value
        
    def get_altitude(self):
        return self._altitude
    
    def set_altitude(self, value):
        self._altitude = value 
    
    # picture attributes
    latitude = property(get_latitude, set_latitude)
    longitude = property(get_longitude, set_longitude)
    shape = property(get_shape, set_shape)
    alpha = property(get_alpha, set_alpha)
    color = property(get_color, set_color)
    alphacolor = property(get_alphacolor, set_alphacolor)
    orientation = property(get_orientation, set_orientation)
    
    # intermediate attributes
    gps_x = property(get_gps_x, set_gps_x)
    gps_y = property(get_gps_y, set_gps_y)
    pan = property(get_pan, set_pan)
    tilt = property(get_tilt, set_tilt)
    yaw = property(get_yaw, set_yaw)
    pitch = property(get_pitch, set_pitch)
    roll = property(get_roll, set_roll)
    plane_orientation = property(get_plane_orientation, set_plane_orientation)
    altitude = property(get_altitude, set_altitude)
