#Crop.py

import os
import math
from Target import *

# TODO: i think the crop needs to be passed its parent (the picture)
class Crop:
    """image"""
    
    def __init__(self, \
            name = "", \
            available = False, \
            completed = False, \
            inqueue = False, \
            segments_downloaded = 0, \
            segments_total = 0, \
            size = 0, \
            path = ""):
        """constructor"""
        
        # various program relevent attributes
        self.name = name
        self.available = available
        self.completed = completed
        self.inqueue = inqueue
        self.size = size
        self.segments_downloaded = segments_downloaded
        self.segments_total = segments_total
        self.path = path
        
        # resolution attributes
        self.x_offset = 0
        self.y_offset = 0
        self.x_full_resolution = 2400
        self.y_full_resolution = 1800
        self.x_thumbnail_resolution = 800
        self.y_thumbnail_resolution = 600
        
        self.target = None
        
        #picture data
        self.segment_size = 250

    def calculate_total_segments(self):
        self.segments_total = math.ceil(float(self.size)/float(self.segment_size))  
        
    def total_segments(self):
        return math.ceil(float(self.size)/float(self.segment_size))
        
    def save_segment(self, segment_data, segment_num):
        
        #make sure the file exists
        fout = open(self.path, 'a')
        fout.close()
        
        #save the data (you can't use seek with 'a')
        fout = open(self.path, 'r+')
        fout.seek(segment_num * self.segment_size)
        fout.write(segment_data)
        fout.truncate(fout.tell())
        fout.close()
        
        #update info
        self.segments_downloaded = self.segments_downloaded + 1;
        
    def get_percent_complete(self):
        percent_complete = \
            math.floor( (self.segments_downloaded*100) / (self.total_segments()) )
        return percent_complete
        
    def calculate_real_coordinates(crop_x, crop_y):
        """ takes the actual coordinates on the crop and returns the
            correspondin coordinates on the full size image"""
        real_x = int(crop_x * (x_full_resolution / x_thumbnail_resolution))
        real_y = int(crop_y * (y_full_resolution / y_thumbnail_resolution))
        return (real_x, real_y)
    
    def set_target(self, crop_x, crop_y):
        self.target = Target(self)
        
        # need these for rendering the target
        self.target.x_coord = crop_x
        self.target.y_coord = crop_y
        
        # need this stuff for calculating latitude and longitude
        # *** needs pitch, yaw, roll, pan, tilt from picture
        # *** needs intrinsic camera matrix (should be in picture)
        # for these use something like self.parent.yaw, self.parent.pitch etc.
        # *** needs to determine real coordinates from crop coordinates
        # for this define a seperate function.
        # e.g. (real_x, real_y) = self.calculate_real_coordinates(
        #                                        crop_x + self.x_offset, 
        #                                        crop_y + self.y_offset)
        
        #TODO: change this to take the required args
        self.target.calculate_gps()
