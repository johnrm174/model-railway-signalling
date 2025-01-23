#------------------------------------------------------------------------------------
# These are common classes used across multiple UI Elements
#
# Provides the following 'extensible' UI elements for the application
#    signal_route_frame(Tk.LabelFrame) - read only list of signal_route_selections
#    row_of_widgets(Tk.Frame) - Pass in the base class to create a fixed length row of the base class
#    row_of_validated_dcc_commands(row_of_widgets) - Similar to above but 'get_values' removes blanks 
#    row_of_point_settings(row_of_widgets) - Similar to above but 'get_values' removes duplicates and blanks
#    grid_of_widgets(Tk.Frame) - an expandable grid of widgets (pass in the base class)
#    grid_of_generic_entry_boxes(grid_of_widgets) - As above but 'get_values' removes duplicates and blanks 
#    grid_of_point_settings(grid_of_widgets) - As above but 'get_values' removes duplicates and blanks
#    list_of_widgets(Tk.Frame) - Cretae a list of (read only) widgets - max rows can be specified
#------------------------------------------------------------------------------------

import tkinter as Tk

from . import common_simple
from . import common_compound

#------------------------------------------------------------------------------------
# Compound UI Element for a "read only" signal_route_frame (LabelFrame) - creates a 
# variable number of instances of the signal_route_selection_element when "set_values" 
# is called (according to the length of the supplied list).
#
# Each element in the list comprises [signal_id, list_of_route_selections]
# The list_of_route_selections comprises [main, lh1, lh2, rh1, rh2]
# Each element is a boolean (True/selected or False/deselected)
#
# Public class instance methods provided by this class are:
#    "set_values" - Populates the list of  signals and their routes
#------------------------------------------------------------------------------------

class signal_route_frame(Tk.LabelFrame):
    def __init__(self, parent_frame, label:str, tool_tip:str, border_width=2):
        super().__init__(parent_frame, text=label, borderwidth=border_width)
        # These are the lists that hold the references to the subframes and subclasses
        self.tooltip = tool_tip
        self.sigelements = []
        self.subframe = None

    def set_values(self, sig_interlocking_frame:[[int,[bool,bool,bool,bool,bool]],]):
        # If the lists are not empty (case of "reloading" the config) then destroy
        # all the UI elements and create them again (asthe list may have changed)
        if self.subframe: self.subframe.destroy()
        self.subframe = Tk.Frame(self)
        self.subframe.pack()
        self.sigelements = []
        # sig_interlocking_frame is a variable length list where each element is [sig_id, interlocked_routes]
        if sig_interlocking_frame:
            for sig_interlocking_routes in sig_interlocking_frame:
                # sig_interlocking_routes comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
                # Where each route element is a boolean value (True or False)            
                self.sigelements.append(common_compound.signal_route_selections(self.subframe,
                                                    read_only=True, tool_tip=self.tooltip))
                self.sigelements[-1].pack()
                self.sigelements[-1].set_value(sig_interlocking_routes)
        else:
            self.label = Tk.Label(self.subframe, text="Nothing configured")
            self.label.pack()

#------------------------------------------------------------------------------------
# Base Class for a (fixed length) row_of_widgets of the specified base class.
# All of the kwargs are passed through to the specified base class on creation.
# If the list provided to 'set_values' contains less values than the number of widgets in the
# row then the remaining widgets will be reset to their default state. If the list contains
# more values than the number of widgets then values beyond the number of widgets are ignored
#
# This class supports creating rows of widgets that need the current item_id for validation
#
# Main class methods used by the editor are:
#    "set_values" - will set the intial values from the provided list
#    "get_values" - will return the last "valid" values in a list
#    "enable" - will enable all the widgets in the row
#    "disable" - will disable all the widgets in the row
#    "validate" - Will validate all entries
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class row_of_widgets(Tk.Frame):
    def __init__(self, parent_frame, base_class, columns:int, **kwargs):
        super().__init__(parent_frame)
        # Maintain a list of Widgets (to keep everything in scope)
        self.list_of_widgets = []
        # Create the widgets for the row
        for entry in range (columns):
            self.list_of_widgets.append(base_class(self, **kwargs))
            self.list_of_widgets[-1].pack(side=Tk.LEFT)

    def set_values(self, list_of_values_to_set:list, item_id:int=0):
        for index, widget_to_set in enumerate(self.list_of_widgets):
            # Only set the value if we haven't reached the end of the list of values_to_set
            # Otherwise we 'reset' the widget to its default state (to blank the widget)
            # If an Item ID is specified (for validation) then we pass through to the widgets
            if index < len(list_of_values_to_set):
                params_to_pass = list_of_values_to_set[index]
                widget_to_set.set_value(params_to_pass)
                if item_id > 0: widget_to_set.set_item_id(item_id)
            else:
                widget_to_set.reset()
                if item_id > 0: widget_to_set.set_item_id(item_id)
        
    def get_values(self):
        # Validate all the entries to accept the current (as entered) values
        self.validate()
        # Compile a list of values to return (we don't remove any blanks here)
        entered_values = []
        for widget in self.list_of_widgets:
            entered_values.append(widget.get_value())
        return(entered_values)
    
    def validate(self):
        valid = True
        for widget in self.list_of_widgets:
            if not widget.validate(): valid = False
        return(valid)

    def enable(self):
        for widget in self.list_of_widgets:
            widget.enable()

    def disable(self):
        for widget in self.list_of_widgets:
            widget.disable()

#------------------------------------------------------------------------------------
# Class for a (fixed length) row_of_validated_dcc_commands - builds on the row_of_widgets
# The get_values function is overridden to remove blank entries from the list (dcc_address=0).
#
# Main class methods used by the editor are:
#    "set_values" - will set the intial values from the provided list
#    "get_values" - will return the last "valid" values in a list
#    "enable" - will enable all the widgets in the row
#    "disable" - will disable all the widgets in the row
#    "validate" - Will validate all entries
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class row_of_validated_dcc_commands(row_of_widgets):
    def __init__(self, parent_frame, columns:int, **kwargs):
        # The overridden set_values function will need to know the number of columns as each
        # validated_dcc_command_entry will need the current item id for validation purposes
        self.number_of_columns = columns
        super().__init__(parent_frame, common_compound.validated_dcc_command_entry, columns, **kwargs)
        
    def get_values(self):
        # Get a list of currently entered values
        entered_values = super().get_values()
        # Compile a list of values to return removing any blanks (dcc_address=0))
        # Note that we don't remove any duplicates for DCC Command sequences
        values_to_return = []
        for entered_value in entered_values:
            if entered_value[0] > 0:
                values_to_return.append(entered_value)
        return(values_to_return)

#------------------------------------------------------------------------------------
# Class for a (fixed length) row_of_point_settings - builds on the row_of_widgets class
# The get_values function is overridden to remove blanks (id=0) and duplicates
#
# Main class methods used by the editor are:
#    "set_values" - will set the intial values from the provided list
#    "get_values" - will return the last "valid" values in a list
#    "enable" - will enable all the widgets in the row
#    "disable" - will disable all the widgets in the row
#    "validate" - Will validate all entries
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class row_of_point_settings(row_of_widgets):
    def __init__(self, parent_frame, columns:int, **kwargs):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame, common_compound.point_settings_entry, columns, **kwargs)

    def get_values(self):
        # Get a list of currently entered values
        entered_values = super().get_values()
        # Compile a list of values to return removing any blanks (Point_id=0) or duplicates
        values_to_return = []
        for entered_value in entered_values:
            if entered_value[0] > 0 and entered_value not in values_to_return:
                values_to_return.append(entered_value)
        return(values_to_return)

#------------------------------------------------------------------------------------
# Base Class for a dynamic grid_of_widgets of the specified base class. Will create as many
# fixed-length rows of widgets as are needed to accommodate the list of values provided to
# the 'set_values' function, with buttons at the end of each row to insert or delete rows.
# If there are not enough values provided to populate an entire row, then the remainder of
# widgets in the row are created in their default state (usually enablled but blankk)
# All of the kwargs are passed through to the specified base class on creation
#
# This class supports creating rows of widgets that need the current item_id for validation
#
# Class instance functions to use externally are:
#    "set_values" - will set the intial values from the provided list
#    "get_values" - will return the last "valid" values in a list
#    "enable" - will enable all the widgets in the row
#    "disable" - will disable all the widgets in the row
#    "validate" - Will validate all entries
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class grid_of_widgets(Tk.Frame):
    def __init__(self, parent_frame, base_class, columns:int, **kwargs):
        self.parent_frame = parent_frame
        self.base_class = base_class
        self.columns = columns
        self.kwargs = kwargs
        super().__init__(parent_frame)
        # Maintain a list of subframes, widgets and buttons (to keep everything in scope)
        self.list_of_subframes = []
        self.list_of_widgets = []
        self.list_of_buttons = []

    def create_row(self, item_id:int, pack_after=None):
        # Create a new Frame for the row and pack it
        self.list_of_subframes.append(Tk.Frame(self))
        self.list_of_subframes[-1].pack(after=pack_after, fill='x')
        # Create the entry_boxes for the row
        for value in range (self.columns):
            self.list_of_widgets.append(self.base_class(self.list_of_subframes[-1], **self.kwargs))
            self.list_of_widgets[-1].pack(side=Tk.LEFT)
            # Only set the value if we haven't reached the end of the values_to_set list
            if len(self.list_of_widgets) <= len(self.values_to_set):
                params_to_pass = self.values_to_set[len(self.list_of_widgets)-1]
                self.list_of_widgets[-1].set_value(params_to_pass)
            # Set the Item ID (if one is specified)
            if item_id > 0: self.list_of_widgets[-1].set_item_id(item_id)
        # Create the button for inserting rows
        this_subframe = self.list_of_subframes[-1]
        self.list_of_buttons.append(Tk.Button(this_subframe, text="+", height= 1, width=1, padx=2, pady=0,
                font=('Courier',8,"normal"), command=lambda:self.create_row(item_id, pack_after=this_subframe)))
        self.list_of_buttons[-1].pack(side=Tk.LEFT, padx=5)
        common_simple.CreateToolTip(self.list_of_buttons[-1], "Insert new row (below)")
        # Create the button for deleting rows (apart from the first row)
        if len(self.list_of_subframes) > 1:
            self.list_of_buttons.append(Tk.Button(this_subframe, text="-", height= 1, width=1, padx=2, pady=0,
                                font=('Courier',8,"normal"), command=lambda:self.delete_row(this_subframe)))
            self.list_of_buttons[-1].pack(side=Tk.LEFT)
            common_simple.CreateToolTip(self.list_of_buttons[-1], "Delete row")

    def delete_row(self, this_subframe):
        this_subframe.destroy()

    def set_values(self, values_to_set:list, item_id:int=0):
        # Destroy and re-create the all the subframes - this should also destroy all child widgets
        for subframe in self.list_of_subframes:
            if subframe.winfo_exists():
                subframe.destroy()
        # Start afresh and create what we need to hold the provided values
        self.list_of_subframes = []
        self.list_of_widgets = []                
        self.list_of_buttons = []                
        # Ensure at least one row is created - even if the list of values_to_set is empty
        self.values_to_set = values_to_set
        while len(self.list_of_widgets) < len(values_to_set) or self.list_of_subframes == []:
            self.create_row(item_id)

    def get_values(self):
        # Validate all the entries to accept the current (as entered) values
        self.validate()
        # Compile a list of values to return (we don't remove any blanks here)
        entered_values = []
        for widget in self.list_of_widgets:
            if widget.winfo_exists():
                entered_values.append(widget.get_value())
        return(entered_values)
    
    def validate(self):
        valid = True
        for widget in self.list_of_widgets:
            if widget.winfo_exists():
                if not widget.validate(): valid = False
        return(valid)

    def enable(self):
        for widget in self.list_of_widgets:
            if widget.winfo_exists():
                widget.enable()

    def disable(self):
        for widget in self.list_of_widgets:
            if widget.winfo_exists():
                widget.disable()

#------------------------------------------------------------------------------------
# Class for a grid_of_generic_entry boxes - builds on the grid_of_widgets class
# The get_values function is overridden to remove blanks and/or duplicates
#
# Main class methods used by the editor are:
#    "set_values" - will set the intial values from the provided list
#    "get_values" - will return the last "valid" values in a list
#    "enable" - will enable all the widgets in the row
#    "disable" - will disable all the widgets in the row
#    "validate" - Will validate all entries
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class grid_of_generic_entry_boxes(grid_of_widgets):
    def __init__(self, parent_frame, base_class, columns:int, **kwargs):
        super().__init__(parent_frame, base_class, columns, **kwargs)

    def get_values(self):
        # Get a list of currently entered values
        entered_values = super().get_values()
        # Compile a list of values to return removing any blanks and/or duplicates
        values_to_return = []
        for entered_value in entered_values:
            if ( ( (type(entered_value)==str and entered_value != "") or
                   (type(entered_value)==int and entered_value != 0) )
                      and entered_value not in values_to_return ):
                values_to_return.append(entered_value)
        return(values_to_return)
    
#------------------------------------------------------------------------------------
# Class for a variable grid_of_point_settings - builds on the grid_of_widgets class
# The get_values function is overridden to remove blanks (id=0) and duplicates
#
# Main class methods used by the editor are:
#    "set_values" - will set the intial values from the provided list
#    "get_values" - will return the last "valid" values in a list
#    "enable" - will enable all the widgets in the row
#    "disable" - will disable all the widgets in the row
#    "validate" - Will validate all entries
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class grid_of_point_settings(grid_of_widgets):
    def __init__(self, parent_frame, columns:int, **kwargs):
        super().__init__(parent_frame, common_compound.point_settings_entry, columns, **kwargs)

    def get_values(self):
        # Get a list of currently entered values
        entered_values = super().get_values()
        # Compile a list of values to return removing any blanks (Point_id=0) or duplicates
        values_to_return = []
        for entered_value in entered_values:
            if entered_value[0] > 0 and entered_value not in values_to_return:
                values_to_return.append(entered_value)
        return(values_to_return)

#------------------------------------------------------------------------------------
# Base Class for a  list_of_widgets of the specified base class. Will create as many
# rows/columns of widgets as are needed to accommodate the list of values provided to the
# the 'set_values' function. If there are not enough values provided to populate an entire
# column, then the remainder of widgets in the row are created in their default state
# All of the kwargs are passed through to the specified base class on creation
#
# Class instance functions to use externally are:
#    "set_values" - will set the intial values from the provided list
#    "get_values" - will return the last "valid" values in a list
#    "validate" - Will validate all entries
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class list_of_widgets(Tk.Frame):
    def __init__(self, parent_frame, base_class, rows:int, **kwargs):
        self.parent_frame = parent_frame
        self.base_class = base_class
        self.maximum_rows_to_create = rows
        self.kwargs = kwargs
        super().__init__(parent_frame)
        # Maintain a list of subframes and widgets (to keep everything in scope)
        self.list_of_subframes = []
        self.list_of_widgets = []

    def set_values(self, values_to_set:list, item_id:int=0):
        # Destroy and re-create the all the subframes - this should also destroy all child widgets
        for subframe in self.list_of_subframes:
            if subframe.winfo_exists():
                subframe.destroy()
        # Start afresh and create what we need to hold the provided values
        self.list_of_subframes = []
        self.list_of_widgets = []
        # Create the frame for the first column and pack it
        self.list_of_subframes.append(Tk.Frame(self))
        self.list_of_subframes[-1].pack(side=Tk.LEFT)
        current_row = 0
        # Create the list of widgets
        if len(values_to_set) > 0:
            for value_to_set in values_to_set:
                # Create the widget and set the value
                self.list_of_widgets.append(self.base_class(self.list_of_subframes[-1], **self.kwargs))
                self.list_of_widgets[-1].pack(side=Tk.TOP, anchor="w")
                self.list_of_widgets[-1].set_value(value_to_set)
                current_row = current_row +1
                # Crete a new column if we need to
                if current_row == self.maximum_rows_to_create:
                    self.list_of_subframes.append(Tk.Frame(self))
                    self.list_of_subframes[-1].pack(side=Tk.LEFT, fill="y")
                    current_row = 0
        else:
            self.empty_label = Tk.Label(self.list_of_subframes[-1], text="No entries to display")
            self.empty_label.pack(padx=5, pady=5)

    def get_values(self):
        # Validate all the entries to accept the current (as entered) values
        self.validate()
        # Compile a list of values to return (we don't remove any blanks here)
        entered_values = []
        for widget in self.list_of_widgets:
            if widget.winfo_exists():
                entered_values.append(widget.get_value())
        return(entered_values)

    def validate(self):
        valid = True
        for widget in self.list_of_widgets:
            if widget.winfo_exists():
                if not widget.validate(): valid = False
        return(valid)

###########################################################################################
