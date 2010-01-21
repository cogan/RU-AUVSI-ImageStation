#ImageStation.py

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
        self.increment = 1;
        
        # Configure the GUI with Glade
        self.initialize_gui()
        
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
        #* Set up video feed
        #*
        
        self.video_canvas = self.widgets.get_widget("drawing_area")
        self.xid = self.video_canvas.window.xid
        
        button_dic = { "on_take_clicked" : self.take_clicked, \
                    "on_reset_clicked" : self.reset_clicked, \
                    "on_pan_left_clicked" : self.pan_left_clicked, \
                    "on_pan_right_clicked" : self.pan_right_clicked, \
                    "on_tilt_up_clicked" : self.tilt_up_clicked, \
                    "on_tilt_down_clicked" : self.tilt_down_clicked, \
                    "on_button1_clicked" : self.button1_clicked }
                    
        self.widgets.signal_autoconnect(button_dic)

    #*
    #* Button Events
    #*
    
    def take_clicked(self, widget, data=None):
        self._take_picture()
    
    def reset_clicked(self, widget, data=None):
        self._camera_reset()
        
    def pan_left_clicked(self, widget, data=None):
        self._camera_pan_left(self.increment)
        
    def pan_right_clicked(self, widget, data=None):
        self._camera_pan_right(self.increment)
        
    def tilt_up_clicked(self, widget, data=None):
        self._camera_tilt_up(self.increment)
        
    def tilt_down_clicked(self, widget, data=None):
        self._camera_tilt_down(self.increment)
        
    def button1_clicked(self, widget, data=None):
        self._video()
    
    #*
    #* Functions called by clicking on buttons and whatnot
    #*
    
    def _take_picture(self):
        """request model to take a picture"""
        self.communicator.take_picture()
        
    def _camera_reset(self):
        """request model to move camera to its home position"""
        self.communicator.camera_reset()
        
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
      
    def _video(self):
        """do video stuff"""

        FIFO = "/tmp/fifo%d" % time.time()
        STDOUT = "/tmp/out%d" % time.time()
        STDERR = "/dev/null"
        MPLAYER_CMD="mplayer tv:// -tv driver=v4l2:input=1:norm=ntsc:device=/dev/video0 -wid %i -slave -idle"
        #"mplayer -ao pcm:file=%s -wid %i -slave -idle -noconsolecontrols -input file=%s"

        if os.path.exists(FIFO):
            os.unlink(FIFO)

        os.mkfifo(FIFO)

        command = MPLAYER_CMD  % (self.xid)
        commandList = command.split()
        Popen(commandList, stdout=open(STDOUT,"w+b"), stderr=open(STDOUT,"r+b"))

        #self.mplayerClient = open(FIFO,"w")
        #self.progressLog = open(STDOUT,"r")
        #self.mplayerClient.write("loadfile '%s' 0\npause" % self.videoFile)

        #self.mediaButtonBox.set_sensitive(True)

        win = self.video_canvas.window
        w,h = win.get_size()
        color = gtk.gdk.Color(red=0, green=0, blue=0, pixel=0)		

        win.draw_rectangle(self.video_canvas.get_style().black_gc, True, 2,2, w,h )

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
