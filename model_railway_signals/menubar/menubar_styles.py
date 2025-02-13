#------------------------------------------------------------------------------------
# This module contains all the functions for the menubar Styles windows
# 
# Classes (pop up windows) called from the main editor module menubar selections
#    edit_section_styles
#    edit_route_styles
#    edit_switch_styles
#    edit_route_line_styles
#    edit_point_styles
#    edit_signal_styles
#    edit_lever_styles
#    edit_textbox_styles
#
# Makes the following external API calls to other editor modules:
#    schematic.get_selected_objects
#    settings.get_default_style
#    settings.get_style
#    settings.set_style
#    objects.update_styles
#
# Accesses the following elements directly from other editor modules:
#    objects.object_type
#    objects.section_index
#    objects.route_index
#    objects.switch_index
#    objects.point_index
#    objects.line_index
#    objects.signal_index
#    objects.textbox_index
#
# Uses the following common editor UI elements:
#    common.CreateToolTip
#    common.colour_selection
#    common.selection_buttons
#    common.font_selection
#    common.font_style_selection
#    common.integer_entry_box
#    common.entry_box
#
#------------------------------------------------------------------------------------

import tkinter as Tk

from .. import common
from .. import objects
from .. import schematic
from .. import settings

#------------------------------------------------------------------------------------
# Class for the common_buttons UI Element
#------------------------------------------------------------------------------------

class common_buttons(Tk.Frame):
    def __init__(self, parent_frame, load_app_defaults_callback, load_layout_defaults_callback,
                 apply_all_callback, apply_selected_callback, set_defaults_callback, close_window_callback):
        super().__init__(parent_frame)
        # Create a Frame for the "reset" buttons
        self.frame3 = Tk.Frame(self)
        self.frame3.pack(fill="x")
        # Create a subframe to center the buttons in
        self.button1 = Tk.Button(self.frame3, text="Load app defaults", width=17, command=load_app_defaults_callback)
        self.button1.pack(padx=5, pady=2, side=Tk.LEFT, fill="x", expand=True)
        self.button1TT = common.CreateToolTip(self.button1, "Click to load the application defaults")
        self.button2 = Tk.Button(self.frame3, text="Load layout defaults", width=17, command=load_layout_defaults_callback)
        self.button2.pack(padx=5, pady=2, side=Tk.LEFT, fill="x", expand=True)
        self.button2TT = common.CreateToolTip(self.button2, "Click to load the current layout defaults")
        # Create a Frame for the apply Buttons
        self.frame4 = Tk.Frame(self)
        self.frame4.pack(fill="x")
        self.button3 = Tk.Button(self.frame4, text="Apply to all", command=apply_all_callback)
        self.button3.pack(padx=5, pady=2, side=Tk.LEFT, fill="x", expand=True)
        self.button3TT = common.CreateToolTip(self.button3, "Select to apply the above settings to ALL objects")
        self.button4 = Tk.Button(self.frame4, text="Apply to selected", command=apply_selected_callback)
        self.button4.pack(padx=5, pady=2, side=Tk.LEFT, fill="x", expand=True)
        self.button4TT = common.CreateToolTip(self.button4, "Select to apply the above settings to SELECTED objects")
        # Add the button to set new layout defaults
        self.button5 = Tk.Button(self.frame4, text="Set as defaults", command=set_defaults_callback)
        self.button5.pack(padx=5, pady=2, fill="x", expand=True)
        self.button5TT = common.CreateToolTip(self.button5, "Select to save the above settings as the new layout defaults "+
                                                        "(which will be applied to new objects as they are created)")
        # Create the close window button and tooltip
        self.button6 = Tk.Button (self, text = "Close Window", command=close_window_callback)
        self.button6.pack(padx=2, pady=2)
        self.button6TT = common.CreateToolTip(self.button6, "Close window")
        
#------------------------------------------------------------------------------------
# Class for the common_style_settings UI Element
#------------------------------------------------------------------------------------

class common_style_settings(Tk.Frame):
    def __init__(self, parent_frame, object_type:str, max_font_size:int,
                    apply_all_callback, apply_selected_callback, close_window_callback):
        self.object_type = object_type
        # Create the frame
        super().__init__(parent_frame)
        # Create a Frame for the button colour and text colour elements (Frame 3)
        self.frame1 = Tk.Frame(self)
        self.frame1.pack(fill='x', padx=2)
        self.widgetcolour = common.colour_selection(self.frame1, label="Background colour")
        self.widgetcolour.pack(side=Tk.LEFT, padx=2, pady=2, fill="x", expand=True)
        self.textcolourtype = common.selection_buttons(self.frame1, label="Text colour",
                    tool_tip="Select the text colour (auto to select 'best' contrast with background)",
                    button_labels=("Auto", "Black", "White"))
        self.textcolourtype.pack(side=Tk.LEFT, padx=2, pady=2, fill='both', expand=True)
        # Create the Font selection element
        self.textfont=common.font_selection(self, label="Text font")
        self.textfont.pack(padx=4, pady=2, fill="x")
        # Create a Frame for the font size and text style elements (Frame 4)
        self.frame2 = Tk.Frame(self)
        self.frame2.pack(padx=2, fill='x')
        # Create a Label Frame for the Font Size Entry components
        self.frame2subframe1 = Tk.LabelFrame(self.frame2, text="Font size")
        self.frame2subframe1.pack(side=Tk.LEFT, padx=2, pady=2, fill="x", expand=True)
        # Create a subframe to center the font size elements in
        self.frame2subframe2 = Tk.Frame(self.frame2subframe1)
        self.frame2subframe2.pack()
        self.frame2subframe2label1 = Tk.Label(self.frame2subframe2, text="Pixels:")
        self.frame2subframe2label1.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
        self.fontsize = common.integer_entry_box(self.frame2subframe2, width=3, min_value=8, max_value=max_font_size,
               tool_tip="Select the font size (between 8 and "+str(max_font_size)+" pixels)", allow_empty=False)
        self.fontsize.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
        # The final label frame is for the text style selection
        self.fontstyle = common.font_style_selection(self.frame2, label="Font style")
        self.fontstyle.pack(padx=2, pady=2, side=Tk.LEFT, fill='x', expand=True)
        # Create the common button elements
        self.buttons = common_buttons(parent_frame, self.load_app_defaults, self.load_layout_defaults,
                        apply_all_callback, apply_selected_callback, self.set_defaults, close_window_callback)
        self.buttons.pack(side=Tk.BOTTOM, fill='x')

    def set_defaults(self):
        if self.validate():
            font_tuple = (self.textfont.get_value(), self.fontsize.get_value(), self.fontstyle.get_value())
            settings.set_style(self.object_type,"textfonttuple", font_tuple)
            settings.set_style(self.object_type,"textcolourtype", self.textcolourtype.get_value())
            settings.set_style(self.object_type,"buttoncolour", self.widgetcolour.get_value())
        
    def load_app_defaults(self):
        self.textfont.set_value(settings.get_default_style(self.object_type,"textfonttuple")[0])
        self.fontsize.set_value(settings.get_default_style(self.object_type,"textfonttuple")[1])
        self.fontstyle.set_value(settings.get_default_style(self.object_type,"textfonttuple")[2])
        self.textcolourtype.set_value(settings.get_default_style(self.object_type,"textcolourtype"))
        self.widgetcolour.set_value(settings.get_default_style(self.object_type,"buttoncolour"))
        
    def load_layout_defaults(self):
        self.textfont.set_value(settings.get_style(self.object_type,"textfonttuple")[0])
        self.fontsize.set_value(settings.get_style(self.object_type,"textfonttuple")[1])
        self.fontstyle.set_value(settings.get_style(self.object_type,"textfonttuple")[2])
        self.textcolourtype.set_value(settings.get_style(self.object_type,"textcolourtype"))
        self.widgetcolour.set_value(settings.get_style(self.object_type,"buttoncolour"))

    def get_values(self):
        styles_to_return = {}
        font_tuple = (self.textfont.get_value(), self.fontsize.get_value(), self.fontstyle.get_value())
        styles_to_return["textfonttuple"] = font_tuple
        styles_to_return["textcolourtype"] = self.textcolourtype.get_value()
        styles_to_return["buttoncolour"] = self.widgetcolour.get_value()
        return(styles_to_return)
        
    def validate(self):
        return(self.fontsize.validate())
    
#------------------------------------------------------------------------------------
# Class for the button_style_selections UI Element. Builds on the
# common_style_settings class with the addition of a button width entry
# Used for Track Sections, Route Buttons and DCC Switches
#------------------------------------------------------------------------------------

class button_style_selections(common_style_settings):
    def __init__(self, parent_frame, object_type:str, max_font_size:int,
                 apply_all_callback, apply_selected_callback, close_window_callback):
        # Create the basic style settings elements
        super().__init__(parent_frame, object_type, max_font_size, apply_all_callback,
                             apply_selected_callback, close_window_callback)
        # Create a Frame for the Button Width components
        self.frame2a = Tk.Frame(self)
        self.frame2a.pack(after=self.frame2, fill="x", expand=True)
        # Create The Label frame for the button width
        self.frame2asubframe1 = Tk.LabelFrame(self.frame2a, text="Button width")
        self.frame2asubframe1.pack (padx=2, pady=2, side=Tk.LEFT, fill="x", expand=True)
        # Create a subframe to center the font size elements in
        self.frame2asubframe2 = Tk.Frame(self.frame2asubframe1)
        self.frame2asubframe2.pack()
        self.frame2asubframe1label1 = Tk.Label(self.frame2asubframe2, text="Chars:")
        self.frame2asubframe1label1.pack(padx=2, pady=2, side=Tk.LEFT)
        self.buttonwidth = common.integer_entry_box(self.frame2asubframe2, width=3, min_value=5, max_value=25,
               tool_tip="Select the button width (between 5 and 25 characters)", allow_empty=False)
        self.buttonwidth.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)

    def set_defaults(self):
        if self.validate():
            super().set_defaults()
            settings.set_style(self.object_type,"buttonwidth", self.buttonwidth.get_value())
                
    def load_app_defaults(self):
        super().load_app_defaults()
        self.buttonwidth.set_value(settings.get_default_style(self.object_type,"buttonwidth"))
        
    def load_layout_defaults(self):
        super().load_layout_defaults()
        self.buttonwidth.set_value(settings.get_style(self.object_type,"buttonwidth"))

    def get_values(self):
        styles_to_return = super().get_values()
        styles_to_return["buttonwidth"] = self.buttonwidth.get_value()
        return(styles_to_return)

    def validate(self):
        return(super().validate() and self.buttonwidth.validate())

#------------------------------------------------------------------------------------
# Class for the track_section_style_selections UI Element. Builds on the
# button_style_selections class with the addition of a default label entry
#------------------------------------------------------------------------------------

class track_section_style_selections(button_style_selections):
    def __init__(self, parent_frame, object_type:str, apply_all_callback, apply_selected_callback, close_window_callback):
        # Create the parent style settings elements
        super().__init__(parent_frame, object_type, 14, apply_all_callback, apply_selected_callback, close_window_callback)
        # Create the default label elements
        self.frame2asubframe2 = Tk.LabelFrame(self.frame2a, text="Default section label")
        self.defaultlabel = common.entry_box(self.frame2asubframe2, width=30, tool_tip = "Enter the default "+
                                         "label to display when the Track Section is occupied")
        self.defaultlabel.pack(padx=2, pady=2)
        self.frame2asubframe2.pack(padx=2, pady=2, fill='x')

    def set_defaults(self):
        if self.validate():
            super().set_defaults()
            settings.set_style(self.object_type,"defaultlabel", self.defaultlabel.get_value())
                
    def load_app_defaults(self):
        super().load_app_defaults()
        self.defaultlabel.set_value(settings.get_default_style(self.object_type,"defaultlabel"))
        
    def load_layout_defaults(self):
        super().load_layout_defaults()
        self.defaultlabel.set_value(settings.get_style(self.object_type,"defaultlabel"))

    def get_values(self):
        styles_to_return = super().get_values()
        styles_to_return["defaultlabel"] = self.defaultlabel.get_value()
        return(styles_to_return)

    def validate(self):
        return(super().validate() and self.defaultlabel.validate())

#####################################################################################
    
#------------------------------------------------------------------------------------
# Class for the Track Section Style Settings toolbar window.
#------------------------------------------------------------------------------------

edit_section_styles_window = None
            
class edit_section_styles():
    def __init__(self, root_window):
        global edit_section_styles_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_section_styles_window is not None:
            edit_section_styles_window.lift()
            edit_section_styles_window.state('normal')
            edit_section_styles_window.focus_force()
        else:
            # Create the (non resizable) top level window
            self.window = Tk.Toplevel(root_window)
            self.window.title("Track Section Styles")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            edit_section_styles_window = self.window
            # Create the UI Elements
            self.styles = track_section_style_selections(self.window, object_type="tracksections",
                        apply_all_callback=self.apply_all, apply_selected_callback=self.apply_selected,
                        close_window_callback=self.close_window)
            self.styles.pack(padx=5, pady=5, fill='x')
            # Load the initial UI state
            self.styles.load_layout_defaults()

    def apply_all(self):
        if self.styles.validate():
            objects_to_update = list(objects.section_index.values())
            objects.update_styles(objects_to_update, self.styles.get_values())

    def apply_selected(self):
        if self.styles.validate():
            objects_to_update = schematic.get_selected_objects(object_type=objects.object_type.section)
            objects.update_styles(objects_to_update, self.styles.get_values())

    def close_window(self):
        global edit_section_styles_window
        if not self.styles.widgetcolour.is_open():
            edit_section_styles_window = None
            self.window.destroy()
        
#------------------------------------------------------------------------------------
# Class for the Route Button Style Settings toolbar window.
#------------------------------------------------------------------------------------

edit_route_styles_window = None
            
class edit_route_styles():
    def __init__(self, root_window):
        global edit_route_styles_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_route_styles_window is not None:
            edit_route_styles_window.lift()
            edit_route_styles_window.state('normal')
            edit_route_styles_window.focus_force()
        else:
            # Create the (non resizable) top level window
            self.window = Tk.Toplevel(root_window)
            self.window.title("Route Button Styles")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            edit_route_styles_window = self.window
            # Create the UI Elements
            self.styles = button_style_selections(self.window, object_type="routebuttons", max_font_size=20,
                    apply_all_callback=self.apply_all, apply_selected_callback=self.apply_selected,
                    close_window_callback=self.close_window)
            self.styles.pack(padx=5, pady=5, fill='x')
            # Load the initial UI state
            self.styles.load_layout_defaults()

    def apply_all(self):
        if self.styles.validate():
            objects_to_update = list(objects.route_index.values())
            objects.update_styles(objects_to_update, self.styles.get_values())

    def apply_selected(self):
        if self.styles.validate():
            objects_to_update = schematic.get_selected_objects(object_type=objects.object_type.route)
            objects.update_styles(objects_to_update, self.styles.get_values())

    def close_window(self):
        global edit_route_styles_window
        if not self.styles.widgetcolour.is_open():
            edit_route_styles_window = None
            self.window.destroy()
        
#------------------------------------------------------------------------------------
# Class for the DCC Switch Button Style Settings toolbar window.
#------------------------------------------------------------------------------------

edit_switch_styles_window = None
            
class edit_switch_styles():
    def __init__(self, root_window):
        global edit_switch_styles_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_switch_styles_window is not None:
            edit_switch_styles_window.lift()
            edit_switch_styles_window.state('normal')
            edit_switch_styles_window.focus_force()
        else:
            # Create the (non resizable) top level window
            self.window = Tk.Toplevel(root_window)
            self.window.title("DCC Switch Styles")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            edit_switch_styles_window = self.window
            # Create the UI Elements
            self.styles = button_style_selections(self.window, object_type="dccswitches", max_font_size=20,
                    apply_all_callback=self.apply_all, apply_selected_callback=self.apply_selected,
                    close_window_callback=self.close_window)
            self.styles.pack(padx=5, pady=5, fill='x')
            # Load the initial UI state
            self.styles.load_layout_defaults()

    def apply_all(self):
        if self.styles.validate():
            objects_to_update = list(objects.switch_index.values())
            objects.update_styles(objects_to_update, self.styles.get_values())

    def apply_selected(self):
        if self.styles.validate():
            objects_to_update = schematic.get_selected_objects(object_type=objects.object_type.switch)
            objects.update_styles(objects_to_update, self.styles.get_values())

    def close_window(self):
        global edit_switch_styles_window
        if not self.styles.widgetcolour.is_open():
            edit_switch_styles_window = None
            self.window.destroy()
            
#------------------------------------------------------------------------------------
# Class for the Route Line Styles toolbar window.
#------------------------------------------------------------------------------------

edit_route_line_styles_window = None
            
class edit_route_line_styles():
    def __init__(self, root_window):
        global edit_route_line_styles_window
        # If there is already a window open then we just make it jump to the top and exit
        if edit_route_line_styles_window is not None:
            edit_route_line_styles_window.lift()
            edit_route_line_styles_window.state('normal')
            edit_route_line_styles_window.focus_force()
        else:
            # Create the (non resizable) top level window
            self.window = Tk.Toplevel(root_window)
            self.window.title("Route & Point Lines")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            edit_route_line_styles_window = self.window
            # Create a subframe to center everything in
            self.frame1 = Tk.Frame(self.window)
            self.frame1.pack(fill='x')
            # Create the UI Elements
            self.colour = common.colour_selection(self.frame1, label="Default line colour")
            self.colour.pack(padx=5, pady=5, side=Tk.LEFT, fill='x', expand=True)
            # Create a Labelframe for the Line Width
            self.subframe1 = Tk.LabelFrame(self.frame1, text="Route line width")
            self.subframe1.pack(padx=5, pady=5, fill='both', expand=True, side=Tk.LEFT)
            # Create another subframe so all the other elements float in the labelframe
            self.subframe2 = Tk.Frame(self.subframe1)
            self.subframe2.pack(fill='y', expand=True)
            # Create a subframe to center the line width elements in
            self.label1 = Tk.Label(self.subframe2, text="Pixels:")
            self.label1.pack(padx=2, pady=2, side=Tk.LEFT)
            self.linewidth = common.integer_entry_box(self.subframe2, width=3, min_value=1, max_value=6,
                   tool_tip="Select the line width (between 1 and 6 pixels)", allow_empty=False)
            self.linewidth.pack(padx=2, pady=2, side=Tk.LEFT)
            # Create the common buttons
            self.buttons = common_buttons(self.window, self.load_app_defaults, self.load_layout_defaults,
                            self.apply_all, self.apply_selected, self.set_layout_defaults, self.close_window)
            self.buttons.pack(padx=5, pady=5, side=Tk.BOTTOM, fill='x', expand=True)
            # Load the initial UI state
            self.load_layout_defaults()
            
    def load_app_defaults(self):
        self.colour.set_value(settings.get_default_style("routelines", "colour"))
        self.linewidth.set_value(settings.get_default_style("routelines", "linewidth"))
        
    def load_layout_defaults(self):
        self.colour.set_value(settings.get_style("routelines", "colour"))
        self.linewidth.set_value(settings.get_style("routelines", "linewidth"))
        
    def set_layout_defaults(self):
        if self.linewidth.validate():
            settings.set_style("routelines","colour", self.colour.get_value())
            settings.set_style("routelines","linewidth", self.linewidth.get_value())

    def apply_all(self):
        if self.linewidth.validate():
            objects_to_update = list(objects.point_index.values())+list(objects.line_index.values())
            styles_to_apply = {"colour": self.colour.get_value(), "linewidth": self.linewidth.get_value()}
            objects.update_styles(objects_to_update, styles_to_apply)

    def apply_selected(self):
        if self.linewidth.validate():
            objects_to_update = ( schematic.get_selected_objects(object_type=objects.object_type.point) +
                                  schematic.get_selected_objects(object_type=objects.object_type.line) )
            styles_to_apply = {"colour": self.colour.get_value(), "linewidth": self.linewidth.get_value()}
            objects.update_styles(objects_to_update, styles_to_apply)

    def close_window(self):
        global edit_route_line_styles_window
        if not self.colour.is_open():
            edit_route_line_styles_window = None
            self.window.destroy()


#------------------------------------------------------------------------------------
# Class for the Point Style Settings toolbar window.
#------------------------------------------------------------------------------------

edit_point_styles_window = None
            
class edit_point_styles():
    def __init__(self, root_window):
        global edit_point_styles_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_point_styles_window is not None:
            edit_point_styles_window.lift()
            edit_point_styles_window.state('normal')
            edit_point_styles_window.focus_force()
        else:
            # Create the (non resizable) top level window
            self.window = Tk.Toplevel(root_window)
            self.window.title("Point Button Styles")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            edit_point_styles_window = self.window
            # Create the UI Elements
            self.styles = common_style_settings(self.window, object_type="points", max_font_size=12,
                    apply_all_callback=self.apply_all, apply_selected_callback=self.apply_selected,
                    close_window_callback=self.close_window)
            self.styles.pack(padx=5, pady=5, fill='x')
            # Load the initial UI state
            self.styles.load_layout_defaults()

    def apply_all(self):
        if self.styles.validate():
            objects_to_update = list(objects.point_index.values())
            objects.update_styles(objects_to_update, self.styles.get_values())

    def apply_selected(self):
        if self.styles.validate():
            objects_to_update = schematic.get_selected_objects(object_type=objects.object_type.point)
            objects.update_styles(objects_to_update, self.styles.get_values())

    def close_window(self):
        global edit_point_styles_window
        if not self.styles.widgetcolour.is_open():
            edit_point_styles_window = None
            self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the Signal Style Settings toolbar window.
#------------------------------------------------------------------------------------

edit_signal_styles_window = None
            
class edit_signal_styles():
    def __init__(self, root_window):
        global edit_signal_styles_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_signal_styles_window is not None:
            edit_signal_styles_window.lift()
            edit_signal_styles_window.state('normal')
            edit_signal_styles_window.focus_force()
        else:
            # Create the (non resizable) top level window
            self.window = Tk.Toplevel(root_window)
            self.window.title("Signal Button Styles")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            edit_signal_styles_window = self.window
            # Create the UI Elements
            self.styles = common_style_settings(self.window, object_type="signals", max_font_size=12,
                    apply_all_callback=self.apply_all, apply_selected_callback=self.apply_selected,
                    close_window_callback=self.close_window)
            self.styles.pack(padx=5, pady=5, fill='x')
            # Load the initial UI state
            self.styles.load_layout_defaults()

    def apply_all(self):
        if self.styles.validate():
            objects_to_update = list(objects.signal_index.values())
            objects.update_styles(objects_to_update, self.styles.get_values())

    def apply_selected(self):
        if self.styles.validate():
            objects_to_update = schematic.get_selected_objects(object_type=objects.object_type.signal)
            objects.update_styles(objects_to_update, self.styles.get_values())

    def close_window(self):
        global edit_signal_styles_window
        if not self.styles.widgetcolour.is_open():
            edit_signal_styles_window = None
            self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the Textbox Style Settings toolbar window.
#------------------------------------------------------------------------------------

edit_textbox_styles_window = None
            
class edit_textbox_styles():
    def __init__(self, root_window):
        global edit_textbox_styles_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_textbox_styles_window is not None:
            edit_textbox_styles_window.lift()
            edit_textbox_styles_window.state('normal')
            edit_textbox_styles_window.focus_force()
        else:
            # Create the (non resizable) top level window
            self.window = Tk.Toplevel(root_window)
            self.window.title("Text Box Styles")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            edit_textbox_styles_window = self.window
            #----------------------------------------------------------------------------------
            # Create a Frame for the Text colour and background colour (Frame 2)
            #----------------------------------------------------------------------------------
            self.frame2 = Tk.Frame(self.window)
            self.frame2.pack(fill='x')
            self.textcolour = common.colour_selection(self.frame2, label="Text colour")
            self.textcolour.pack(padx=2, pady=2, fill='both', side=Tk.LEFT, expand=1)
            self.background = common.colour_selection(self.frame2, label="Background Colour", transparent_option=True)
            self.background.pack(padx=2, pady=2, fill='x', side=Tk.LEFT, expand=1)
            #----------------------------------------------------------------------------------
            # Create a Frame for the font selection
            #----------------------------------------------------------------------------------
            self.font = common.font_selection(self.window, label="Text font")
            self.font.pack(padx=2, pady=2, fill="x")
            #----------------------------------------------------------------------------------
            # Create a Frame for the font size, text style and border width elements (Frame 3)
            # Pack the elements as a grid to get an aligned layout
            #----------------------------------------------------------------------------------
            self.frame3 = Tk.Frame(self.window)
            self.frame3.pack(fill='x')
            self.frame3.grid_columnconfigure(0, weight=1)
            self.frame3.grid_columnconfigure(1, weight=1)
            # Create a Label Frame for the Font Size Entry components (grid 0,0)
            self.frame3subframe1 = Tk.LabelFrame(self.frame3, text="Font size")
            self.frame3subframe1.grid(row=0, column=0, padx=2, pady=2, sticky='NSWE')
            # Create a subframe to center the label and entrybox
            self.frame3subframe2 = Tk.Frame(self.frame3subframe1)
            self.frame3subframe2.pack()
            self.frame3label1 = Tk.Label(self.frame3subframe2, text="Pixels:")
            self.frame3label1.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
            self.fontsize = common.integer_entry_box(self.frame3subframe2, width=3, min_value=8, max_value=20,
                            allow_empty=False, tool_tip="Select the border width (between 8 and 20 pixels)")
            self.fontsize.pack(padx=2, pady=2, side=Tk.LEFT)
            # Create a Label Frame for the Text Style selection (grid 1,0)
            self.fontstyle = common.font_style_selection(self.frame3, label="Font style")
            self.fontstyle.grid(row=0, column=1, padx=2, pady=2, sticky='NSWE')
            # Create a Label Frame for the Border Width selection (grid 0,1)
            self.frame3subframe3 = Tk.LabelFrame(self.frame3, text="Border width")
            self.frame3subframe3.grid(row=1, column=0, padx=2, pady=2, sticky='NSWE')
            # Create a subframe to center the label and entrybox
            self.frame3subframe4 = Tk.Frame(self.frame3subframe3)
            self.frame3subframe4.pack()
            self.frame3label2 = Tk.Label(self.frame3subframe4, text="Pixels:")
            self.frame3label2.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
            self.borderwidth = common.integer_entry_box(self.frame3subframe4, width=3, min_value=0, max_value=5,
                    allow_empty=False, tool_tip="Select border width between 0 and 5 (0 to disable border)")
            self.borderwidth.pack(padx=2, pady=2, side=Tk.LEFT, fill="x")
            # Create a Label Frame for the Text Justification selection (grid 1,1)
            self.textjustify = common.selection_buttons(self.frame3, label="Text justification",
                    tool_tip="Select text justification", button_labels = ("Left", "Centre", "Right"))
            self.textjustify.grid(row=1, column=1, padx=2, pady=2, sticky='NSWE')
            #----------------------------------------------------------------------------------
            # Create the common buttons and Load the initial UI state
            #----------------------------------------------------------------------------------
            self.buttons = common_buttons(self.window, self.load_app_defaults, self.load_layout_defaults,
                            self.apply_all, self.apply_selected, self.set_layout_defaults, self.close_window)
            self.buttons.pack(padx=5, pady=5, side=Tk.BOTTOM, fill='x', expand=True)
            self.load_layout_defaults()

    def load_app_defaults(self):
        self.textcolour.set_value(settings.get_default_style("textboxes", "textcolour"))
        self.background.set_value(settings.get_default_style("textboxes", "background"))
        self.font.set_value(settings.get_default_style("textboxes", "textfonttuple")[0])
        self.fontsize.set_value(settings.get_default_style("textboxes", "textfonttuple")[1])
        self.fontstyle.set_value(settings.get_default_style("textboxes", "textfonttuple")[2])
        self.borderwidth.set_value(settings.get_default_style("textboxes", "borderwidth"))
        self.textjustify.set_value(settings.get_default_style("textboxes", "justification"))

    def load_layout_defaults(self):
        self.textcolour.set_value(settings.get_style("textboxes", "textcolour"))
        self.background.set_value(settings.get_style("textboxes", "background"))
        self.font.set_value(settings.get_style("textboxes", "textfonttuple")[0])
        self.fontsize.set_value(settings.get_style("textboxes", "textfonttuple")[1])
        self.fontstyle.set_value(settings.get_style("textboxes", "textfonttuple")[2])
        self.borderwidth.set_value(settings.get_style("textboxes", "borderwidth"))
        self.textjustify.set_value(settings.get_style("textboxes", "justification"))

    def set_layout_defaults(self):
        if self.fontsize.validate() and self.borderwidth.validate():
            font_tuple = (self.font.get_value(), self.fontsize.get_value(), self.fontstyle.get_value())
            settings.set_style("textboxes","textfonttuple", font_tuple)
            settings.set_style("textboxes","textcolour", self.textcolour.get_value())
            settings.set_style("textboxes","background", self.background.get_value())
            settings.set_style("textboxes","borderwidth", self.borderwidth.get_value())
            settings.set_style("textboxes","justification", self.textjustify.get_value())

    def apply_all(self):
        if self.fontsize.validate() and self.borderwidth.validate():
            font_tuple = (self.font.get_value(), self.fontsize.get_value(), self.fontstyle.get_value())
            styles_to_apply = {"textfonttuple": font_tuple,
                               "textcolour": self.textcolour.get_value(),
                               "background": self.background.get_value(),
                               "borderwidth": self.borderwidth.get_value(),
                               "justification": self.textjustify.get_value() }
            objects_to_update = list(objects.textbox_index.values())
            objects.update_styles(objects_to_update, styles_to_apply)

    def apply_selected(self):
        if self.fontsize.validate() and self.borderwidth.validate():
            font_tuple = (self.font.get_value(), self.fontsize.get_value(), self.fontstyle.get_value())
            styles_to_apply = {"textfonttuple": font_tuple,
                               "textcolour": self.textcolour.get_value(),
                               "background": self.background.get_value(),
                               "borderwidth": self.borderwidth.get_value(),
                               "justification": self.textjustify.get_value() }
            objects_to_update = schematic.get_selected_objects(object_type=objects.object_type.textbox)
            objects.update_styles(objects_to_update, styles_to_apply)

    def close_window(self):
        global edit_textbox_styles_window
        if not self.textcolour.is_open() and not self.background.is_open():
            edit_textbox_styles_window = None
            self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the Textbox Style Settings toolbar window.
#------------------------------------------------------------------------------------

edit_lever_styles_window = None

class edit_lever_styles():
    def __init__(self, root_window):
        global edit_lever_styles_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_lever_styles_window is not None:
            edit_lever_styles_window.lift()
            edit_lever_styles_window.state('normal')
            edit_lever_styles_window.focus_force()
        else:
            # Create the (non resizable) top level window
            self.window = Tk.Toplevel(root_window)
            self.window.title("Signalbox Lever Styles")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            edit_lever_styles_window = self.window
            #----------------------------------------------------------------------------------
            # Create a Frame for the frame colour and locking text colour type
            #----------------------------------------------------------------------------------
            self.frame1 = Tk.Frame(self.window)
            self.frame1.pack(fill='x')
            self.framecolour = common.colour_selection(self.frame1, label="Frame colour")
            self.framecolour.pack(padx=2, pady=2, fill='both', side=Tk.LEFT, expand=1)
            self.frametextcolour = common.selection_buttons(self.frame1, label="Text colour",
                    tool_tip="Select the text colour (auto to select 'best' contrast with background)",
                    button_labels=("Auto", "Black", "White"))
            self.frametextcolour.pack(side=Tk.LEFT, padx=2, pady=2, fill='both', expand=True)
            #----------------------------------------------------------------------------------
            # Create a Frame for the button colour and button text colour type
            #----------------------------------------------------------------------------------
            self.frame2 = Tk.Frame(self.window)
            self.frame2.pack(fill='x')
            self.buttoncolour = common.colour_selection(self.frame2, label="Button Colour")
            self.buttoncolour.pack(padx=2, pady=2, fill='x', side=Tk.LEFT, expand=1)
            self.buttontextcolour = common.selection_buttons(self.frame2, label="Text colour",
                    tool_tip="Select the text colour (auto to select 'best' contrast with background)",
                    button_labels=("Auto", "Black", "White"))
            self.buttontextcolour.pack(side=Tk.LEFT, padx=2, pady=2, fill='both', expand=True)
            #----------------------------------------------------------------------------------
            # Create a Frame for the font selection
            #----------------------------------------------------------------------------------
            self.font = common.font_selection(self.window, label="Button font")
            self.font.pack(padx=2, pady=2, fill="x")
            #----------------------------------------------------------------------------------
            # Create a Frame for the font size, text style and border width elements (Frame 3)
            # Pack the elements as a grid to get an aligned layout
            #----------------------------------------------------------------------------------
            self.frame3 = Tk.Frame(self.window)
            self.frame3.pack(fill='x')
            self.frame3.grid_columnconfigure(0, weight=1)
            self.frame3.grid_columnconfigure(1, weight=1)
            # Create a Label Frame for the Font Size Entry components (grid 0,0)
            self.frame3subframe1 = Tk.LabelFrame(self.frame3, text="Font size")
            self.frame3subframe1.grid(row=0, column=0, padx=2, pady=2, sticky='NSWE')
            # Create a subframe to center the label and entrybox
            self.frame3subframe2 = Tk.Frame(self.frame3subframe1)
            self.frame3subframe2.pack()
            self.frame3label1 = Tk.Label(self.frame3subframe2, text="Pixels:")
            self.frame3label1.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
            self.fontsize = common.integer_entry_box(self.frame3subframe2, width=3, min_value=8, max_value=20,
                            allow_empty=False, tool_tip="Select the font size (between 8 and 20 pixels)")
            self.fontsize.pack(padx=2, pady=2, side=Tk.LEFT)
            # Create a Label Frame for the Text Style selection (grid 1,0)
            self.fontstyle = common.font_style_selection(self.frame3, label="Font style")
            self.fontstyle.grid(row=0, column=1, padx=2, pady=2, sticky='NSWE')
            #----------------------------------------------------------------------------------
            # Create the common buttons and Load the initial UI state
            #----------------------------------------------------------------------------------
            self.buttons = common_buttons(self.window, self.load_app_defaults, self.load_layout_defaults,
                            self.apply_all, self.apply_selected, self.set_layout_defaults, self.close_window)
            self.buttons.pack(padx=5, pady=5, side=Tk.BOTTOM, fill='x', expand=True)
            self.load_layout_defaults()

    def load_app_defaults(self):
        self.framecolour.set_value(settings.get_default_style("levers", "framecolour"))
        self.frametextcolour.set_value(settings.get_default_style("levers", "lockcolourtype"))
        self.buttoncolour.set_value(settings.get_default_style("levers", "buttoncolour"))
        self.buttontextcolour.set_value(settings.get_default_style("levers", "textcolourtype"))
        self.font.set_value(settings.get_default_style("levers", "textfonttuple")[0])
        self.fontsize.set_value(settings.get_default_style("levers", "textfonttuple")[1])
        self.fontstyle.set_value(settings.get_default_style("levers", "textfonttuple")[2])

    def load_layout_defaults(self):
        self.framecolour.set_value(settings.get_style("levers", "framecolour"))
        self.frametextcolour.set_value(settings.get_style("levers", "lockcolourtype"))
        self.buttoncolour.set_value(settings.get_style("levers", "buttoncolour"))
        self.buttontextcolour.set_value(settings.get_style("levers", "textcolourtype"))
        self.font.set_value(settings.get_style("levers", "textfonttuple")[0])
        self.fontsize.set_value(settings.get_style("levers", "textfonttuple")[1])
        self.fontstyle.set_value(settings.get_style("levers", "textfonttuple")[2])

    def set_layout_defaults(self):
        if self.fontsize.validate():
            font_tuple = (self.font.get_value(), self.fontsize.get_value(), self.fontstyle.get_value())
            settings.set_style("levers","textfonttuple", font_tuple)
            settings.set_style("levers","framecolour", self.framecolour.get_value())
            settings.set_style("levers","lockcolourtype", self.frametextcolour.get_value())
            settings.set_style("levers","buttoncolour", self.buttoncolour.get_value())
            settings.set_style("levers","textcolourtype", self.buttontextcolour.get_value())

    def apply_all(self):
        if self.fontsize.validate():
            font_tuple = (self.font.get_value(), self.fontsize.get_value(), self.fontstyle.get_value())
            styles_to_apply = {"textfonttuple": font_tuple,
                               "framecolour": self.framecolour.get_value(),
                               "lockcolourtype": self.frametextcolour.get_value(),
                               "buttoncolour": self.buttoncolour.get_value(),
                               "textcolourtype": self.buttontextcolour.get_value() }
            objects_to_update = list(objects.lever_index.values())
            objects.update_styles(objects_to_update, styles_to_apply)

    def apply_selected(self):
        if self.fontsize.validate():
            font_tuple = (self.font.get_value(), self.fontsize.get_value(), self.fontstyle.get_value())
            styles_to_apply = {"textfonttuple": font_tuple,
                               "framecolour": self.framecolour.get_value(),
                               "lockcolourtype": self.frametextcolour.get_value(),
                               "buttoncolour": self.buttoncolour.get_value(),
                               "textcolourtype": self.buttontextcolour.get_value() }
            objects_to_update = schematic.get_selected_objects(object_type=objects.object_type.lever)
            objects.update_styles(objects_to_update, styles_to_apply)

    def close_window(self):
        global edit_lever_styles_window
        if not self.framecolour.is_open() and not self.buttoncolour.is_open():
            edit_lever_styles_window = None
            self.window.destroy()

#############################################################################################
