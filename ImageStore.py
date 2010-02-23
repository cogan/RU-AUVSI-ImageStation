#ImageStore.py

from Picture import *

class ImageStore:
    """Store locations for Images"""
    
    def __init__(self):
        self.picture_list = []
        self.picture_count = 0
        self.project_path = "/tmp"
    
    def set_project_path(self, path):
        if path[-1] != '/':
            path += '/'
        if not os.path.isdir(path):
            #make the directory
            os.mkdir(path)
        self.project_path = path
    
    def add_picture(self):
        self.picture_list.append(Picture())
        self.picture_list[-1].add_crop()
        self.picture_list[-1].crop_list[1].name = "thumb_" + str(self.picture_count)
        self.picture_list[-1].crop_list[1].path = \
                self.project_path + "pic" + str(self.picture_count) + "crop1.jpg"
        self.picture_count += 1
        
        #return the number of the pic added
        return self.picture_count-1
    
    def get_picture(self, picture_num):
        return self.picture_list[picture_num]
    
    def get_crop(self, picture_num, crop_num):
        return self.picture_list[picture_num].crop_list[crop_num]
