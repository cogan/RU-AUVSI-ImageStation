#DebugInterface.py

from Interface import *
from NmeaEncoder import *
from NmeaDecoder import *
from ivy.std_api import *

import time
import subprocess
import thread

class FrameGrabberInterface(Interface):
    """interface class to use when debugging."""
    
    def __init__(self):
        """constructor"""
        print "Using the frame grabber interface"
        
        # fifo to communicate with mplayer
        self.fifo_name = "mplayer_fifo"
        
        thread.start_new_thread(self.ivy_setup, ())
        
        self.heading = "NW"
        self.latitude = "38.1454"
        self.longitude = "76.431586"
            
    def __del__(self):
        print "framegrabber destructor called, killing ivy bus"
    
    #*
    #* Define Abstract functions
    #*
    
    def toggle_power(self):
        """toggle power on and off for the camera"""
        raise InterfaceError("This interface does not support that functionality")
    
    def set_mode(self, mode):
        """set the mode for the camera (0 for storage, 1 for camera mode)"""
        raise InterfaceError("This interface does not support that functionality")
    
    def take_picture(self, picture_num):
        """snap a picture."""
        subprocess.Popen(['./mplayer_screenshot.sh', self.fifo_name])
    
    def toggle_record(self):
        """toggle recording on and off for the camera"""
        raise InterfaceError("This interface does not support that functionality")
    
    def pan(self, value):
        """set the pan servo to position (-180 to 180)"""
        raise InterfaceError("This interface does not support that functionality")

    def tilt(self, value):
        """set the pan servo to position (-45 to 45)"""
        raise InterfaceError("This interface does not support that functionality")
    
    #def resume_search(self):
    #    """have the camera resume it's search pattern."""
    #    pass
        
    #def lock_target(self, xa, ya):
    #    """lock onto a target given pixels xa and ya."""
    #    pass
        
    def download_to_flc(self):
        """download pictures form the camera memory onto the
        flight linux computer."""
        raise InterfaceError("This interface does not support that functionality")

    def generate_crop(self, picture_num, xa, ya, xb, yb):
        """generate a crop of an image given the image number,
        xa, ya, xb, and yb. which represent the top left and bottom right
        corners of a rectangle."""
        raise InterfaceError("This interface does not support that functionality")
        
    def request_info(self, picture_num):
        """get all positional info about a picture
        returns gps_x, gps_y, pan, tilt, yaw, pitch, roll, orientation, altitude"""
        raise InterfaceError("This interface does not support that functionality")
               
    def request_size(self, picture_num, crop_num):
        """get the size of a crop"""
        raise InterfaceError("This interface does not support that functionality")
        
    def download_segment(self, picture_num, crop_num, segment_num): 
        """download a segment of an image"""
        raise InterfaceError("This interface does not support that functionality")

    
    #def camera_zoom_in(self, increment):
    #    """have the camera zoom in."""
    #    return True

    #def camera_zoom_out(self, increment):
    #    """have the camera zoom out."""
    #    return True
                
    def ping(self):
        """ping the plane"""
        pass
    
    def lprint(self, fmt,*arg):
        print "GroundStationIvy:" + ": " + fmt % arg

    def oncxproc(self, agent, connected):
        """connection callback"""
        if connected == IvyApplicationDisconnected:
            self.lprint( "Ivy application %r was disconnected", agent)
        else:
            self.lprint( "Ivy application %r was connected", agent)
            self.lprint("currents Ivy application are [%s]", IvyGetApplicationList())

    def ondieproc(self, agent, id):
        """die callback"""
        self.lprint( "received the order to die from %r with id = %d", agent, id)

    def ongpsproc(self, agent, *larg):
        #self.lprint("Received from %r: [%s] ", agent, larg[0])
        # parse gps info
        if len(larg) > 0:
            try:
                data_str = larg[2]
                data_arr = data_str.split(" ")
                self.heading = data_arr[4]
                self.latitude = data_arr[5]
                self.longitude = data_arr[6]
            except Exception as e:
                pass

    def ivy_setup(self):
        # initialize
        IvyInit("GroundStationIvy",   # application name for Ivy
          "Ground Station Ivy is Ready" , # ready message
          0,            # main loop is local (ie. using IvyMainloop)
          self.oncxproc,     # handler called on connection/deconnection
          self.ondieproc     # handler called when a diemessage is received 
        )

        # start the bus
        sivybus = "192.168.1.255:2010"
        IvyStart(sivybus)

        # check for messages containing gps information
        IvyBindMsg(self.ongpsproc, "^([0-9]+\.[0-9]+ )?([^ ]*) +(FLIGHT_PARAM( .*|$))")

        # loop
        IvyMainLoop()
