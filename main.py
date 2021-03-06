#!/usr/bin/env python

###############################################################################
#
# file: main.py
# author: Cogan Noll
# email: colgate360@gmail.com
# last modified: 2010
#
###############################################################################

import sys

from Communicator import *
from ImageStation import *
from CameraControl import *
from ISThreads import *

#
# Script to start the program
#

if __name__ == "__main__":

    #create the communicator (model)
    communicator = Communicator()

    #create GUI components (controllers)
    camera_control = CameraControl(communicator)
    communicator.attach(camera_control)
    image_station = ImageStation(communicator, camera_control)
    communicator.attach(image_station)
    
    #create threads for the models and controllers
    ct = CommunicatorThread(communicator)
    gt = GtkThread()

    #start the threads
    ct.start()
    gt.start()
