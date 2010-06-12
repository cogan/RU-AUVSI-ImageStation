#CameraControl.py

#import required modules
import os
from subprocess import Popen
import pygtk
pygtk.require('2.0')
import gtk.glade

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
        tes = "/dev/video0"
        self.streaming = False
        #self.video_menu_streaming.set_active(True)
        
        # Initialize video display
        self.display_mode = "down"
        self._set_display_mode("down")
        
        # Configure update handler
        self.update_dic = {"POWER_TOGGLED" : self._handle_power_toggled, \
            "MODE_SET" : self._handle_mode_set, \
            "PICTURE_TAKEN" : self._handle_picture_taken, \
            "RECORD_TOGGLED" : self._handle_record_toggled, \
            "CAMERA_PAN" : self._handle_camera_pan, \
            "CAMERA_TILT" : self._handle_camera_tilt }
            
    def initialize_gui(self):
        
        #*
        #* Set up the Widget Tree
        #*
        
        self.widgets = gtk.glade.XML("CameraControl.glade")
        
        #*
        #* Get top level window
        #*
        
        self.window = self.widgets.get_widget("camera_window")
        self.window.set_title("Camera Control")
        
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
        
        button_dic = { "on_on_off_clicked" : self.on_off_clicked, \
                    "on_camera_mode_clicked" : self.camera_mode_clicked, \
                    "on_storage_mode_clicked" : self.storage_mode_clicked, \
                    "on_take_clicked" : self.take_clicked, \
                    "on_record_clicked" : self.record_clicked, \
                    "on_toggle_display_clicked" : self.toggle_display_clicked }
        
        slider_dic = {"on_pan_value_changed" : self.pan_value_changed, \
                    "on_tilt_value_changed" : self.tilt_value_changed }
        
        general_dic = { "on_camera_window_delete_event" : self.camera_window_delete_event }

        self.widgets.signal_autoconnect(video_dic)
        self.widgets.signal_autoconnect(button_dic)
        self.widgets.signal_autoconnect(slider_dic)
        self.widgets.signal_autoconnect(general_dic)

    #*
    #* Video Events
    #*

    def video_menu_streaming_toggled(self, widget, data=None):
        self._toggle_streaming()

    #*
    #* Button Events
    #*
    
    def on_off_clicked(self, widget, data=None):
        self._toggle_on_off()
        
    def camera_mode_clicked(self, widget, data=None):
        self._camera_mode()
        
    def storage_mode_clicked(self, widget, data=None):
        self._storage_mode()
        
    def take_clicked(self, widget, data=None):
        self._take_picture()
        
    def record_clicked(self, widget, data=None):
        self._toggle_record()
        
    def toggle_display_clicked(self, widget, data=None):
        if self.display_mode == "down":
            self._set_display_mode("up")
        else:
            self._set_display_mode("down")
            
    def tilt_value_changed(self, widget, data=None):
        # snap to 0
        if -10 <= widget.get_adjustment().get_value() <= 10:
            widget.get_adjustment().set_value(0)
        self._tilt(int(widget.get_adjustment().get_value()))
        
    def pan_value_changed(self, widget, data=None):
        # snap to 0
        if -15 <= widget.get_adjustment().get_value() <= 15:
            widget.get_adjustment().set_value(0)
        self._pan(int(widget.get_adjustment().get_value()))
    
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

        #MPLAYER_CMD="mplayer tv:// -tv driver=v4l2:input=1:norm=ntsc:device=%s -wid %i -slave -idle"
        MPLAYER_CMD="mplayer -dumpfile /home/cogan/Desktop/test.mpg tv:// -tv driver=v4l2:input=1:norm=ntsc:device=%s -wid %i -slave -idle"

        command = MPLAYER_CMD  % (self.video_device, self.xid)
        print command
        commandList = command.split()
        self.proc_inst = Popen(commandList)
        
        win = self.video_canvas.window
        w,h = win.get_size()
        #color = gtk.gdk.Color(red=0, green=0, blue=0, pixel=0)		

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
    
    def _toggle_on_off(self):
        self.communicator.toggle_power()
        
    def _camera_mode(self):
        self.communicator.set_mode(mode=0)
        
    def _storage_mode(self):
        self.communicator.set_mode(mode=1)
    
    def _take_picture(self):
        """request model to take a picture"""
        self.communicator.take_picture()
        
    def _toggle_record(self):
        self.communicator.toggle_record()

    def _tilt(self, value):
        self.communicator.tilt(value=value)
    
    def _pan(self, value):
        self.communicator.pan(value=value)

    #def _camera_zoom_in(self, inc):
    #    """request model to zoom in by increment"""
    #    self.communicator.camera_zoom_in(increment=inc)
    
    #def _camera_zoom_out(self, inc):
    #    """request model to zoom out by increment"""
    #    self.communicator.camera_zoom_out(increment=inc)

    #*
    #* Update
    #*
    
    def update(self, update, **kwargs):
        """update to reflect the model"""
        try:
            function_to_call = self.update_dic[update]
            function_to_call(**kwargs)
        except KeyError:
            pass
    
    def _handle_power_toggled(self):
        pass
    
    def _handle_mode_set(self, mode):
        pass
    
    def _handle_picture_taken(self, picture_num):
        pass
    
    def _handle_record_toggled(self):
        pass
    
    def _handle_camera_pan(self, value):
        pass
    
    def _handle_camera_tilt(self, value):
        pass