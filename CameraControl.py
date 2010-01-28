#ImageStation.py

#****
#TODO:
# get pictures for buttons and up/down arrow
# get new pictures for 'dl to flc' and 'generate crop'
# get new/save/load working
#****

#import required modules
import sys
import os
from subprocess import Popen
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

#import project related dependencies
from Communicator import *

class CameraControl:
    """Control panel for manipulating camera on plane."""
    
    def __init__(self, communicator):
        """constructor"""
        
        # Set the model
        self.communicator = communicator
        
        # Initialize the increment for pan/tilting
        self.increment = 1
        
        # Configure the GUI with Glade
        self.initialize_gui()
        
        # Initialize video streaming
        self.video_device = "/dev/video0"
        self.streaming = False
        #self.video_menu_streaming.set_active(True)
        
        # Initialize video display
        self.display_mode = "down"
        self._set_display_mode("down")
        
        # Configure update handler
        self.update_dic = {"PICTURE_TAKEN" : self._handle_picture_taken, \
            "CAMERA_RESET" : self._handle_camera_reset, \
            "CAMERA_PAN_LEFT" : self._handle_camera_pan_left, \
            "CAMERA_PAN_RIGHT" : self._handle_camera_pan_right, \
            "CAMERA_TILT_UP" : self._handle_camera_tilt_up, \
            "CAMERA_TILT_DOWN" : self._handle_camera_tilt_down }
    
    def initialize_gui(self):
        
        #*
        #* Set up the Widget Tree
        #*
        
        self.widgets = gtk.glade.XML("CameraControl.glade")
        
        #*
        #* Get top level window
        #*
        
        self.window = self.widgets.get_widget("camera_window")
        
        #*
        #* Set up video check menu item
        #*
        
        self.video_menu_streaming = self.widgets.get_widget("video_menu_streaming")
        
        #*
        #* Set up display mode button
        #*
        
        self.toggle_display = self.widgets.get_widget("toggle_display")
        
        #*
        #* Set up drawing area
        #*
        
        self.video_canvas = self.widgets.get_widget("drawing_area")
        self.xid = self.video_canvas.window.xid
        
        video_dic = { "on_video_menu_streaming_toggled" : self.video_menu_streaming_toggled }
        
        button_dic = { "on_take_clicked" : self.take_clicked, \
                    "on_reset_clicked" : self.reset_clicked, \
                    "on_zoom_in_clicked" : self.zoom_in_clicked, \
                    "on_zoom_out_clicked" : self.zoom_out_clicked, \
                    "on_pan_left_clicked" : self.pan_left_clicked, \
                    "on_pan_right_clicked" : self.pan_right_clicked, \
                    "on_tilt_up_clicked" : self.tilt_up_clicked, \
                    "on_tilt_down_clicked" : self.tilt_down_clicked, \
                    "on_toggle_display_clicked" : self.toggle_display_clicked }

        general_dic = { "on_camera_window_delete_event" : self.camera_window_delete_event }

        self.widgets.signal_autoconnect(video_dic)
        self.widgets.signal_autoconnect(button_dic)
        self.widgets.signal_autoconnect(general_dic)

    #*
    #* Video Events
    #*

    def video_menu_streaming_toggled(self, widget, data=None):
        self._toggle_streaming()

    #*
    #* Button Events
    #*
    
    def take_clicked(self, widget, data=None):
        self._take_picture()
    
    def reset_clicked(self, widget, data=None):
        self._camera_reset()
    
    def zoom_in_clicked(self, widget, data=None):
        self._camera_zoom_in(self.increment)
     
    def zoom_out_clicked(self, widget, data=None):
        self._camera_zoom_out(self.increment) 
        
    def pan_left_clicked(self, widget, data=None):
        self._camera_pan_left(self.increment)
        
    def pan_right_clicked(self, widget, data=None):
        self._camera_pan_right(self.increment)
        
    def tilt_up_clicked(self, widget, data=None):
        self._camera_tilt_up(self.increment)
        
    def tilt_down_clicked(self, widget, data=None):
        self._camera_tilt_down(self.increment)
        
    def toggle_display_clicked(self, widget, data=None):
        if self.display_mode == "down":
            self._set_display_mode("up")
        else:
            self._set_display_mode("down")
    
    #*
    #* General Events
    #*
    
    def camera_window_delete_event(self, widget, data=None):
        """hide the window and return True to prevent it from being destroyed"""
        self.window.hide()
        return True
        
    #*
    #* Functions called by clicking on buttons and whatnot
    #*
    
    def _toggle_streaming(self):
        if (self.streaming == False) and (self.video_menu_streaming.get_active() == True):
            
            self._set_display_mode("up")
            
            # make sure the video device exists, if not exit
            if not os.path.exists(self.video_device):
                self.video_menu_streaming.set_active(False)
                print "%s does not exist" % (self.video_device,)
                return
            
            # display video
            self._setup_video()
            self.streaming = True
        
        elif (self.streaming == True):
            Popen.terminate(self.proc_inst)
            self.streaming = False
    
    def _setup_video(self):
        """do video stuff"""

        MPLAYER_CMD="mplayer tv:// -tv driver=v4l2:input=1:norm=ntsc:device=%s -wid %i -slave -idle"

        command = MPLAYER_CMD  % (self.video_device, self.xid)
        commandList = command.split()
        self.proc_inst = Popen(commandList)
        
        win = self.video_canvas.window
        w,h = win.get_size()
        color = gtk.gdk.Color(red=0, green=0, blue=0, pixel=0)		

        win.draw_rectangle(self.video_canvas.get_style().black_gc, True, 2,2, w,h )
    
    def _set_display_mode(self, mode):
        if mode == "up":
            self.display_mode = "up"
            
            #show the video
            self.video_canvas.show()
            self.window.resize(1,1)
            
            #change the image on the button
            image = gtk.Image()
            image.set_from_file("images/video_up.png")
            image.show()
            self.toggle_display.set_image(image)
            
        else:
            self.display_mode = "down"
            
            #hide the video
            self.video_canvas.hide()
            self.window.resize(1,1)
            
            #change the image on the button
            image = gtk.Image()
            image.set_from_file("images/video_down.png")
            image.show()
            self.toggle_display.set_image(image)
    
    def _take_picture(self):
        """request model to take a picture"""
        self.communicator.take_picture()
        
    def _camera_reset(self):
        """request model to move camera to its home position"""
        self.communicator.camera_reset()

    def _camera_zoom_in(self, inc):
        """request model to zoom in by increment"""
        self.communicator.camera_zoom_in(increment=inc)
    
    def _camera_zoom_out(self, inc):
        """request model to zoom out by increment"""
        self.communicator.camera_zoom_out(increment=inc)
    
    def _camera_pan_left(self, inc):
        """request model to pan camera left by increment"""
        self.communicator.camera_pan_left(increment=inc)
        
    def _camera_pan_right(self, inc):
        """request model to pan camera right by increment"""
        self.communicator.camera_pan_right(increment=inc)
        
    def _camera_tilt_up(self, inc):
        """request model to tilt camera up by increment"""
        self.communicator.camera_tilt_up(increment=inc)
        
    def _camera_tilt_down(self, inc):
        """request model to tilt camera down by increment"""
        self.communicator.camera_tilt_down(increment=inc)

    #*
    #* Update
    #*
    
    def update(self, update, **kwargs):
        """update to reflect the model"""
        try:
            function_to_call = self.update_dic[update]
            function_to_call(**kwargs)
        except KeyError as e:
            pass

    def _handle_picture_taken(self, picture_num):
        pass

    def _handle_camera_reset(self):
        pass
    
    def _handle_camera_pan_left(self):
        pass
        
    def _handle_camera_pan_right(self):
        pass
    
    def _handle_camera_tilt_up(self):
        pass
    
    def _handle_camera_tilt_down(self):
        pass
