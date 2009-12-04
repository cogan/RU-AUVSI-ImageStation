#Crop.py

import os

class Crop:
    """image"""
    
    def __init__(self, \
            available = False, \
            completed = False, \
            inqueue = False, \
            segments_downloaded = 0, \
            size = 0, \
            path = ""):
        """constructor"""
        #various program relevent attributes
        self.available = available
        self.completed = completed
        self.inqueue = inqueue
        self.size = size
        self.segments_downloaded = segments_downloaded
        self.path = path
        
        #picture data
        self.segment_size = 250
        
    def total_segments(self):
        return math.ceil(float(self.size)/float(self.segment_size))
        
    def save_segment(segment_data):
        #save the data
        fout = open(self.path, 'wb')
        fout.write(segment_data)
        fout.close
        
        #update info
        segments_downloaded = segments_downloaded + 1;
