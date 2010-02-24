#ImageStation.py

#import required modules
import sys
import os.path
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

#import project related dependencies
from Communicator import *
from PictureDialog import *
import CameraControl

class ImageStation:
    """Image Station for displaying and manipulating pictures"""

    def __init__(self, communicator, camera_control):
        """constructor"""
        
        # camera_control object
        self.camera_control = camera_control
        
        # cd = currently displayed
        self.cd_crop_num = -1
        self.cd_pic_num = -1
        self.saved = False
        
        # Set the model
        self.communicator = communicator
        
        # list for tracking which pictures currently have info dialog boxes open
        self.picture_info_list = []
        
        # Configure the GUI with Glade
        self.initialize_gui()
        
        # Configure update handler
        self.update_dic = {"PICTURE_TAKEN" : self._handle_picture_taken, \
            "SEARCH_RESUMED" : self._handle_search_resumed, \
            "LOCKED_TARGET" : self._handle_locked_target, \
            "DOWNLOADED_TO_FLC" : self._handle_downloaded_to_flc, \
            "CROP_GENERATED" : self._handle_crop_generated, \
            "SIZE_CALCULATED" : self._handle_size_calculated, \
            "IMAGE_DOWNLOADED" : self._handle_image_downloaded, \
            "PING" : self._handle_ping, \
            "INTERFACE_ERROR" : self._handle_interface_error }
    
    def initialize_gui(self):
        
        #*
        #* Set up the Widget Tree
        #*
        
        self.widgets = gtk.glade.XML("ImageStation.glade")
        
        #*
        #* Set up File Chooser Dialog
        #*
        
        self.file_chooser = self.widgets.get_widget("file_chooser_dialog")
        
        #*
        #* Set up Connection Menu (can't be done in Glade)
        #* ***update: can be done in glade, just isn't right now***
        #*
        
        connection_menu = self.widgets.get_widget("connection_menu")
        
        connection_menu_none = gtk.RadioMenuItem(None, "None")
        connection_menu_serial = gtk.RadioMenuItem(connection_menu_none, "Serial")
        connection_menu_debug = gtk.RadioMenuItem(connection_menu_none, "Debug")
        
        connection_menu.append(connection_menu_none)
        connection_menu.append(connection_menu_serial)
        connection_menu.append(connection_menu_debug)
        
        connection_menu_none.show()
        connection_menu_serial.show()
        connection_menu_debug.show()
        
        #*
        #* Set up TreeView
        #*
        
        #gets tree widget as treeview with 1 column
        self.image_tree = self.widgets.get_widget("image_tree")
        
        #create treemodel object (tree_store)
        #column 0: picture name
        #column 1: picture number
        #column 2: crop number
        #column 3: % complete
        self.tree_store = gtk.TreeStore(str, int, int, str)
        
        #treeview associated with model
        self.image_tree.set_model(self.tree_store)
        
        #create column 0
        cell0 = gtk.CellRendererText()
        column0 = gtk.TreeViewColumn('Image List', cell0, markup=0)
        column0.set_resizable(True)
        self.image_tree.append_column(column0)
        
        #create column 1
        cell1 = gtk.CellRendererText()
        column1 = gtk.TreeViewColumn("Pic", cell1, text=1)
        self.image_tree.append_column(column1)
        
        #create column 2
        cell2 = gtk.CellRendererText()
        column2 = gtk.TreeViewColumn("Crop", cell2, text=2)
        self.image_tree.append_column(column2)
        
        #create column 3
        cell3 = gtk.CellRendererText()
        column3 = gtk.TreeViewColumn("Status", cell3, text=3)
        self.image_tree.append_column(column3)
        
        #*
        #* Set up ListView
        #*
        
        #gets list widget as listview with 1 column
        self.list_view = self.widgets.get_widget("image_queue")
        
        #create listmodel object (tree_store)
        #column 0: picture name
        #column 1: picture number
        #column 2: crop number
        self.list_store = gtk.ListStore(str, int, int)

        #listview associated with model
        self.list_view.set_model(self.list_store)
        self.list_view.set_reorderable(True)
        
        #create column 0
        self.list_view.set_headers_visible(True)
        column0 = gtk.TreeViewColumn("Queue", gtk.CellRendererText(), markup=0)
        column0.set_resizable(True)
        self.list_view.append_column(column0)
        
        #create column 1
        column1 = gtk.TreeViewColumn("Pic", gtk.CellRendererText(), text=1)
        self.list_view.append_column(column1)
        
        #create column 2
        column2 = gtk.TreeViewColumn("Crop", gtk.CellRendererText(), text=2)
        self.list_view.append_column(column2)
        
        #*
        #* Set up ImageTree_Menu
        #*
        
        self.image_tree_menu = self.widgets.get_widget("image_tree_menu")
        
        #*
        #* Set up Picture Info Dialog
        #*
        
        self.picture_info_dialog = self.widgets.get_widget("picture_info_dialog")
        self.picture_name_label = self.widgets.get_widget("picture_name_label")
        self.picture_shape_entry = self.widgets.get_widget("picture_shape_entry")
        self.picture_color_entry = self.widgets.get_widget("picture_color_entry")
        self.picture_alpha_entry = self.widgets.get_widget("picture_alpha_entry")
        self.picture_alphacolor_entry = self.widgets.get_widget("picture_alphacolor_entry")
        self.picture_location_entry = self.widgets.get_widget("picture_location_entry")
        self.picture_orientation_entry = self.widgets.get_widget("picture_orientation_entry")
        
        #*
        #* Set up Drawing Area
        #*
        
        self.drawing_area = self.widgets.get_widget("drawing_area")
        
        # style and gc
        self.style = self.drawing_area.get_style()
        self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
        
        # create background for drawing area
        image = gtk.Image()
        filename = "%s/images/blank.jpg" % (os.path.dirname(__file__),)
        image.set_from_file(filename)
        self.pixbuf = image.get_pixbuf()
        
        # for keeping track of crop areas
        self.box_drawn = False
        self.button_pressed = False
        self.xa = 0
        self.ya = 0
        self.xb = 0
        self.yb = 0
        
        #*
        #* Connect events
        #*
        
        file_dic = { "on_file_menu_new_activate" : self.file_menu_new_activate, \
                "on_file_menu_open_activate" : self.file_menu_open_activate, \
                "on_file_menu_save_activate" : self.file_menu_save_activate, \
                "on_file_menu_saveas_activate" : self.file_menu_saveas_activate, \
                "on_file_menu_quit_activate" : self.file_menu_quit_activate }
                
        connection_menu_none.connect("activate", self.connection_menu_none_activate)
        connection_menu_serial.connect("activate", self.connection_menu_serial_activate)
        connection_menu_debug.connect("activate", self.connection_menu_debug_activate)
            
        view_dic = { "on_view_menu_cc_activate" : self.view_menu_cc_activate }
            
        tool_dic = { "on_tool_new_clicked" : self.tool_new_clicked, \
                "on_tool_open_clicked" : self.tool_open_clicked, \
                "on_tool_save_clicked" : self.tool_save_clicked, \
                "on_tool_dl2flc_clicked" : self.tool_dl2flc_clicked, \
                "on_tool_gen_crop_clicked" : self.tool_gen_crop_clicked }
                
        chooser_dic = { "on_fcd_save_activate" : self.fcd_save_activate, \
                "on_fcd_cancel_activate" : self.fcd_cancel_activate }
        
        image_tree_dic = { "on_image_tree_button_press_event" : self.image_tree_button_press_event, \
                "on_image_tree_menu_display_activate" : self.image_tree_menu_display_activate, \
                "on_image_tree_menu_add_to_queue_activate" : self.image_tree_menu_add_to_queue_activate, \
                "on_image_tree_menu_info_activate" : self.image_tree_menu_info_activate }
        
        image_queue_dic = { "on_image_queue_key_press_event" : self.image_queue_key_press_event, \
                "on_image_queue_drag_end" : self.image_queue_drag_end }
        
        drawing_dic = { "on_drawing_area_expose_event" : self.drawing_area_expose_event, \
                "on_drawing_area_button_press_event" : self.drawing_area_button_press_event, \
                "on_drawing_area_button_release_event" : self.drawing_area_button_release_event, \
                "on_drawing_area_motion_notify_event" : self.drawing_area_motion_notify_event }
        
        general_dic = { "on_ImageWindow_destroy" : self.ImageWindow_destroy }
        
        self.widgets.signal_autoconnect(file_dic)
        self.widgets.signal_autoconnect(view_dic)
        self.widgets.signal_autoconnect(tool_dic)
        self.widgets.signal_autoconnect(chooser_dic)
        self.widgets.signal_autoconnect(image_tree_dic)
        self.widgets.signal_autoconnect(image_queue_dic)
        self.widgets.signal_autoconnect(drawing_dic)
        self.widgets.signal_autoconnect(general_dic)

    #*
    #* File Events
    #*
    
    def file_menu_new_activate(self, widget, data=None):
        """new clicked on file menu."""
        pass
    
    def file_menu_open_activate(self, widget, data=None):
        """open clicked on file menu."""
        pass
        
    def file_menu_save_activate(self, widget, data=None):
        """save clicked on file menu."""
        pass
        
    def file_menu_saveas_activate(self, widget, data=None):
        """saveas clicked on file menu."""
        pass
    
    def file_menu_quit_activate(self, widget, data=None):
        """quit clicked on file menu."""
        self._quit()
     
    #*
    #* Connection Events
    #*
    
    def connection_menu_none_activate(self, widget, data=None):
        """none clicked on connection menu."""
        if widget.get_active():
            self.communicator.set_interface("none")
    
    def connection_menu_serial_activate(self, widget, data=None):
        """serial clicked on connection menu."""
        if widget.get_active():
            self.communicator.set_interface("serial")
        
    def connection_menu_debug_activate(self, widget, data=None):
        """serial clicked on connection menu."""
        if widget.get_active():
            self.communicator.set_interface("debug")
       
    #*
    #* View Events
    #*
    
    def view_menu_cc_activate(self, widget, data=None):
        """show camera control clicked on view menu."""
        if self.camera_control.window.get_property("visible") == True:
            self.camera_control.window.hide()
        else:
            self.camera_control.window.show()

    #*
    #* Toolbar events
    #*
    
    def tool_new_clicked(self, widget, data=None):
        """new clicked on toolbar menu."""
        pass
        
    def tool_open_clicked(self, widget, data=None):
        """open clicked on the toolbar menu."""
        pass
        
    def tool_save_clicked(self, widget, data=None):
        """save clicked on the toolbar menu."""
        pass
        
    def tool_dl2flc_clicked(self, widget, data=None):
        """dl2flc clicked on the toolbar menu."""
        self._download_to_flc()

    def tool_gen_crop_clicked(self, widget, data=None):
        """generate crop clicked on the toolbar menu."""
        self._generate_crop()
        
    #*
    #* File Chooser Dialog events
    #*
        
    def fcd_save_activate(self, widget, data=None):
        """save clicked in file choose dialog."""
        print "save clicked"
    
    def fcd_cancel_activate(self, widget, data=None):
        """cancel clicked in file choose dialog."""
        print "cancel clicked"
        widget.hide()
    
    #*
    #* Image Tree events
    #*   

    def image_tree_button_press_event(self, treeview, event, data=None):
        """item selected in image_tree."""
        #show pop-up menu
        if (event.button == 3):       #right mouse click
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor(path, col, 0)
                self.image_tree_menu.popup(None, None, None, event.button, time)
            return 1

    def image_tree_menu_display_activate(self, widget, data=None):
        """display picture of selected imagetree_menu item."""
        model, treeiter = self.image_tree.get_selection().get_selected()

        pic_num = int(self.tree_store.get_value(treeiter, 1))
        crop_num = int(self.tree_store.get_value(treeiter, 2))
        self.cd_pic_num = pic_num
        self.cd_crop_num = crop_num
        self.display_image(pic_num, crop_num)
        
    def image_tree_menu_add_to_queue_activate(self, widget, data=None):
        """add selected imagetree_menu item to the download queue."""
        (model, treeiter) = self.image_tree.get_selection().get_selected()
        pic_num = int(self.tree_store.get_value(treeiter, 1))
        crop_num = int(self.tree_store.get_value(treeiter, 2))
        name = self.communicator.image_store.get_crop(pic_num, crop_num).name
        self.add_to_queue(name, pic_num, crop_num)
    
    def image_tree_menu_info_activate(self, widget, data=None):
        """display the picture info dialog box."""
        (model, treeiter) = self.image_tree.get_selection().get_selected()
        pic_num = int(self.tree_store.get_value(treeiter, 1))
        crop_num = int(self.tree_store.get_value(treeiter, 2))
        self.display_picture_info(pic_num, crop_num)
    
    def display_picture_info(self, pic_num, crop_num):
        """displays the info for the appropriate picture."""
        
        # If the dialog box isn't currently shown, get all the picture
        # attributes and display them
        if self.picture_info_list[pic_num] == False:
            # get picture attributes
            picture = self.communicator.image_store.get_picture(pic_num)
            self.picture_info_list[pic_num] = PictureDialog()
            self.picture_info_list[pic_num].set_picture(picture)
        
        # If the dialog box was already displayed, make sure we are displaying
        # info from the correct crop
        crop = self.communicator.image_store.get_crop(pic_num, crop_num)
        self.picture_info_list[pic_num].set_crop(crop)
        
        #show the box and set flag
        self.picture_info_list[pic_num].show()
        
    #*
    #* Picture Info Dialog events
    #*
    
    def pid_save_activate(self, widget, data=None):
        #TODO: do this
        print "save"
        
    def pid_cancel_activate(self, widget, data=None):
        #TODO: do this
        print "cancel"
    
    #*
    #* Image Queue events
    #*
    
    def image_queue_key_press_event(self, treeview, event, data=None):
        """button pressed in image_queue."""
        #check for delete key press
        if event.keyval == 65535:
            (model, treeiter) = treeview.get_selection().get_selected()
            pic_num = int(model.get_value(treeiter, 1))
            crop_num = int(model.get_value(treeiter, 2))
            model.remove(treeiter)
            self.communicator.image_store.get_crop(pic_num, crop_num).inqueue = False
            self.queue_changed()

    def image_queue_drag_end(self, event, data=None):
        self.queue_changed()

    #*
    #* Drawing Area events
    #*

    def drawing_area_expose_event(self, widget, event):
        x, y, width, height = widget.get_allocation()
        self.drawing_area.window.draw_pixbuf(self.gc, self.pixbuf, \
                                            0, 0, 0, 0, -1, -1)
                  
    def drawing_area_button_press_event(self, widget, event):
        """button pressed in drawing area"""
        if event.button == 1 and self.pixbuf != None:
            self.button_pressed = True
            
            if self.box_drawn == True:
                #clear the screen
                self.drawing_area.window.draw_pixbuf(self.gc, self.pixbuf, \
                                                        0, 0, 0, 0, -1, -1)
            #current coordinates
            self.x_begin = int(event.x)
            self.y_begin = int(event.y)

    def drawing_area_motion_notify_event(self, widget, event):
        if (self.button_pressed == True) & (self.pixbuf != None):
            #current coordinates
            self.x_end = int(event.x)
            self.y_end = int(event.y)
            
            #draw the box
            self.draw_box(widget, self.x_begin, self.y_begin, \
                                    self.x_end, self.y_end)
    
    def drawing_area_button_release_event(self, widget, event):
        """button released in drawing area"""
        if event.button == 1 and self.pixbuf != None:
            self.button_pressed = False
            
            #current ending coordinates
            self.x_end = int(event.x)
            self.y_end = int(event.y)
            
            #draw the box
            self.draw_box(widget, self.x_begin, self.y_begin, \
                                    self.x_end, self.y_end)
                                    
    #*
    #* General events
    #*
        
    def ImageWindow_destroy(self, widget, data=None):
        """window was destroyed, exit the program."""
        self._quit()

    #*
    #* Functions related to file manipulation
    #*
    
    #put save, open, saveas and all that stuff here
    
    def _quit(self):
        """exit the program"""
        sys.exit(1)
    
    #*
    #* Functions called by clicking on buttons and whatnot
    #*
    
    def _download_to_flc(self):
        """request model to move images from the camera's memory stick
        to the flc."""
        self.communicator.download_to_flc()
    
    def _generate_crop(self):
        """generate a new crop for the currently selected picture using
        the area selected in the currently displayed picture."""
        if self.box_drawn == True:
            if (self.cd_pic_num != -1) & (self.cd_crop_num == 1):
                self.communicator.generate_crop(picture_num=self.cd_pic_num, \
                    xa=self.xa, ya=self.ya, xb=self.xb, yb=self.yb)
            else:
                print "ERROR: can only generate a new crop from a thumbnail"
        else:
            print "ERROR: please select an area to generate a crop from"
    
    #*
    #* Functions related to images
    #*
    
    def insert_in_tree(self, pic_name, pic_num, crop_num, is_crop=False):
        """inserts a row into the imagetree"""
        # insert the picture/crop name in column 0
        if (is_crop == False):
            myiter = self.tree_store.append(None, None)
            self.tree_store.set_value(myiter, \
                0, '<span foreground="#A0A0A0"><b>' + pic_name + '</b></span>')
        elif (is_crop == True):
            #determine iter that points to row containing pic_num
            # in column 1
            for i in range(0, len(self.tree_store)):
                if (pic_num == self.tree_store[i][1]):
                    #found the parent, insert the child
                    parent = self.tree_store[i].iter
                    myiter = self.tree_store.append(parent, None)
                    self.tree_store.set_value(myiter, 0, '<span foreground="#000000"><b>' + pic_name + '</b></span>')
                    break

        # fill in the remaining columns
        self.tree_store.set_value(myiter, 1, pic_num)
        self.tree_store.set_value(myiter, 2, crop_num)
        self.tree_store.set_value(myiter, 3, "0%")
        return myiter
    
    def add_to_queue(self, name, pic_num, crop_num):
        """adds an item to the queue"""
        #if the picture is not already in the queue
        #and if it is not already downloaded
        if ((self.communicator.image_store.get_crop(pic_num, crop_num).inqueue == False) & \
                    (self.communicator.image_store.get_crop(pic_num, crop_num).completed == False)):
            #insert in queue
            myiter = self.list_store.append(None)
            #set the data in column 0
            #if the picture is ready for download set color to black
            if (self.communicator.image_store.get_crop(pic_num, crop_num).available == True):
                self.list_store.set_value(myiter, \
                    0, '<span foreground="#000000"><b>' + name + '</b></span>')
            #otherwise set to gray
            else:
                self.list_store.set_value(myiter, \
                    0, '<span foreground="#A0A0A0"><b>' + name + '</b></span>')
            #set the data in column 1 and 2
            self.list_store.set_value(myiter, 1, pic_num)
            self.list_store.set_value(myiter, 2, crop_num)
            #let model know picture is inqueue
            self.communicator.image_store.get_crop(pic_num, crop_num).inqueue = True
            #call queue_changed function
            self.queue_changed()
        elif self.communicator.image_store.get_crop(pic_num, crop_num).completed == True:
            print "image has already been downloaded"
        else:
            print "image is currently in the queue"
    
    def queue_changed(self):
        #get item at the top of the queue
        print "queue_changed called"
        try:
            #if there are items in queue send info to model
            pic_num = self.list_store[0][1]
            crop_num = self.list_store[0][2]
            self.communicator.download_image(picture_num=pic_num, crop_num=crop_num)
        except IndexError as e:
            #nothing on the queue
            pass
        
    def display_image(self, pic_num, crop_num):
        """displays the appropriate image in the drawing_area"""
        if (self.communicator.image_store.get_crop(pic_num, crop_num).completed == True):
            self.cd_crop_num = crop_num
            self.cd_pic_num = pic_num
            try:
                path = self.communicator.image_store.get_crop(pic_num, crop_num).path
                image = gtk.Image()
                image.set_from_file(path)
                self.pixbuf = image.get_pixbuf()
                w = self.pixbuf.get_width()
                h = self.pixbuf.get_height()
                #draw the image and resize
                self.drawing_area.window.draw_pixbuf(self.gc, self.pixbuf, \
                                                    0, 0, 0, 0, w, h)
                self.drawing_area.window.resize(w, h)
            except ValueError as e:
                print "picture " + str(pic_num) + " crop " + str(crop_num) + \
                    " is corrupt!"
        else:
            #draw "incomplete" image
            path = "%s/images/incomplete.jpg" % (os.path.dirname(__file__),)
            image = gtk.Image()
            image.set_from_file(path)
            self.pixbuf = image.get_pixbuf()
            w = self.pixbuf.get_width()
            h = self.pixbuf.get_height()
            #draw the image and resize
            self.drawing_area.window.draw_pixbuf(self.gc, self.pixbuf, \
                                                0, 0, 0, 0, w, h)
            self.drawing_area.window.resize(w, h)
            
    def draw_box(self, widget, x_begin, y_begin, x_end, y_end):
        self.box_width = self.x_end - self.x_begin
        self.box_height = self.y_end - self.y_begin
        #erase previous box
        widget.window.draw_pixbuf(self.gc, self.pixbuf, \
                                                        0, 0, 0, 0, -1, -1)
        #box drawn from bottom right to top left
        if ((self.box_width < 0) & (self.box_height < 0)):
            self.xa = self.x_end
            self.ya = self.y_end
            self.xb = self.xa + abs(self.box_width)
            self.yb = self.ya + abs(self.box_width)
            widget.window.draw_rectangle(self.gc, False, \
                        self.xa, self.ya, \
                        abs(self.box_width), abs(self.box_height))
            self.box_drawn = True
        #box drawn top right to bottom left
        elif ((self.box_width < 0) & (self.box_height > 0)):
            self.xa = self.x_begin + self.box_width
            self.ya = self.y_begin
            self.xb = self.xa + abs(self.box_width)
            self.yb = self.ya + abs(self.box_width)    
            widget.window.draw_rectangle(self.gc, False, \
                        self.xa, self.ya, \
                        abs(self.box_width), abs(self.box_height))
            self.box_drawn = True
        #box drawn from bottom left to top right
        elif ((self.box_width > 0) & (self.box_height < 0)):
            self.xa = self.x_begin
            self.ya = self.y_begin + self.box_height
            self.xb = self.xa + abs(self.box_width)
            self.yb = self.ya + abs(self.box_width)    
            widget.window.draw_rectangle(self.gc, False, \
                        self.xa, self.ya, \
                        abs(self.box_width), abs(self.box_height))
            self.box_drawn = True  
        #box drawn from top left to bottom right              
        elif ((self.box_width > 0) & (self.box_height > 0)):
            self.xa = self.x_begin
            self.ya = self.y_begin
            self.xb = self.xa + abs(self.box_width)
            self.yb = self.ya + abs(self.box_width)  
            widget.window.draw_rectangle(self.gc, False, \
                        self.xa, self.ya, \
                        abs(self.box_width), abs(self.box_height))
            self.box_drawn = True
        #no box drawn
        else:
            self.xa = 0
            self.ya = 0
            self.xb = 0
            self.yb = 0
            self.box_drawn = False
            
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
        #add the picture to tree!
        picture_name = self.communicator.image_store.get_crop(picture_num, 1).name
        self.insert_in_tree(picture_name, picture_num, 1, False)
        self.add_to_queue(picture_name, picture_num, 1)
        self.picture_info_list.append(False)
        
    def _handle_search_resumed(self):
        pass
        
    def _handle_locked_target(self):
        pass
        
    def _handle_downloaded_to_flc(self, picture_count):
        print "complete download to flc, %d pictures now available" % (picture_count,)
        
        #render as active in the treeview
        for i in range(0, picture_count):
            self.tree_store[i][0] = '<span foreground="#000000"><b>' + \
                self.communicator.image_store.get_crop(i, 1).name + '</b></span>'
        
        #render as active in the queue
        for i in range(0, len(self.list_store)):
            picture_num = self.list_store[i][1]
            crop_num = self.list_store[i][2]
            if picture_num < picture_count:
                self.list_store[i][0] = '<span foreground="#000000"><b>' + \
                self.communicator.image_store.get_crop(picture_num, crop_num).name + '</b></span>'
        
        self.queue_changed()
        
    def _handle_crop_generated(self, picture_num, crop_num):
        #a crop was generated, add it to the tree
        crop_name = self.communicator.image_store.get_crop(picture_num, crop_num).name
        self.insert_in_tree(crop_name, picture_num, crop_num, True)
        self.add_to_queue(crop_name, picture_num, crop_num)
        
    def _handle_size_calculated(self, picture_num, crop_num, size):
    	print "picture %d, crop %d has size %d" % (picture_num, crop_num, size)
    	self.queue_changed()
        
    def _handle_image_downloaded(self, picture_num, crop_num, percent_complete):
        #part or all of a picture has finished downloading
        if (self.communicator.image_store.get_crop(picture_num, crop_num).completed == True):
            del self.list_store[0]

        # update the progress
        if crop_num == 1:
            #it's the parent/thumbnail, just do it
            self.tree_store[picture_num][3] = str(percent_complete) + "%"
        else:
            #it's a child, cycle through the array to find it
            parent = self.tree_store[picture_num].iter
            n=0
            childiter = self.tree_store.iter_nth_child(parent, n)
            while (self.tree_store.get_value(childiter, 2) != crop_num):
                n += 1
                childiter = self.tree_store.iter_nth_child(parent, n)
            self.tree_store.set_value(childiter, 3, str(percent_complete) + "%")
        
        #call queue changed
        self.queue_changed()
        
    def _handle_ping(self, latency):
        print "ping latency was: %sms" % (latency,)
        
    def _handle_interface_error(self, msg, function):
        print "interface error from function \'%s\': \"%s\"" % (function, msg)
