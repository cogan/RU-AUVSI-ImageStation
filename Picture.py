#Picture.py

class Picture:
    """contains picture attributes and crop list"""
    
    def __init__(self, \
            gps=None, \
            orientation=None, \
            shape=None, \
            alphanumeric=None, \
            border_color=None, \
            alphanumeric_color=None):
        """constructor"""
        
        #mission relevant attributes
        self.gps = gps
        self.orientation = orientation
        self.shape = shape
        self.alphanumeric = alphanumeric
        self.border_color = border_color
        self.alphanumeric_color = alphanumeric_color
        
        #various crops of pictures
        # we want to start with index 1, so we put an dud in crop_list[0]
        self.crop_list = [0]
