#Crop.py

import os
import math

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
        #various program relevent attributes
        self.name = name
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
