#Communicator.py

#import required modules
import math
import sys
import os
import time

#import project related dependencies
from Subject import *
from SerialInterface import *
from NoneInterface import *
from DebugInterface import *
from ImageStore import *

class Communicator(Subject):
    """class for communicating with the airplane and storing airplane data"""
    
    def __init__(self):
        """constructor"""
        Subject.__init__(self)

        #these hold tuples that indicate the next command/request
        # to be issued.  The string is the function to be called, and the
        # dictionary contains the arguments (**kwargs)
        self.current_command = ("none", {})
        self.current_request = ("none", {})
        
        #storage of pictures
        self.image_store = ImageStore()
        self.image_store.set_project_path("/home/cogan/Desktop/ImageStationProject/")
        
        #set default interface to none
        #self.interface = SerialInterface("/dev/ttyUSB0", 9600)
        self.interface = DebugInterface()

    def set_interface(self, interface, **kwargs):
        """sets the interface used to communicate with the plane"""
        if interface == "serial":
            self.interface = SerialInterface(**kwargs)
        elif interface == "none":
            self.interface = NoneInterface()
        elif interface == "debug":
            self.interface = DebugInterface()

    #def get_image(pn, cn)

    #*
    #* Functions to be called by a "controller" to initiate Communicator actions
    #*

    def take_picture(self, **kwargs):
        """command the Communicator to make the plane take a picture.
        
        args:
        (none)"""
        self.current_command = ("_execute_take_picture", kwargs)
        
    def resume_search(self, **kwargs):
        """command the Communicator to make the plane to resume 
        its search path.
        
        args:
        (none)"""
        self.current_command = ("_execute_resume_search", kwargs)    
        
    def lock_target(self, **kwargs):
        """command the Communicator to make the plane seek a target.
        
        args: 
        xa, ya"""
        self.current_command = ("_execute_lock_target", kwargs)
        
    def download_to_flc(self, **kwargs):
        """command the Communicator to make the plane transfer pictures 
        from the camera memory stick to the flight linux computer.
        
        args:
        (none)"""
        self.current_command = ("_execute_download_to_flc", kwargs)
        
    def generate_crop(self, **kwargs):
        """command the Communicator to make the plane generate 
        a crop of an existing image based on pixels coordinates representing 
        two corners of a rectangle.
        
        args:
        picture_num, xa, ya, xb, yb"""
        self.current_command = ("_execute_generate_crop", kwargs)
        
    def download_image(self, **kwargs):
        """ command the Communicator to make the plane send down a 
        section of an image.
    
        args:
        picture_num, crop_num"""
        self.current_request = ("_execute_download_image", kwargs)

    def camera_reset(self, **kwargs):
        """command the Communicator to make the plane reset the camera.
        
        args:
        (none)"""
        self.current_command = ("_execute_camera_reset", kwargs)
        
    def camera_pan_left(self, **kwargs):
        """command the Communicator to pan camera left by increment.
        
        args:
        increment"""
        self.current_command = ("_execute_camera_pan_left", kwargs)
        
    def camera_pan_right(self, **kwargs):
        """command the Communicator to pan camera right by increment.
        
        args:
        increment"""
        self.current_command = ("_execute_camera_pan_right", kwargs)
        
    def camera_tilt_up(self, **kwargs):
        """command the Communicator to tilt camera up by increment.
        
        args:
        increment"""
        self.current_command = ("_execute_camera_tilt_up", kwargs)
        
    def camera_tilt_down(self, **kwargs):
        """command the Communicator to tilt camera down by increment.
        
        args:
        increment"""
        self.current_command = ("_execute_camera_tilt_down", kwargs)

    #*
    #* Private functions called by the Communicator to initiate commands
    #* through the selected 'interface' and relay data back to observers
    #*
    
    def _execute_take_picture(self, **kwargs):
        """command the plane to take a picture
        
        args:
        (none)"""
        
        #reset command flag / command acknowledged
        self.current_command = ("none", {})
        
        print "Communicator sending request to take picture"
        try:
            #send the number of the picture about to be taken for data checking
            self.interface.take_picture(self.image_store.picture_count)
            
            #add a new picture to image store
            pic_num = self.image_store.add_picture()
            
            self.notify("PICTURE_TAKEN", picture_num=pic_num)
            
        except InterfaceError as e:
            self.notify("INTERFACE_ERROR", \
                msg=e.value, \
                function=sys._getframe().f_code.co_name)
    
    def _execute_resume_search(self, **kwargs):
        """command the plane to go into search mode
        
        args:
        (none)"""
        
        #reset command flag / command acknowledged
        self.current_command = ("none", {})
        
        print "Communicator sending request to resume search"
        try:
            self.interface.resume_search()

            self.notify("SEARCH_RESUMED")
        except InterfaceError as e:
            self.notify("INTERFACE_ERROR", \
                msg=e.value, \
                function=sys._getframe().f_code.co_name)
        
    def _execute_lock_target(self, **kwargs):
        """command the plane to lock onto a target based on pixel values.
        
        args:
        xa, ya"""
        
        #reset command flag / command acknowledged
        self.current_command = ("none", {})
        
        #for notational convenience
        xa = kwargs['xa']
        ya = kwargs['ya']
        print "Communicator sending request to lock target"

        try:
            self.interface.lock_target(xa, ya)
        
            self.notify("LOCKED_TARGET")
        except InterfaceError as e:
            self.notify("INTERFACE_ERROR", \
                msg=e.value, \
                function=sys._getframe().f_code.co_name)
    
    def _execute_download_to_flc(self, **kwargs):
        """command the plane to download images from the camera memory
        stick to the flight linux computer.
        
        args:
        (none)"""
        
        #reset command flag / command acknowledged
        self.current_command = ("none", {})
        
        print "Communicator sending request to download to flc"
        
        try:
            self.interface.download_to_flc()

            #generate make thumbnails available for all pictures that have
            # been taken (if this is called more than once it will loop from
            # 0 again, but it's not a big deal because a picture can never
            # become unavailable once it is available)
            for i in range(0, self.image_store.picture_count):
                self.image_store.get_image(i, 1).available = True

            self.notify("DOWNLOADED_TO_FLC", picture_count=self.image_store.picture_count)
        except InterfaceError as e:
            self.notify("INTERFACE_ERROR", \
                msg=e.value, \
                function=sys._getframe().f_code.co_name)
        
    def _execute_generate_crop(self, **kwargs):
        """command the plane to generate a crop from an image based on
        pixel data representing 2 corners of a square

        args:
        picture_num, xa, ya, xb, yb
        """
        
        #reset command flag / command acknowledged
        self.current_command = ("none", {})
        
        #for notational convenience
        picture_num = kwargs['picture_num']
        xa = kwargs['xa']
        ya = kwargs['ya']
        xb = kwargs['xb']
        yb = kwargs['yb']
        print "generating a new crop for %d" % (picture_num,)
        
        try:
            self.interface.generate_crop(picture_num=picture_num, \
                xa=xa, ya=ya, xb=xb, yb=yb)

            #add a new crop to the crop_list
            crop_num = len(self.image_store.picture_list[picture_num].crop_list)
            self.image_store.picture_list[picture_num].add_crop()
            self.image_store.get_image(picture_num, crop_num).available = True
            self.image_store.get_image(picture_num, crop_num).path = \
                self.image_store.project_path + "pic" + str(picture_num) \
                + "crop" + str(crop_num) + ".jpg"
            
            self.notify("CROP_GENERATED", \
                picture_num=picture_num, 
                crop_num=crop_num)
        except InterfaceError as e:
            self.notify("INTERFACE_ERROR", \
                msg=e.value, \
                function=sys._getframe().f_code.co_name)
        
    def _execute_download_image(self, **kwargs):
        """command the plane to transmit a section of an image
        
        args:
        picture_num, crop_num
        """
        #reset request flag / request acknowledged
        self.current_request = ("none", {})
        
        #for notational convenience
        picture_num = kwargs['picture_num']
        crop_num = kwargs['crop_num']
        
        print "sending request to download image"
        
        #check if the picture in question is available for download
        if (self.image_store.get_image(picture_num, crop_num).available == True):
        
            #if the picture has size 0, initialize the picture for download
            if (self.image_store.get_image(picture_num, crop_num).size == 0):
                #get the size and update the model
                print "initializing picture %d, crop %d" % (picture_num, crop_num)
                try:
                    #if the crop is 0, we're downloading the thumbnail, we want
                    # all the info relevant to the picture (i.e. plane angles,
                    # camera angles, and gps info at the time the pic was taken
                    if crop_num == 1:
                        #TODO something = self.interface.request_info(picture_num)
                        # give off a notification
                        pass
                        
                    print "requesting size of picture %d, crop %d" % (picture_num, crop_num)
                    
                    #now we get the size of the crop
                    crop_size = self.interface.request_size(picture_num, crop_num)
                    self.image_store.get_image(picture_num, crop_num).size = crop_size
                    
                    #now that we have the size calculate the amount of 
                    # segments needed to dl the full pic
                    self.image_store.get_image(picture_num, crop_num).calculate_total_segments()
                    
                    #notify observers
                    self.notify("SIZE_CALCULATED", \
                    			picture_num=picture_num, \
                        		crop_num=crop_num, \
                        		size=crop_size)
                    
                except InterfaceError as e:
                    self.notify("INTERFACE_ERROR", \
                        msg=e.value, \
                        function=sys._getframe().f_code.co_name)

            #the picture has size info, download it
            else:
                segment_num = self.image_store.get_image(picture_num, crop_num).segments_downloaded
                print "downloading segment %d of picture %d crop %d" % (segment_num, picture_num, crop_num)
                try:
                    segment_data = self.interface.download_segment( \
                        picture_num = picture_num, \
                        crop_num = crop_num, \
                        segment_num = segment_num)

                    #store the data with the corresponding picture
                    self.image_store.get_image(picture_num, crop_num).save_segment(segment_data)

                    percent_complete = \
                        math.ceil((self.image_store.get_image(picture_num, crop_num).segments_downloaded*100) / \
                            self.image_store.get_image(picture_num, crop_num).total_segments())

                    #check for completion
                    if self.image_store.get_image(picture_num, crop_num).segments_downloaded == \
                        self.image_store.get_image(picture_num, crop_num).total_segments():
                        print "picture %d crop %d completed downloading" % (picture_num,crop_num)
                        self.image_store.get_image(picture_num, crop_num).completed = True
                    
                    #notify observers
                    self.notify("IMAGE_DOWNLOADED", \
                        picture_num=picture_num, \
                        crop_num=crop_num, \
                        percent_complete=percent_complete)
                except InterfaceError as e:
                    self.notify("INTERFACE_ERROR", \
                        msg=e.value, \
                        function=sys._getframe().f_code.co_name)

    def _execute_camera_reset(self, **kwargs):
        """command the plane to make the plane reset the camera.
        
        args:
        (none)"""
        
        #reset command flag / command acknowledged
        self.current_command = ("none", {})
        
        print "Communicator sending request to reset camera"
        
        try:
            self.interface.camera_reset()
            self.notify("CAMERA_RESET")
            
        except InterfaceError as e:
            self.notify("INTERFACE_ERROR", \
                msg=e.value, \
                function=sys._getframe().f_code.co_name)
        
    def _execute_camera_pan_left(self, **kwargs):
        """command the plane to pan camera left by increment.
        
        args:
        increment"""
        
        #reset command flag / command acknowledged
        self.current_command = ("none", {})
        
        #for notational convenience
        increment = kwargs['increment']
        print "Communicator sending request to pan camera left"
        
        try:
            self.interface.camera_pan_left(increment)
            self.notify("CAMERA_PAN_LEFT")
            
        except InterfaceError as e:
            self.notify("INTERFACE_ERROR", \
                msg=e.value, \
                function=sys._getframe().f_code.co_name)
        
    def _execute_camera_pan_right(self, **kwargs):
        """command the plane to pan camera right by increment.
        
        args:
        increment"""
        
        #reset command flag / command acknowledged
        self.current_command = ("none", {})
        
        #for notational convenience
        increment = kwargs['increment']
        print "Communicator sending request to pan camera right"
        
        try:
            self.interface.camera_pan_right(increment)
            self.notify("CAMERA_PAN_RIGHT")
            
        except InterfaceError as e:
            self.notify("INTERFACE_ERROR", \
                msg=e.value, \
                function=sys._getframe().f_code.co_name)
        
    def _execute_camera_tilt_up(self, **kwargs):
        """command the plane to tilt camera up by increment.
        
        args:
        increment"""
        
        #reset command flag / command acknowledged
        self.current_command = ("none", {})
        
        #for notational convenience
        increment = kwargs['increment']
        print "Communicator sending request to tilt camera up"
        
        try:
            self.interface.camera_tilt_up(increment)
            self.notify("CAMERA_TILT_UP")
            
        except InterfaceError as e:
            self.notify("INTERFACE_ERROR", \
                msg=e.value, \
                function=sys._getframe().f_code.co_name)
        
    def _execute_camera_tilt_down(self, **kwargs):
        """command the plane to tilt camera down by increment.
        
        args:
        increment"""
        
        #reset command flag / command acknowledged
        self.current_command = ("none", {})
        
        #for notational convenience
        increment = kwargs['increment']
        print "Communicator sending request to tilt camera down"
        
        try:
            self.interface.camera_tilt_down(increment)
            self.notify("CAMERA_TILT_DOWN")
            
        except InterfaceError as e:
            self.notify("INTERFACE_ERROR", \
                msg=e.value, \
                function=sys._getframe().f_code.co_name)

    def _execute_ping(self):
        """ping the plane and transmit back the latency."""
        
        #reset command flag / command acknowledged
        self.current_command = ("none", {})
        
        try:
            #record the latency 
            latency = self.interface.ping()
            
            self.notify("PING", latency=latency)
            
        except InterfaceError as e:
            self.notify("INTERFACE_ERROR", \
                msg=e.value, \
                function=sys._getframe().f_code.co_name)

    #*
    #* Main Loop
    #*
    
    def main(self):
        """main loop that processes commands coming in from controllers"""
        
        while True:
            # prevent loop from using 100% cpu
            time.sleep(.1)
            
            # handle the current command or request
            if self.current_command[0] != "none":
                #calls the method with the same name as the string
                # stored in current_command and passes arguments from kwargs
                getattr(self, self.current_command[0])(**self.current_command[1])
            elif self.current_request[0] != "none":
                #calls the method with the same name as the string
                # stored in current_request and passes arguments from kwargs
                getattr(self, self.current_request[0])(**self.current_request[1])
            else:
                #ping the plane
                #self._execute_ping()
                pass
