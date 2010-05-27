#ImageStation.py
# change gtk.entry colors: http://bytes.com/topic/python/answers/540122-gtk-entry-colors

#import required modules
import sys
import os.path
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import glib

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
        self.saved = True
        
        # Set the model
        self.communicator = communicator
        
        # for tracking the number of identified targets
        self.num_targets = 0
        self.user_toggled = True
        
        # Configure the GUI with Glade
        self.initialize_gui()
        
        #debugging load
        self.communicator.load_project('/home/cogan/Desktop/newISP/save_file.isp')
        self.project_loaded()
        
        # Configure update handler
        self.update_dic = {"PICTURE_TAKEN" : self._handle_picture_taken, \
            "SEARCH_RESUMED" : self._handle_search_resumed, \
            "LOCKED_TARGET" : self._handle_locked_target, \
            "DOWNLOADED_TO_FLC" : self._handle_downloaded_to_flc, \
            "CROP_GENERATED" : self._handle_crop_generated, \
            "INFO_RECEIVED" : self._handle_info_received, \
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
        #* Get top level window
        #*
        
        self.window = self.widgets.get_widget("ImageWindow")
        self.window.set_title("Image Station")
        
        #*
        #* Set up Dialogs
        #*
        
        self.new_chooser = self.widgets.get_widget("new_dialog")
        self.open_chooser = self.widgets.get_widget("open_dialog")

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
        #* Set up play/pause button
        #*
        
        self.play_pause = self.widgets.get_widget("play_pause")
        play_image = gtk.Image()
        
        play_image.set_from_file("images/play.png")
        play_image.show()
        self.play_pause.set_image(play_image)
        
        self.paused = False
        
        #*
        #* Set up ImageTree_Menu
        #*
        
        self.image_tree_menu = self.widgets.get_widget("image_tree_menu")
        
        #*
        #* Set up Drawing Area
        #*
        
        self.drawing_area = self.widgets.get_widget("drawing_area")
        cross_cursor = gtk.gdk.Cursor(gtk.gdk.CROSS)
        self.drawing_area.window.set_cursor(cross_cursor)
        self.drawing_area_mode = "GENERATE_CROP"
        
        # style and gc
        self.style = self.drawing_area.get_style()
        self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
        
        # create background for drawing area
        image = gtk.Image()
        filename = "%s/images/blank.jpg" % (os.path.dirname(__file__),)
        self.pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, 800, 600)
        
        # for keeping track of crop areas
        self.box_drawn = False
        self.button_pressed = False
        self.xa = 0
        self.ya = 0
        self.xb = 0
        self.yb = 0
        
        # disable image window to start
        self.image_viewport = self.widgets.get_widget("image_viewport")
        self.image_viewport.set_sensitive(False)
        
        #*
        #* Set up Target
        #*
        
        self.target_viewport = self.widgets.get_widget("target_viewport")
        self.target_viewport.set_sensitive(False)
        
        self.picture_shape = self.widgets.get_widget("picture_shape_entry")
        self.picture_color = self.widgets.get_widget("picture_color_entry")
        self.picture_alpha = self.widgets.get_widget("picture_alpha_entry")
        self.picture_alphacolor = self.widgets.get_widget("picture_alphacolor_entry")
        self.picture_orientation = self.widgets.get_widget("picture_orientation_entry")
        self.picture_longitude = self.widgets.get_widget("picture_long_entry")
        self.picture_latitude = self.widgets.get_widget("picture_lat_entry")
        
        self.picture_shape.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
        self.picture_color.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
        self.picture_alpha.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
        self.picture_alphacolor.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
        self.picture_orientation.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
        self.picture_longitude.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
        self.picture_latitude.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
        
        self.include_target = self.widgets.get_widget("include_target")
        self.target_number = self.widgets.get_widget("target_number")
        
        #*
        #* Connect events
        #*
        
        file_dic = { "on_file_menu_new_activate" : self.file_menu_new_activate, \
                "on_file_menu_open_activate" : self.file_menu_open_activate, \
                "on_file_menu_save_activate" : self.file_menu_save_activate, \
                "on_file_menu_quit_activate" : self.file_menu_quit_activate }
                
        connection_menu_none.connect("activate", self.connection_menu_none_activate)
        connection_menu_serial.connect("activate", self.connection_menu_serial_activate)
        connection_menu_debug.connect("activate", self.connection_menu_debug_activate)
            
        view_dic = { "on_view_menu_cc_activate" : self.view_menu_cc_activate }
            
        help_dic = { "on_help_menu_about_activate" : self.help_menu_about_activate }
            
        tool_dic = { "on_tool_new_clicked" : self.tool_new_clicked, \
                "on_tool_open_clicked" : self.tool_open_clicked, \
                "on_tool_save_clicked" : self.tool_save_clicked, \
                "on_tool_dl2flc_clicked" : self.tool_dl2flc_clicked, \
                "on_tool_gen_crop_clicked" : self.tool_gen_crop_clicked, \
                "on_tool_identify_target_clicked" : self.tool_identify_target_clicked, \
                "on_tool_save_target_info_clicked" : self.tool_save_target_info_clicked }
                
        chooser_dic = { "on_nd_ok_clicked" : self.nd_ok_clicked, \
                "on_nd_cancel_clicked" : self.nd_cancel_clicked, \
                "on_od_open_clicked" : self.od_open_clicked, \
                "on_od_cancel_clicked" : self.od_cancel_clicked }
        
        image_tree_dic = { "on_image_tree_button_press_event" : self.image_tree_button_press_event, \
                "on_image_tree_menu_display_activate" : self.image_tree_menu_display_activate, \
                "on_image_tree_menu_add_to_queue_activate" : self.image_tree_menu_add_to_queue_activate }
        
        image_queue_dic = { "on_image_queue_key_press_event" : self.image_queue_key_press_event, \
                "on_image_queue_drag_end" : self.image_queue_drag_end }
        
        button_dic = { "on_play_pause_toggled" : self.play_pause_toggled }
        
        drawing_dic = { "on_drawing_area_expose_event" : self.drawing_area_expose_event, \
                "on_drawing_area_button_press_event" : self.drawing_area_button_press_event, \
                "on_drawing_area_button_release_event" : self.drawing_area_button_release_event, \
                "on_drawing_area_motion_notify_event" : self.drawing_area_motion_notify_event }
        
        picture_info_dic = { "on_picture_shape_entry_button_press_event" : self.shape_entry_button_press_event, \
                "on_picture_shape_entry_focus_out_event" : self.shape_entry_focus_out_event, \
                "on_picture_shape_entry_key_press_event" : self.shape_entry_key_press_event, \
                "on_picture_color_entry_button_press_event" : self.color_entry_button_press_event, \
                "on_picture_color_entry_focus_out_event" : self.color_entry_focus_out_event, \
                "on_picture_color_entry_key_press_event" : self.color_entry_key_press_event, \
                "on_picture_alpha_entry_button_press_event" : self.alpha_entry_button_press_event, \
                "on_picture_alpha_entry_focus_out_event" : self.alpha_entry_focus_out_event, \
                "on_picture_alpha_entry_key_press_event" : self.alpha_entry_key_press_event, \
                "on_picture_alphacolor_entry_button_press_event" : self.alphacolor_entry_button_press_event, \
                "on_picture_alphacolor_entry_focus_out_event" : self.alphacolor_entry_focus_out_event, \
                "on_picture_alphacolor_entry_key_press_event" : self.alphacolor_entry_key_press_event, \
                "on_picture_orientation_entry_button_press_event" : self.orientation_entry_button_press_event, \
                "on_picture_orientation_entry_focus_out_event" : self.orientation_entry_focus_out_event, \
                "on_picture_orientation_entry_key_press_event" : self.orientation_entry_key_press_event, \
                "on_include_target_toggled" : self.include_target_toggled }
        
        general_dic = { "on_ImageWindow_delete_event" : self.image_window_delete_event, \
                        "on_ImageWindow_destroy" : self.image_window_destroy }
        
        self.widgets.signal_autoconnect(file_dic)
        self.widgets.signal_autoconnect(view_dic)
        self.widgets.signal_autoconnect(help_dic)
        self.widgets.signal_autoconnect(tool_dic)
        self.widgets.signal_autoconnect(chooser_dic)
        self.widgets.signal_autoconnect(image_tree_dic)
        self.widgets.signal_autoconnect(image_queue_dic)
        self.widgets.signal_autoconnect(button_dic)
        self.widgets.signal_autoconnect(drawing_dic)
        self.widgets.signal_autoconnect(picture_info_dic)
        self.widgets.signal_autoconnect(general_dic)
    
    #*
    #* File Events
    #*
    
    def file_menu_new_activate(self, widget, data=None):
        """new clicked on file menu."""
        self.new_chooser.show()
    
    def file_menu_open_activate(self, widget, data=None):
        """open clicked on file menu."""
        self.open_chooser.show()
        
    def file_menu_save_activate(self, widget, data=None):
        """save clicked on file menu."""
        self.communicator.save_project()
        self.saved = True
    
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
    #* Help Events
    #*
            
    def help_menu_about_activate(self, widget, data=None):
        """about clicked on help menu."""
        print "cmon"
        button1 = gtk.Button("Press Me!")
        self.fixed1.put(button1, 0, 0)
        button1.window.raise_()
        button1.show()
        button2 = gtk.Button("Prease Press Me!")
        self.fixed1.put(button2, 380, 380)
        button2.show()
        button2.window.raise_()

    #*
    #* Toolbar events
    #*
    
    def tool_new_clicked(self, widget, data=None):
        """new clicked on toolbar menu."""
        self.new_chooser.show()
        
    def tool_open_clicked(self, widget, data=None):
        """open clicked on the toolbar menu."""
        self.open_chooser.show()
        
    def tool_save_clicked(self, widget, data=None):
        """save clicked on the toolbar menu."""
        self.communicator.save_project()
        self.saved = True
        
    def tool_dl2flc_clicked(self, widget, data=None):
        """dl2flc clicked on the toolbar menu."""
        self._download_to_flc()

    def tool_gen_crop_clicked(self, widget, data=None):
        """generate crop clicked on the toolbar menu."""
        self._generate_crop()
        
    def tool_identify_target_clicked(self, widget, data=None):
        """identify target clicked on the toolbar menu."""
        self._identify_target()
        
    def tool_save_target_info_clicked(self, widget, data=None):
        """save target info clicked on the toolbar menu."""
        self._save_target_info()

    #*
    #* File Chooser Dialog events
    #*
    
    def nd_ok_clicked(self, widget, data=None):
        """save clicked in file choose dialog."""
        filename = self.new_chooser.get_filename()
        self.communicator.new_project(filename)
        self.new_chooser.hide()
        self.project_loaded()
    
    def nd_cancel_clicked(self, widget, data=None):
        """cancel clicked in file choose dialog."""
        self.new_chooser.hide()
    
    def od_open_clicked(self, widget, data=None):
        """save clicked in file choose dialog."""
        filename = self.open_chooser.get_filename()
        if (self.communicator.load_project(filename)):
            self.open_chooser.hide()
        self.project_loaded()
        
    def od_cancel_clicked(self, widget, data=None):
        """cancel clicked in file choose dialog."""
        self.open_chooser.hide()
        
    def sd_yes_clicked(self, widget, data=None):
        """cancel clicked on "are you sure you want to save?" dialog"""
        return True
        
    def sd_cancel_clicked(self, widget, data=None):
        """cancel clicked in file choose dialog."""
        self.open_chooser.hide()
    
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
        self.image_viewport.set_sensitive(True)
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
    #* Button Events
    #*

    def play_pause_toggled(self, widget, data=None):
        if self.paused == True:
            self.paused = False
            self.queue_changed()
        else:
            self.paused = True

    #*
    #* Drawing Area events
    #*

    def drawing_area_expose_event(self, widget, event):
        #x, y, width, height = widget.get_allocation()
        if self.image_viewport.get_property('sensitive') == False:
            self.drawing_area.window.draw_pixbuf(self.gc, self.pixbuf, \
                                                            0, 0, 0, 0, -1, -1)
        else:
            self.redraw_current_image()
                  
    def drawing_area_button_press_event(self, widget, event):
        """button pressed in drawing area"""
        if self.drawing_area_mode == "GENERATE_CROP":
            if event.button == 1 and self.pixbuf != None:
                self.button_pressed = True
                
                if self.box_drawn == True:
                    # clear the screen
                    self.redraw_current_image()
                    
                # current coordinates
                self.x_begin = int(event.x)
                self.y_begin = int(event.y)
        
        if self.drawing_area_mode == "IDENTIFY_TARGET":
            if event.button == 1 and self.pixbuf != None:
                # get pixel coordinates
                print "x: %d, y: %d" % (int(event.x), int(event.y),)
                x = int(event.x)
                y = int(event.y)
                
                # redraw to remove any existing targets
                self.drawing_area.window.draw_pixbuf(self.gc, self.pixbuf, \
                                                            0, 0, 0, 0, -1, -1)
                
                # draw target on image
                # TODO: make it cooler
                self.drawing_area.window.draw_arc(self.gc, False, x-10, y-10, 20, 20, 0, 360*64)
                self.drawing_area.window.draw_arc(self.gc, False, x-20, y-20, 40, 40, 0, 360*64)
                
                # create target
                crop = self.communicator.image_store.get_crop(self.cd_pic_num, \
                                                    self.cd_crop_num)
                crop.set_target(x, y)
                self.update_target_info(self.cd_pic_num, self.cd_crop_num)
            
                # go back to generate crop mode
                self.drawing_area_mode = "GENERATE_CROP_TRANSITION"
                cross_cursor = gtk.gdk.Cursor(gtk.gdk.CROSS)
                self.drawing_area.window.set_cursor(cross_cursor)
            
            # on right click go back to generate crop mode
            elif event.button == 3:
                self.drawing_area_mode = "GENERATE_CROP"
                cross_cursor = gtk.gdk.Cursor(gtk.gdk.CROSS)
                self.drawing_area.window.set_cursor(cross_cursor)
                

    def drawing_area_motion_notify_event(self, widget, event):
        if self.drawing_area_mode == "GENERATE_CROP":
            if (self.button_pressed == True) & (self.pixbuf != None):
                #current coordinates
                self.x_end = int(event.x)
                self.y_end = int(event.y)
                
                #draw the box
                self.draw_box(widget, self.x_begin, self.y_begin, \
                                        self.x_end, self.y_end)
    
    def drawing_area_button_release_event(self, widget, event):
        """button released in drawing area"""
        if self.drawing_area_mode == "GENERATE_CROP":
            if event.button == 1 and self.pixbuf != None:
                self.button_pressed = False
                
                #current ending coordinates
                self.x_end = int(event.x)
                self.y_end = int(event.y)
                
                #draw the box
                self.draw_box(widget, self.x_begin, self.y_begin, \
                                        self.x_end, self.y_end)
        
        if self.drawing_area_mode == "GENERATE_CROP_TRANSITION":
            self.drawing_area_mode = "GENERATE_CROP"
    
    
    #*
    #* Picture Info Box Events
    #*

    def shape_entry_button_press_event(self, widget, event, data=None):
        """picture info entry box double clicked"""
        
        # check for double click
        # if so make the widget editable and change its color
        if event.type == gtk.gdk._2BUTTON_PRESS:
            widget.set_editable(True)
            widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
    
    def shape_entry_focus_out_event(self, widget, data=None):
        """focus lost on shape entry"""
        widget.set_editable(False)
        widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
        crop = self.communicator.image_store.get_crop(self.cd_pic_num, \
                                                    self.cd_crop_num)
        crop.target.shape = widget.get_text()

    def shape_entry_key_press_event(self, widget, event, data=None):
        """key press"""
        if event.keyval == 65293:
            if widget.get_editable() == False:
                widget.set_editable(True)
                widget.select_region(0, len(widget.get_text()))
                widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            elif widget.get_editable() == True:
                widget.set_editable(False)
                widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
                crop = self.communicator.image_store.get_crop(self.cd_pic_num, \
                                                        self.cd_crop_num)
                crop.target.shape = widget.get_text()
                
    def color_entry_button_press_event(self, widget, event, data=None):
        """picture info entry box double clicked"""
        
        # check for double click
        # if so make the widget editable and change its color
        if event.type == gtk.gdk._2BUTTON_PRESS:
            widget.set_editable(True)
            widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
    
    def color_entry_focus_out_event(self, widget, data=None):
        """focus lost on color entry"""
        widget.set_editable(False)
        widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
        crop = self.communicator.image_store.get_crop(self.cd_pic_num, \
                                                    self.cd_crop_num)
        crop.target.color = widget.get_text()

    def color_entry_key_press_event(self, widget, event, data=None):
        """key press"""
        if event.keyval == 65293:
            if widget.get_editable() == False:
                widget.set_editable(True)
                widget.select_region(0, len(widget.get_text()))
                widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            elif widget.get_editable() == True:
                widget.set_editable(False)
                widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
                crop = self.communicator.image_store.get_crop(self.cd_pic_num, \
                                                        self.cd_crop_num)
                crop.target.color = widget.get_text()
    
    def alpha_entry_button_press_event(self, widget, event, data=None):
        """picture info entry box double clicked"""
        
        # check for double click
        # if so make the widget editable and change its color
        if event.type == gtk.gdk._2BUTTON_PRESS:
            widget.set_editable(True)
            widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
    
    def alpha_entry_focus_out_event(self, widget, data=None):
        """focus lost on alpha entry"""
        widget.set_editable(False)
        widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
        crop = self.communicator.image_store.get_crop(self.cd_pic_num, \
                                                    self.cd_crop_num)
        crop.target.alpha = widget.get_text()

    def alpha_entry_key_press_event(self, widget, event, data=None):
        """key press"""
        if event.keyval == 65293:
            if widget.get_editable() == False:
                widget.set_editable(True)
                widget.select_region(0, len(widget.get_text()))
                widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            elif widget.get_editable() == True:
                widget.set_editable(False)
                widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
                crop = self.communicator.image_store.get_crop(self.cd_pic_num, \
                                                        self.cd_crop_num)
                crop.target.alpha = widget.get_text()
                
    def alphacolor_entry_button_press_event(self, widget, event, data=None):
        """picture info entry box double clicked"""
        
        # check for double click
        # if so make the widget editable and change its color
        if event.type == gtk.gdk._2BUTTON_PRESS:
            widget.set_editable(True)
            widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
    
    def alphacolor_entry_focus_out_event(self, widget, data=None):
        """focus lost on alphacolor entry"""
        widget.set_editable(False)
        widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
        crop = self.communicator.image_store.get_crop(self.cd_pic_num, \
                                                    self.cd_crop_num)
        crop.target.alphacolor = widget.get_text()

    def alphacolor_entry_key_press_event(self, widget, event, data=None):
        """key press"""
        if event.keyval == 65293:
            if widget.get_editable() == False:
                widget.set_editable(True)
                widget.select_region(0, len(widget.get_text()))
                widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            elif widget.get_editable() == True:
                widget.set_editable(False)
                widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
                crop = self.communicator.image_store.get_crop(self.cd_pic_num, \
                                                        self.cd_crop_num)
                crop.target.alphacolor = widget.get_text()

    def orientation_entry_button_press_event(self, widget, event, data=None):
        """picture info entry box double clicked"""
        
        # check for double click
        # if so make the widget editable and change its color
        if event.type == gtk.gdk._2BUTTON_PRESS:
            widget.set_editable(True)
            widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
    
    def orientation_entry_focus_out_event(self, widget, data=None):
        """focus lost on orientation entry"""
        widget.set_editable(False)
        widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
        crop = self.communicator.image_store.get_crop(self.cd_pic_num, \
                                                    self.cd_crop_num)
        crop.target.orientation = widget.get_text()

    def orientation_entry_key_press_event(self, widget, event, data=None):
        """key press"""
        if event.keyval == 65293:
            if widget.get_editable() == False:
                widget.set_editable(True)
                widget.select_region(0, len(widget.get_text()))
                widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
            elif widget.get_editable() == True:
                widget.set_editable(False)
                widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6D6D6"))
                crop = self.communicator.image_store.get_crop(self.cd_pic_num, \
                                                        self.cd_crop_num)
                crop.target.orientation = widget.get_text()
                
    def include_target_toggled(self, widget, data=None):
        """include target button toggled"""
        print "number of targets before click is %d" % (self.num_targets,)
        crop = self.communicator.image_store.get_crop(self.cd_pic_num, 
                                                        self.cd_crop_num)
        # if toggled on we need to display the target num and update Target
        if self.include_target.get_active() == True:
            if self.user_toggled == True:
                self.num_targets += 1
                self.target_number.set_text("target 0" + str(self.num_targets))
                crop.target.included = True
                crop.target.number = self.num_targets
        else:
            if self.user_toggled == True:
                self.num_targets -= 1
                self.target_number.set_text("")
                crop.target.included = False
                crop.target.number = 0
       
        print "number of targets after click is %d" % (self.num_targets,)

    #*
    #* General events
    #*
    
    def image_window_delete_event(self, widget, data=None):
        if (self.saved == False):
            dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, \
            gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO, \
            "The current project has not been saved!")
            dialog.format_secondary_text("Are you sure you want to quit without saving?")
            
            dialog.set_title(":(")

            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                return False
            else:
                return True
                
    def image_window_destroy(self, widget, data=None):
        """window was destroyed, exit the program."""
        self._quit()

    #*
    #* Functions related to file manipulation
    #*
    
    def project_loaded(self):
        # clear the current treeview and listview
        while 1:
            iters = self.tree_store.get_iter_first()
            if not iters:
                break
            self.tree_store.remove(iters)
        
        while 1:
            iters = self.list_store.get_iter_first()
            if not iters:
                break
            self.list_store.remove(iters)
        
        # determine the current state of each picture and handle accordingly
        for pic_num in range(0, self.communicator.image_store.picture_count):
            
            pic = self.communicator.image_store.get_picture(pic_num)
            
            for crop_num in range(1, pic.num_crops()):
                # get crop
                crop = pic.get_crop(crop_num)
                
                # insert into tree
                if crop_num == 1:
                    self.insert_in_tree(crop.name, pic_num, crop_num, False)
                    if crop.available == True:
                        self.tree_store[pic_num][0] = \
                            '<span foreground="#000000"><b>' + crop.name + '</b></span>'
                else:
                    self.insert_in_tree(crop.name, pic_num, crop_num, True)
                
                # insert into queue?
                if crop.inqueue == True:
                    crop.inqueue = False
                    self.add_to_queue(crop.name, pic_num, crop_num)
                
                # update the progress
                if crop.size > 0:
                    if crop_num == 1:
                        #it's the parent/thumbnail, just do it
                        self.tree_store[pic_num][3] = str(crop.get_percent_complete()) + "%"
                    else:
                        #it's a child, cycle through the array to find it
                        parent = self.tree_store[pic_num].iter
                        n=0
                        childiter = self.tree_store.iter_nth_child(parent, n)
                        while (self.tree_store.get_value(childiter, 2) != crop_num):
                            n += 1
                            childiter = self.tree_store.iter_nth_child(parent, n)
                        self.tree_store.set_value(childiter, 3, str(crop.get_percent_complete()) + "%")
    
        # set the title of the window to be the project path
        self.window.set_title("Image Station - " + \
            self.communicator.image_store.project_path)
    
        self.saved = True
    
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
    
    def _identify_target(self):
        """identify a target on the image"""
        
        # change the cursor for the drawing area
        x_cursor = gtk.gdk.Cursor(gtk.gdk.X_CURSOR)
        self.drawing_area.window.set_cursor(x_cursor)
        
        # set the drawing area mode
        self.drawing_area_mode = "IDENTIFY_TARGET"
        
        #clear the screen
        if self.box_drawn == True:
            self.redraw_current_image()
    
    def _save_target_info(self):
        """save all the target info to a file"""
        #TODO: this
        print "did NOT save info to file cause this shit isn't done"
    
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
            if not self.paused == True:
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
                self.pixbuf = gtk.gdk.pixbuf_new_from_file(path)
                w = self.pixbuf.get_width()
                h = self.pixbuf.get_height()
                
                # draw the image
                self.drawing_area.window.draw_pixbuf(self.gc, self.pixbuf, \
                                                    0, 0, 0, 0, w, h)
                self.drawing_area.window.resize(w, h)
                
                # render the target and compass
                self.draw_target(pic_num, crop_num)
                
            except glib.GError as e:
                print "picture " + str(pic_num) + " crop " + str(crop_num) + \
                    " is corrupt!"
        else:
            #draw "incomplete" image
            path = "%s/images/incomplete.jpg" % (os.path.dirname(__file__),)
            self.pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 800, 600)
            w = self.pixbuf.get_width()
            h = self.pixbuf.get_height()
            #draw the image
            self.drawing_area.window.draw_pixbuf(self.gc, self.pixbuf, \
                                                0, 0, 0, 0, w, h)
        
        # show the picture info and update it
        self.update_target_info(pic_num, crop_num)

    def redraw_current_image(self):
        self.drawing_area.window.draw_pixbuf(self.gc, self.pixbuf, \
                                                    0, 0, 0, 0, -1, -1)
        self.draw_target(self.cd_pic_num, self.cd_crop_num)

    def draw_target(self, pic_num, crop_num):
            crop = self.communicator.image_store.get_crop(pic_num, crop_num)
            if crop.target != None:
                x = crop.target.x_coord
                y = crop.target.y_coord
                self.drawing_area.window.draw_arc(self.gc, False, x-10, y-10, 20, 20, 0, 360*64)
                self.drawing_area.window.draw_arc(self.gc, False, x-20, y-20, 40, 40, 0, 360*64)

    def update_target_info(self, pic_num, crop_num):
        """update the fields containing a pictures info"""
        crop = self.communicator.image_store.get_crop(pic_num, crop_num)
        
        # get the attributes from the picture
        if crop.target != None:
            self.target_viewport.set_sensitive(True)
            self.picture_shape.set_text(crop.target.shape)
            self.picture_color.set_text(crop.target.color)
            self.picture_alpha.set_text(crop.target.alpha)
            self.picture_alphacolor.set_text(crop.target.alphacolor)
            self.picture_orientation.set_text(crop.target.orientation)
            self.picture_longitude.set_text(crop.target.longitude)
            self.picture_latitude.set_text(crop.target.latitude)
            if crop.target.included == True:
                self.user_toggled = False
                self.include_target.set_active(True)
                self.user_toggled = True
                self.target_number.set_text("target 0" + str(crop.target.number))
            else:
                self.user_toggled = False
                self.include_target.set_active(False)
                self.user_toggled = True
                self.target_number.set_text("")
        else:
            self.target_viewport.set_sensitive(False)
            self.picture_shape.set_text("")
            self.picture_color.set_text("")
            self.picture_alpha.set_text("")
            self.picture_alphacolor.set_text("")
            self.picture_orientation.set_text("")
            self.picture_longitude.set_text("")
            self.picture_latitude.set_text("")
            self.user_toggled = False
            self.include_target.set_active(False)
            self.user_toggled = True
            self.target_number.set_text("")

    def draw_box(self, widget, x_begin, y_begin, x_end, y_end):
        self.box_width = self.x_end - self.x_begin
        self.box_height = self.y_end - self.y_begin
        #erase previous box
        #TODO: this is extremely slow... need to use cairo
        self.redraw_current_image()
        #box drawn from bottom right to top left
        if ((self.box_width < 0) & (self.box_height < 0)):
            self.xa = self.x_end
            self.ya = self.y_end
            self.xb = self.xa + abs(self.box_width)
            self.yb = self.ya + abs(self.box_height)
            widget.window.draw_rectangle(self.gc, False, \
                        self.xa, self.ya, \
                        abs(self.box_width), abs(self.box_height))
            self.box_drawn = True
        #box drawn top right to bottom left
        elif ((self.box_width < 0) & (self.box_height > 0)):
            self.xa = self.x_begin + self.box_width
            self.ya = self.y_begin
            self.xb = self.xa + abs(self.box_width)
            self.yb = self.ya + abs(self.box_height)    
            widget.window.draw_rectangle(self.gc, False, \
                        self.xa, self.ya, \
                        abs(self.box_width), abs(self.box_height))
            self.box_drawn = True
        #box drawn from bottom left to top right
        elif ((self.box_width > 0) & (self.box_height < 0)):
            self.xa = self.x_begin
            self.ya = self.y_begin + self.box_height
            self.xb = self.xa + abs(self.box_width)
            self.yb = self.ya + abs(self.box_height)    
            widget.window.draw_rectangle(self.gc, False, \
                        self.xa, self.ya, \
                        abs(self.box_width), abs(self.box_height))
            self.box_drawn = True  
        #box drawn from top left to bottom right              
        elif ((self.box_width > 0) & (self.box_height > 0)):
            self.xa = self.x_begin
            self.ya = self.y_begin
            self.xb = self.xa + abs(self.box_width)
            self.yb = self.ya + abs(self.box_height)  
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
            self.saved = False
        except KeyError as e:
            pass

    def _handle_picture_taken(self, picture_num):
        #add the picture to tree!
        picture_name = self.communicator.image_store.get_crop(picture_num, 1).name
        self.insert_in_tree(picture_name, picture_num, 1, False)
        self.add_to_queue(picture_name, picture_num, 1)
        
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
        
    def _handle_info_received(self, picture_num, gps_x, gps_y, pan, tilt, yaw, pitch, roll):
        print "info received, gps_x: %f, gps_y: %f" % (gps_x, gps_y)
    
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
