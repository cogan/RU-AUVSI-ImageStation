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

class ImageStation:
    """Image Station for displaying and manipulating pictures"""

    def __init__(self, communicator):
        """constructor"""
        
        # cd = currently displayed
        self.cd_crop_num = -1
        self.cd_pic_num = -1
        self.saved = False
        
        # Set the model
        self.communicator = communicator
        
        # Configure the GUI with Glade
        self.initialize_gui()
        
        # Configure update handler
        self.update_dic = {"PICTURE_TAKEN" : self._handle_picture_taken, \
            "SEARCH_RESUMED" : self._handle_search_resumed, \
            "LOCKED_TARGET" : self._handle_locked_target, \
            "DOWNLOADED_TO_FLC" : self._handle_downloaded_to_flc, \
            "CROP_GENERATED" : self._handle_crop_generated, \
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
        #*
        
        connection_menu = self.widgets.get_widget("connection_menu")
        
        connection_menu_none = gtk.RadioMenuItem(None, "None")
        connection_menu_serial = gtk.RadioMenuItem(connection_menu_none, "Serial")
        
        connection_menu.append(connection_menu_none)
        connection_menu.append(connection_menu_serial)
        
        
        
        connection_menu_none.show()
        connection_menu_serial.show()
        
        #*
        #* Set up TreeView
        #*
        
        #gets tree widget as treeview with 1 column
        self.image_tree = self.widgets.get_widget("image_tree")
        
        #create treemodel object (treestore)
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
        
        #create listmodel object (treestore)
        #column 0: picture name
        #column 1: picture number
        #column 2: crop number
        self.list_store = gtk.TreeStore(str, int, int)

        #listview associated with model
        self.list_view.set_model(self.list_store)
        
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
        
        self.image_tree_menu = self.widgets.get_widget("imagetree_menu")
        
        #*
        #* Set up Drawing Area
        #*
        
        self.drawing_area = self.widgets.get_widget("drawing_area")
        
        # style and gc
        self.style = self.drawing_area.get_style()
        self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
        
        # create background for drawing area
        image = gtk.Image()
        filename = "%s/blank.jpg" % (os.path.dirname(__file__),)
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
                
        connection_menu_none.connect("activate", \
            self.connection_menu_none_activate)
        connection_menu_serial.connect("activate", \
            self.connection_menu_serial_activate)
            
        tool_dic = { "on_tool_new_clicked" : self.tool_new_clicked, \
                "on_tool_open_clicked" : self.tool_open_clicked, \
                "on_tool_save_clicked" : self.tool_save_clicked, \
                "on_tool_dl2flc_clicked" : self.tool_dl2flc_clicked, \
                "on_tool_gen_crop_clicked" : self.tool_gen_crop_clicked }
                
        chooser_dic = { "on_fcd_save_activate" : self.fcd_save_activate, \
                "on_fcd_cancel_activate" : self.fcd_cancel_activate }
        
        image_tree_dic = { "on_image_tree_button_press_event" : self.image_tree_button_press_event, \
                "on_image_tree_menu_display_activate" : self.image_tree_menu_display_activate, \
                "on_image_tree_menu_add_to_queue_activate" : self.image_tree_menu_add_to_queue_activate }
        
        drawing_dic = { "on_drawing_area_expose_event" : self.drawing_area_expose_event, \
                "on_drawing_area_button_press_event" : self.drawing_area_button_press_event, \
                "on_drawing_area_button_release_event" : self.drawing_area_button_release_event, \
                "on_drawing_area_motion_notify_event" : self.drawing_area_motion_notify_event }
        
        general_dic = { "on_ImageWindow_destroy" : self.ImageWindow_destroy }
        
        self.widgets.signal_autoconnect(file_dic)
        self.widgets.signal_autoconnect(tool_dic)
        self.widgets.signal_autoconnect(chooser_dic)
        self.widgets.signal_autoconnect(image_tree_dic)
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
                self.imagetree_menu.popup(None, None, None, event.button, time)
            return 1

    def image_tree_menu_display_activate(self, widget, data=None):
        """display picture of selected imagetree_menu item."""
        model, treeiter = self.treeview.get_selection().get_selected()
        self.raw_name = self.treestore.get_value(treeiter, 0)
        self.pic_name = self.remove_markup(self.raw_name)
        #set currently displayed pic and crop num
        self.crop_num = self.treestore.get_value(treeiter, 2)
        self.pic_num = self.treestore.get_value(treeiter, 3)
        self.display_image(self.crop_num, self.pic_num)
        
    def image_tree_menu_add_to_queue_activate(self, widget, data=None):
        """add selected imagetree_menu item to the download queue."""
        #get name
        model, treeiter = self.treeview.get_selection().get_selected()
        self.raw_name = self.treestore.get_value(treeiter, 0)
        self.pic_name = self.remove_markup(self.raw_name)
        #get index
        self.crop_num = self.treestore.get_value(treeiter, 2)
        self.pic_num = self.treestore.get_value(treeiter, 3)
        self.add_to_queue(self.pic_name, self.crop_num, self.pic_num)
    
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
            if (self.cd_pic_num != -1) & (self.cd_crop_num == 0):
                self.communicator.generate_crop(picture_num=self.cd_pic_num, \
                    xa=self.xa, ya=self.ya, xb=self.xb, yb=self.yb)
            else:
                print "ERROR: can only generate a new crop from a thumbnail"
        else:
            print "ERROR: please select an area to generate a crop from"
    
    #*
    #* Functions related to images
    #*
    
    def add_to_queue(self, name, crop_num, pic_num):
        """adds an item to the queue"""
        #if the picture is not already in the queue
        #and if it is not already downloaded
        if ((self.model.picture_list[pic_num].crop_list[crop_num].inqueue == False) & \
                    (self.model.picture_list[pic_num].crop_list[crop_num].completed == False)):
            #insert in queue
            myiter = self.liststore.append(None, None)
            #set the data in column 0
            #if the picture is ready for download set color to black
            if (self.model.picture_list[pic_num].crop_list[crop_num].available == True):
                self.liststore.set_value(myiter, \
                    0, '<span foreground="#000000"><b>' + name + '</b></span>')
            #otherwise set to gray
            else:
                self.liststore.set_value(myiter, \
                    0, '<span foreground="#A0A0A0"><b>' + name + '</b></span>')
            #set the data in column 1 and 2
            self.liststore.set_value(myiter, 1, crop_num)
            self.liststore.set_value(myiter, 2, pic_num)
            #let model know picture is inqueue
            self.model.picture_list[pic_num].crop_list[crop_num].inqueue = True
            #call queue_changed function
            self.queue_changed()
        else:
            print "picture is already in the queue or has already completed"
    
    def queue_changed(self):
        #get item at the top of the queue
        print "queue change called"
        try:
            #if there are items in queue send info to model
            self.raw_name = self.liststore[0][0]
            self.pic_name = self.remove_markup(self.raw_name)
            self.crop_num = self.liststore[0][1]
            self.pic_num = self.liststore[0][2]
            self.model.set_request_flag(1, self.crop_num, self.pic_num)
        except Exception:
            self.model.set_request_flag(0)
    
    def remove_markup(self, string):
        """removes markup from strings in liststore and treestore"""
        #this will only remove the markup the colored bold strings
        #if other markup is applied this script will need to be changed
        #30 - length of beginning markup
        #11 - length of ending markup
        return string[30:len(string)-11]
    
    def insert_in_tree(self, pic_name, crop_num, pic_num, is_crop=False):
        """inserts a row into the imagetree"""
        #insert the picture name in column 0
        if (is_crop == False):
            myiter = self.treestore.append(None, None)
            self.treestore.set_value(myiter, \
                0, '<span foreground="#A0A0A0"><b>' + pic_name + '</b></span>')
        elif (is_crop == True):
            #determine iter that points to row containing pic_num
            #in column 3
            for i in range(0, len(self.treestore)):
                if (pic_num == self.treestore[i][3]):
                    #found the parent, insert the child
                    parent = self.treestore[i].iter
                    myiter = self.treestore.append(parent, None)
                    self.treestore.set_value(myiter, 0, '<span foreground="#000000"><b>' + pic_name + '</b></span>')
                    break

        #insert the appropriate mark in column 1
        self.treestore.set_value(myiter, 1, 'X')

        #insert crop number and picture number in column 2 and 3
        self.treestore.set_value(myiter, 2, crop_num)
        self.treestore.set_value(myiter, 3, pic_num)
        
        return myiter
        
    def display_image(self, crop_num, pic_num):
        """displays the appropriate image in the drawing_area"""
        #set style and gc necessary for drawing
        #this should be moved but i need it here now for debugging
        if (self.model.picture_list[pic_num].crop_list[crop_num].completed == True):
            self.cd_crop_num = crop_num
            self.cd_pic_num = pic_num
            try:
                self.path = self.model.picture_list[pic_num].crop_list[crop_num].path
                self.image = gtk.Image()
                self.image.set_from_file(self.path)
                self.pixbuf = self.image.get_pixbuf()
                #draw the image
                self.drawing_area.window.draw_pixbuf(self.gc, self.pixbuf, \
                                                0, 0, 0, 0, -1, -1)
            except Exception:
                print "picture " + str(pic_num) + " crop " + str(crop_num) + \
                    " is corrupt!"
        else:
            #draw an it's not done image
            print "it aint done fool"
            
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
        pass
        
    def _handle_search_resumed(self):
        pass
        
    def _handle_locked_target(self):
        pass
        
    def _handle_downloaded_to_flc(self, picture_count):
        pass
        
    def _handle_crop_generated(self, picture_num, crop_num):
        pass
        
    def _handle_image_downloaded(self, picture_num, crop_num, percent_complete):
        pass
        
    def _handle_ping(self, latency):
        print "ping latency was: %sms" % (latency,)
        
    def _handle_interface_error(self, msg, function):
        print "interface error from function \'%s\': \"%s\"" % (function, msg)
