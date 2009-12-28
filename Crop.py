#Crop.py

import os
import math

class Crop:
    """image"""
    
    def __init__(self, \
            available = False, \
            completed = False, \
            inqueue = False, \
            segments_downloaded = 0, \
            segments_total = 0, \
            size = 0, \
            path = ""):
        """constructor"""
        #various program relevent attributes
        self.available = available
        self.completed = completed
        self.inqueue = inqueue
        self.size = size
        self.segments_downloaded = segments_downloaded
        self.segments_total = segments_total
        self.path = path
        
        #picture data
        self.segment_size = 250

    def calculate_total_segments(self):
        self.segments_total = math.ceil(float(self.size)/float(self.segment_size))  
        
    def total_segments(self):
        return math.ceil(float(self.size)/float(self.segment_size))
        
    def save_segment(self, segment_data):
        #save the data
        fout = open(self.path, 'wb')
        fout.write(segment_data)
        fout.close
        
        #update info
        self.segments_downloaded = self.segments_downloaded + 1;
