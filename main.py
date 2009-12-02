#!/usr/bin/env python

#main.py

#import required modules
import sys

#import project related dependencies
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
    image_station = ImageStation(communicator)
    communicator.attach(image_station)
    camera_control = CameraControl(communicator)
    communicator.attach(camera_control)

    #create threads for the models and controllers
    ct = CommunicatorThread(communicator)
    gt = GtkThread()

    #start the threads
    ct.start()
    gt.start()
