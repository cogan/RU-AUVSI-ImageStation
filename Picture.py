#Picture.py

from Crop import *

class Picture:
    """contains picture attributes and crop list"""
    
    def __init__(self):
        """constructor"""
        
        # mission relevant attributes
        self.location = ""
        self.orientation = ""
        self.shape = "triangle"
        self.alpha = ""
        self.alphacolor = ""
        self.color = ""
        
        # various crops of pictures
        # we want to start with index 1, so we put an dud in crop_list[0]
        self.crop_list = [0]
    
    def get_title(self):
        return "it works!"
    
    def set_title(self, title):
        pass
        
    def add_crop(self):
        self.crop_list.append(Crop())
        
        #return the number of the crop added
        return len(self.crop_list)-1
        
    location = property(get_title, set_title)
    orientation = None
    shape = None
    alpha = None
    color = None
    alphacolor = None
