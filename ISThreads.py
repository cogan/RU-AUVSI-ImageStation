#ISThreads.py (Image Station Threads)

#import required modules
import threading
import sys
import pygtk
pygtk.require('2.0')
import gtk
import time

#import project related dependencies
from Communicator import *

#*
#* Thread Classes
#*

class GtkThread(threading.Thread):
    
    def run(self):
        print "Gtk thread started"
        gtk.gdk.threads_init()
        gtk.main()

class CommunicatorThread(threading.Thread):
        
    def __init__(self, communicator):
        self.communicator = communicator
        threading.Thread.__init__(self)
        
    def run(self):
        print "Communicator Loop Started"
        self.communicator.main()