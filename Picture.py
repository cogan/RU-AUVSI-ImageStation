#Picture.py

from Crop import *

class Picture(object):
    """contains picture attributes and crop list"""
    
    def __init__(self):
        """constructor"""
        
        # mission relevant attributes
        self._latitude = "uncalculated"
        self._longitude = "uncalculated"
        self._shape = "unknown"
        self._alpha = "unknown"
        self._alphacolor = "unknown"
        self._color = "unknown"
        
        # various crops of pictures
        # we want to start with index 1, so we put an dud in crop_list[0]
        self.crop_list = [0]
        
    def add_crop(self):
        crop_num = len(self.crop_list)
        self.crop_list.append(Crop(name="crop_" + str(crop_num)))
        
        #return the number of the crop added
        return len(self.crop_list)-1
        
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
    
    latitude = property(get_latitude, set_latitude)
    longitude = property(get_longitude, set_longitude)
    shape = property(get_shape, set_shape)
    alpha = property(get_alpha, set_alpha)
    color = property(get_color, set_color)
    alphacolor = property(get_alphacolor, set_alphacolor)
