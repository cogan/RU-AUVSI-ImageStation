#Crop.py

import os
import math
from Target import *

class Crop:
    """image"""
    
    def __init__(self, \
            picture, \
            x_offset = 0, \
            y_offset = 0, \
            name = "", \
            available = False, \
            completed = False, \
            inqueue = False, \
            segments_downloaded = 0, \
            segments_total = 0, \
            size = 0, \
            path = ""):
        """constructor"""
        
        # the picture this crop belongs to
        self.picture = picture
        
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
        self.x_offset = x_offset
        self.y_offset = y_offset
        
        self.target = None
        
        #picture data
        self.segment_size = 250

    def set_for_redownload(self):
        """reset crop properties for redownloading"""
        self.completed = False
        self.inqueue = False
        self.segments_downloaded = 0
        self.segments_total = 0
        self.size = 0
        self.target = None

    def set_for_manual(self):
        """set crop to be completed for manually picture dragging"""
        self.available = True
        self.completed = True
        self.segments_downloaded = 1
        self.segments_total = 1
        self.size = self.segment_size
        
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
        if self.total_segments() == 0:
            return 0
        else:
            percent_complete = \
                math.floor( (self.segments_downloaded*100) / (self.total_segments()) )
            return percent_complete
        
    def calculate_real_coordinates(self, crop_x, crop_y):
        """ takes the actual coordinates on the crop and returns the
            correspondin coordinates on the full size image"""
        real_x = int((self.x_offset + crop_x) * (self.picture.x_resolution / self.picture.x_thumbnail_resolution))
        real_y = int((self.y_offset + crop_y) * (self.picture.y_resolution / self.picture.y_thumbnail_resolution))
        return (real_x, real_y)
    
    def set_target(self, crop_x, crop_y):
        self.target = Target(self)
        
        # need these for rendering the target
        self.target.x_coord = crop_x
        self.target.y_coord = crop_y
        
        # need this stuff for calculating latitude and longitude
        # * needs pitch, yaw, roll, pan, tilt from picture, etc.
        gps_x = self.picture.gps_x
        gps_y = self.picture.gps_y
        pan = self.picture.pan
        tilt = self.picture.tilt
        yaw = self.picture.yaw
        pitch = self.picture.pitch
        roll = self.picture.roll
        plane_orientation = self.picture.plane_orientation
        altitude = self.picture.altitude
        
        # * needs intrinsic camera matrix (should be in picture)
        # -> in picture constructor put a bloggie = Camera() part
        # -> right now all pictures should use the default image size of
        #    fully zoomed out, and the corresponding intrinsic params.
        #    If this were to change the image station would have to get
        #    the zoom level and use it to calculate new intrinsic params
        M_int = self.picture.bloggie.get_intrinsic_matrix()
        
        # * needs to determine real coordinates from crop coordinates
        # -> for this define a seperate function.
        # -> e.g. (real_x, real_y) = self.calculate_real_coordinates(
        #                                        crop_x + self.x_offset, 
        #                                        crop_y + self.y_offset)
        #
        # *** to get x_offset and y_offset
        # --> look at '_execute_generate_crop' and make it so xa and ya are stored
        (real_x, real_y) = self.calculate_real_coordinates(crop_x, crop_y)
        print "crop_coords are x: %d, y%d" % (crop_x, crop_y)
        print "real coords are x: %d, y%d" % (real_x, real_y,)
        # FINALLY: pass all this info to the calculate_gps function, which
        # will do matrix mults and math described in the blue notebook
        #
        self.target.calculate_gps(M_int, real_x, real_y, gps_x, gps_y, \
                pan, tilt, yaw, pitch, roll, plane_orientation, altitude)
