#Target.py

class Target(object):
    """contains target attributes"""
    
    def __init__(self):
        """constructor"""
        
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
        self._number = 0
    
    def calculate_gps(self):
        self.latitude = "1234.12.12"
        self.longitude = "9876.98.98"
    
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
    
    def get_wordup(self):
        return self._wordup
    
    def set_wordup(self, value):
        self._wordup = value
    
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
