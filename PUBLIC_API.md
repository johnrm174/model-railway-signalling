# model-railway-signalling - Public API

All of the functions for creating and managing 'signals', 'points', 'sections', 'sensors' and 'block instruments',
were originally developed as a Python Package and a 'Public API' was maintained to allow these functions to be 
re-used by others writing their own layout automation code. However, as the schematic editor application now 
allows users to exploit 99% of the library features when creating and operating signalling schemes within the 
editor, I feel it unlikely that anyone would consider re-using the library functions in their own code
(although if this is not the case then please do tell me).

The Public API is therefore DEPRECATED from Release 4.0

## Using the library functions

To use the public API functions for developing your own layout signalling system:
<pre>
from model_railway_signals import * 
</pre>

## Points
<pre>
point_type (use when creating points)
  point_type.RH
  point_type.LH

point_callback_type (tells the calling program what has triggered the callback):
  point_callback_type.point_switched (point has been switched)
  point_callback_type.fpl_switched (facing point lock has been switched)

create_point - Creates a point object and returns a list of the tkinter drawing objects (lines) 
               that make up the point so calling programs can later update them if required 
               (e.g. change the colour of the lines to represent the route that has been set up)
             - Returns: [straight blade, switched blade, straight route ,switched route]
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the point is to be displayed
      point_id:int - The ID for the point - also displayed on the point button
      pointtype:point_type - either point_type.RH or point_type.LH
      x:int, y:int - Position of the point on the canvas (in pixels)

  Optional Parameters:
      colour:str - Any tkinter colour can be specified as a string - Default = "Black"
      orientation:int- Orientation in degrees (0 or 180) - Default = zero
      point_callback - The function to call when the point is changed - default = no callback
                       Note that the callback function returns (item_id, callback type)
      reverse:bool - If the switching logic is to be reversed - Default = False
      fpl:bool - If the point is to have a Facing point lock - Default = False (no FPL)
      also_switch:int - the Id of another point to switch with this point - Default = None
      auto:bool - Point is fully automatic (i.e. no point control buttons) - Default = False.

lock_point(*point_id:int) - use for point/signal interlocking (multiple IDs can be specified)

unlock_point(*point_id:int) - use for point/signal interlocking (multiple IDs can be specified)

toggle_point(point_id:int) - use for route setting (use 'point_switched' to find state first)

toggle_fpl(point_id:int) - use for route setting (use 'fpl_active' to find state first)

point_switched (point_id:int) - returns the point state (True/False) - to support interlocking

fpl_active (point_id:int) - returns the FPL state (True/False) - to support interlocking
                          - Will return True if the point does not have a Facing point Lock 
</pre>

## Signals

<pre>
Currently supported signal types:

    Colour Light Signals - 3 or 4 aspect or 2 aspect (home, distant or red/ylw)
          - with / without a position light subsidary signal
          - with / without route indication feathers (maximum of 5)
          - with / without a theatre type route indicator
          - With / without a "Signal Passed" Button
          - With / without a "Approach Release" Button
          - With / without control buttons (manual / fully automatic)
    Semaphore Signals - Home or Distant
          - with / without junction arms (RH1, RH2, LH1, LH2)
          - with / without subsidary arms (Main, LH1, LH2, RH1, RH2) (Home signals only)
          - with / without a theatre type route indicator (Home signals only)
          - With / without a "Signal Passed" Button
          - With / without a "Approach Release" Button
          - With / without control buttons (manual / fully automatic)
      - Home and Distant signals can be co-located
    Ground Position Light Signals
          - normal ground position light or shunt ahead position light
          - either early or modern (post 1996) types
    Ground Disc Signals
          - normal ground disc (red banner) or shunt ahead ground disc (yellow banner)

Summary of features supported by each signal type:

    Colour Light signals
           - set_route_indication (Route Type and theatre text)
           - update_signal (based on a signal Ahead) - not 2 Aspect Home or Red/Yellow
           - toggle_signal / toggle_subsidary
           - lock_subsidary / unlock_subsidary
           - lock_signal / unlock_signal
           - set_signal_override / clear_signal_override
           - set_signal_override_caution / clear_signal_override_caution (not Home)
           - set_approach_control (Release on Red or Yellow) / clear_approach_control
           - trigger_timed_signal
           - query signal state (signal_clear, signal_state, subsidary_clear)
    Semaphore signals:
           - set_route_indication (Route Type and theatre text)
           - update_signal (based on a signal Ahead) - (distant signals only)
           - toggle_signal / toggle_subsidary
           - lock_subsidary / unlock_subsidary
           - lock_signal / unlock_signal
           - set_signal_override / clear_signal_override
           - set_signal_override_caution / clear_signal_override_caution (not Home)
           - set_approach_control (Release on Red only) / clear_approach_control
           - trigger_timed_signal
           - query signal state (signal_clear, signal_state, subsidary_clear)
    Ground Position Colour Light signals:
           - toggle_signal
           - lock_signal / unlock_signal
           - set_signal_override / clear_signal_override
           - query signal state (signal_clear, signal_state)
    Ground Disc signals
           - toggle_signal
           - lock_signal / unlock_signal
           - set_signal_override / clear_signal_override
           - query signal state (signal_clear, signal_state)

Public types and functions:

signal_sub_type (use when creating colour light signals):
    signal_sub_type.home         (2 aspect - Red/Green)
    signal_sub_type.distant      (2 aspect - Yellow/Green
    signal_sub_type.red_ylw      (2 aspect - Red/Yellow
    signal_sub_type.three_aspect (3 aspect - Red/Yellow/Green)
    signal_sub_type.four_aspect  (4 aspect - Red/Yellow/Double-Yellow/Green)

semaphore_sub_type (use when creating semaphore signals):
    semaphore_sub_type.home
    semaphore_sub_type.distant
                                  
ground_pos_sub_type(enum.Enum):
    ground_pos_sub_type.standard          (post 1996 type)
    ground_pos_sub_type.shunt_ahead       (post 1996 type)
    ground_pos_sub_type.early_standard           
    ground_pos_sub_type.early_shunt_ahead

ground_disc_sub_type(enum.Enum):
    ground_disc_sub_type.standard
    ground_disc_sub_type.shunt_ahead

route_type (use for specifying the route):
    route_type.NONE   (no route indication)
    route_type.MAIN   (main route)
    route_type.LH1    (immediate left)
    route_type.LH2    (far left)
    route_type.RH1    (immediate right)
    route_type.RH2    (rar right)
These equate to the feathers for colour light signals or the Sempahore junction "arms"

signal_state_type(enum.Enum):
    DANGER               (colour light & semaphore signals)
    PROCEED              (colour light & semaphore signals)
    CAUTION              (colour light & semaphore signals)
    PRELIM_CAUTION       (colour light signals only)
    CAUTION_APP_CNTL     (colour light signals only - CAUTION but subject to RELEASE ON YELLOW)
    FLASH_CAUTION        (colour light signals only- when the signal ahead is CAUTION_APP_CNTL)
    FLASH_PRELIM_CAUTION (colour light signals only- when the signal ahead is FLASH_CAUTION)

sig_callback_type (tells the calling program what has triggered the callback):
    sig_callback_type.sig_switched (signal has been switched)
    sig_callback_type.sub_switched (subsidary signal has been switched)
    sig_callback_type.sig_passed ("signal passed" event - or triggered by a Timed signal)
    sig_callback_type.sig_updated (signal aspect updated as part of a timed sequence)
    sig_callback_type.sig_released (signal "approach release" event)

create_colour_light_signal - Creates a colour light signal
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the signal is to be displayed
      sig_id:int - The ID for the signal - also displayed on the signal button
      x:int, y:int - Position of the signal on the canvas (in pixels) 
  Optional Parameters:
      signal_subtype:sig_sub_type - subtype of signal - Default = four_aspect
      orientation:int- Orientation in degrees (0 or 180) - Default = zero
      sig_callback:name - Function to call when a signal event happens - Default = None
                        Note that the callback function returns (item_id, callback type)
      sig_passed_button:bool - Creates a "signal Passed" button - Default = False
      approach_release_button:bool - Creates an "Approach Release" button - Default = False
      position_light:bool - Creates a subsidary position light signal - Default = False
      lhfeather45:bool - Creates a LH route feather at 45 degrees - Default = False
      lhfeather90:bool - Creates a LH route feather at 90 degrees - Default = False
      rhfeather45:bool - Creates a RH route feather at 45 degrees - Default = False
      rhfeather90:bool - Creates a RH route feather at 90 degrees - Default = False
      mainfeather:bool - Creates a MAIN route feather - Default = False
      theatre_route_indicator:bool -  Creates a Theatre route indicator - Default = False
      refresh_immediately:bool - When set to False the signal aspects will NOT be automatically
                updated when the signal is changed and the external programme will need to call 
                the seperate 'update_signal' function. Primarily intended for use with 3/4 
                aspect signals, where the displayed aspect will depend on the displayed aspect 
                of the signal ahead if the signal is clear - Default = True 
      fully_automatic:bool - Creates a signal without a manual controls - Default = False

create_semaphore_signal - Creates a Semaphore signal
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the signal is to be displayed
      sig_id:int - The ID for the signal - also displayed on the signal button
      x:int, y:int - Position of the signal on the canvas (in pixels) 
  Optional Parameters:
      signal_subtype - subtype of signal - default = semaphore_sub_type.home
      associated_home:int - Option only valid when creating distant signals - Provide the ID of
                            a previously created home signal (and use the same x and y coords)
                            to create the distant signal on the same post as the home signal 
                            with appropriate "slotting" between the signal arms - Default = False  
      orientation:int - Orientation in degrees (0 or 180) - Default = zero
      sig_callback:name - Function to call when a signal event happens - Default = None
                          Note that the callback function returns (item_id, callback type)
      sig_passed_button:bool - Creates a "signal Passed" button - Default = False
      approach_release_button:bool - Creates an "Approach Release" button - Default = False
      main_signal:bool - To create a signal arm for the main route - default = True
                         (Only set this to False when creating an "associated" distant signal
                         for a situation where a distant arm for the main route is not required)
      lh1_signal:bool - create a LH1 post with a main (junction) arm - default = False
      lh2_signal:bool - create a LH2 post with a main (junction) arm - default = False
      rh1_signal:bool - create a RH1 post with a main (junction) arm - default = False
      rh2_signal:bool - create a RH2 post with a main (junction) arm - default = False
      main_subsidary:bool - create a subsidary signal under the "main" signal - default = False
      lh1_subsidary:bool - create a LH1 post with a subsidary arm - default = False
      lh2_subsidary:bool - create a LH2 post with a subsidary arm - default = False
      rh1_subsidary:bool - create a RH1 post with a subsidary arm - default = False
      rh2_subsidary:bool - create a RH2 post with a subsidary arm - default = False
      theatre_route_indicator:bool -  Creates a Theatre route indicator - Default = False
      refresh_immediately:bool - When set to False the signal aspects will NOT be automatically
                updated when the signal is changed and the external programme will need to call 
                the seperate 'update_signal' function. Primarily intended for fully automatic
                distant signals to reflect the state of the home signal ahead - Default = True 
      fully_automatic:bool - Creates a signal without a manual control button - Default = False

create_ground_position_signal - create a ground position light signal
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the signal is to be displayed
      sig_id:int - The ID for the signal - also displayed on the signal button
      x:int, y:int - Position of the signal on the canvas (in pixels) 
  Optional Parameters:
      signal_subtype - subtype of the signal - default = ground_pos_sub_type.early_standard
      orientation:int- Orientation in degrees (0 or 180) - default is zero
      sig_callback:name - Function to call when a signal event happens - default = None
                        Note that the callback function returns (item_id, callback type)
      sig_passed_button:bool - Creates a "signal Passed" button - default =False

create_ground_disc_signal - Creates a ground disc type signal
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the signal is to be displayed
      sig_id:int - The ID for the signal - also displayed on the signal button
      x:int, y:int - Position of the signal on the canvas (in pixels) 
 Optional Parameters:
      signal_subtype - subtype of the signal - default = ground_disc_sub_type.standard
      orientation:int- Orientation in degrees (0 or 180) - Default is zero
      sig_callback:name - Function to call when a signal event happens - Default = none
                        Note that the callback function returns (item_id, callback type)
      sig_passed_button:bool - Creates a "signal Passed" button - Default = False

set_route - Set (and change) the route indication (either feathers or theatre text)
  Mandatory Parameters:
      sig_id:int - The ID for the signal
  Optional Parameters:
      route:signals_common.route_type - MAIN, LH1, LH2, RH1 or RH2 - default = 'NONE'
      theatre_text:str - The text to display in the theatre indicator - default = "NONE"

update_signal - update the signal aspect based on the aspect of a signal ahead - Primarily
                intended for 3/4 aspect colour light signals but can also be used to update 
                2-aspect distant signals (semaphore or colour light) on the home signal ahead
  Mandatory Parameters:
      sig_id:int - The ID for the signal
  Optional Parameters:
      sig_ahead_id:int/str - The ID for the signal "ahead" of the one we want to update.
               Either an integer representing the ID of the signal created on our schematic,
               or a string representing the compound identifier of a remote signal on an 
               external MQTT node. Default = "None" (no signal ahead to take into account)

toggle_signal(sig_id:int) - for route setting (use 'signal_clear' to find the state)

toggle_subsidary(sig_id:int) - forroute setting (use 'subsidary_clear' to find the state)

lock_signal(*sig_id:int) - for interlocking (multiple Signal_IDs can be specified)

unlock_signal(*sig_id:int) - for interlocking (multiple Signal_IDs can be specified)

lock_subsidary(*sig_id:int) - for interlocking (multiple Signal_IDs can be specified)

unlock_subsidary(*sig_id:int) - for interlocking (multiple Signal_IDs can be specified)

signal_clear - returns the SWITCHED state of the signal - i.e the state of the 
               signal manual control button (True='OFF', False = 'ON'). If a route
               is specified then the function also tests against the specified route
  Mandatory Parameters:
      sig_id:int - The ID for the signal
  Optional Parameters:
      route:signals_common.route_type - MAIN, LH1, LH2, RH1 or RH2 - default = 'NONE'

subsidary_clear - returns the SWITCHED state of the subsidary  i.e the state of the 
                  signal manual control button (True='OFF', False = 'ON'). If a route
                  is specified then the function also tests against the specified route
  Mandatory Parameters:
      sig_id:int - The ID for the signal
  Optional Parameters:
      route:signals_common.route_type - MAIN, LH1, LH2, RH1 or RH2 - default = 'NONE'

signal_state(sig_id:int/str) - returns the DISPLAYED state of the signal. This can be different 
                      to the SWITCHED state if the signal is OVERRIDDEN or subject to APPROACH
                      CONTROL. Use this function when you need to get the actual state (in terms
                      of aspect) that the signal is displaying - returns 'signal_state_type'.
                      - Note that for this function, the sig_id can be specified either as an 
                      integer (representing the ID of a signal on the local schematic), or a 
                      string (representing the identifier of an signal on an external MQTT node)

set_signal_override (sig_id*:int) - Overrides the signal to display the most restrictive aspect
                      (Distant signals will display CAUTION - all other types will display DANGER)

clear_signal_override (sig_id*:int) - Clears the signal Override (can specify multiple sig_ids)

set_signal_override_caution (sig_id*:int) - Overrides the signal to display CAUTION
                      (Applicable to all main signal types apart from home signals)

clear_signal_override_caution (sig_id*:int) - Clears the signal Override
                      (Applicable to all main signal types apart from home signals)

trigger_timed_signal - Sets the signal to DANGER and cycles through the aspects back to PROCEED.
                      If start delay > 0 then a 'sig_passed' callback event is generated when
                      the signal is changed to DANGER - For each subsequent aspect change 
                      (back to PROCEED) a 'sig_updated' callback event will be generated.
  Mandatory Parameters:
      sig_id:int - The ID for the signal
  Optional Parameters:
      start_delay:int - Delay (in seconds) before changing to DANGER (default = 5)
      time_delay:int - Delay (in seconds) for cycling through the aspects (default = 5)

set_approach_control - Normally used when a diverging route has a lower speed restriction.
            Puts the signal into "Approach Control" Mode where the signal will display a more 
            restrictive aspect/state (either DANGER or CAUTION) to approaching trains. As the
            Train approaches, the signal will then be "released" to display its "normal" aspect.
            When a signal is in "approach control" mode the signals behind will display the 
            appropriate aspects (when updated based on the signal ahead). These would be the
            normal aspects for "Release on Red" but for "Release on Yellow", the colour light 
            signals behind would show flashing yellow / double-yellow aspects as appropriate.
  Mandatory Parameters:
      sig_id:int - The ID for the signal
  Optional Parameters:
      release_on_yellow:Bool - True for Release on Yellow - default = False (Release on Red)
      force_set:Bool - If False then this function will have no effect in the period between
                      the signal being 'released' and the signal being 'passed' (default True)

clear_approach_control (sig_id:int) - This "releases" the signal to display the normal aspect. 
            Signals are also automatically released when the"release button" (displayed just 
            in front of the signal if specified when the signal was created) is activated,
            either manually or via an external sensor event.
</pre>

## Track Occupancy

<pre>
section_callback_type (tells the calling program what has triggered the callback):
     section_callback_type.section_updated - The section has been updated by the user

create_section - Creates a Track Occupancy section object
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the section is to be displayed
      section_id:int - The ID to be used for the section 
      x:int, y:int - Position of the section on the canvas (in pixels)
  Optional Parameters:
      section_callback - The function to call if the section is updated - default = None
                        Note that the callback function returns (item_id, callback type)
      editable:bool - If the section can be manually toggled and/or edited (default = True)
      label:str - The label to display on the section when occupied - default: "OCCUPIED"

section_occupied (section_id:int/str)- Returns the section state (True=Occupied, False=Clear)
               The Section ID can either be specified as an integer representing the ID of a 
               section created on our schematic, or a string representing the compound 
               identifier of a section on an remote MQTT network node.

section_label (section_id:int/str)- Returns the 'label' of the section (as a string)
               The Section ID can either be specified as an integer representing the ID of a 
               section created on our schematic, or a string representing the compound 
               identifier of a section on an remote MQTT network node.

set_section_occupied - Sets the section to "OCCUPIED" (and updates the 'label' if required)
  Mandatory Parameters:
      section_id:int - The ID to be used for the section 
  Optional Parameters:
      label:str - An updated label to display when occupied (Default = No Change)
      publish:bool - Publish updates via MQTT Broker (Default = True)

clear_section_occupied - Sets the section to "CLEAR" (and updates the 'label' if required)
          Returns the current value of the Section Lable (as a string) to allow this
          to be 'passed' to the next section (via the set_section_occupied function)  
  Mandatory Parameters:
      section_id:int - The ID to be used for the section 
  Optional Parameters:
      label:str - An updated label to display when occupied (Default = No Change)
      publish:bool - Publish updates via MQTT Broker (Default = True)
</pre>

## Track Sensors

These functions enable external train detectors (such as the BlockSignalling BOD2-NS) to be 
integrated with the signalling scheme to provide a level of automation.

<pre>
sensor_callback_type (tells the calling program what has triggered the callback):
    track_sensor_callback_type.sensor_triggered - The external sensor has been triggered

create_sensor - Creates a sensor object
  Mandatory Parameters:
      sensor_id:int - The ID to be used for the sensor 
      gpio_channel:int - The GPIO port number for the sensor (not the physical pin number)
  Optional Parameters:
      sensor_timeout:float - Time period for ignoring further triggers - default = 3.0 secs
      trigger_period:float - Active duration for sensor before triggering - default = 0.001 secs
      signal_passed:int    - Raise a "signal passed" event for a signal ID - default = None
      signal_approach:int  - Raise an "approach release" event for a signal ID - default = None
      sensor_callback      - Function to call when a sensor has been triggered (if signal events 
                             have not been specified) - default = None
                             Note that the callback function returns (item_id, callback type)

sensor_active (sensor_id:int) - Returns the current state of the sensor (True/False)

get_list_of_available_ports() - returns a list of supported ports

</pre>

## Block Instruments

These functions (together with the MQTT networking functions) enable the users of different 
signalling applications, running on different computers to communicate prototypically via signalbox 
bell codes and block status.

If you want to use Block Instruments with full sound enabled (bell rings and telegraph key sounds) 
then you will also need to install the 'simpleaudio' package. Note that for Windows it has a dependency 
on Microsoft Visual C++ 14.0 or greater so you will need to install Visual Studio 2015 first. I've 
found that all to be a bit of a faff, so haven't made it a hard dependency - if 'simpleaudio' is 
not installed then the software will still function correctly (just without sound).

<pre>
block_callback_type (tells the calling program what has triggered the callback)
    block_section_ahead_updated - The block section AHEAD of our block section has been updated
                            (i.e. the block section state represented by the Repeater indicator)

instrument_type - enumeration type - single_line or double_line

create_block_instrument - Creates a Block Section Instrument on the schematic
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the instrument is to be displayed
      block_id:int - The local identifier to be used for the Block Instrument 
      x:int, y:int - Position of the instrument on the canvas (in pixels)
  Optional Parameters:
      inst_type:instrument_type - either instrument_type.single_line or instrument_type.double_line
      block_callback - The function to call when the repeater indicator on our instrument has been
                       updated (i.e. the block changed on the linked instrument) - default: null
                       Note that the callback function returns (item_id, callback type)
      bell_sound_file:str - The filename of the soundfile (in the local package resources
                          folder) to use for the bell sound (default "bell-ring-01.wav" - other
                          options are "bell-ring-02.wav", "bell-ring-03.wav", "bell-ring-04.wav")
      telegraph_sound_file:str - The filename of the soundfile (in the local package resources)
                          to use for the Telegraph key sound (default "telegraph-key-01.wav")
      linked_to:int/str - the identifier for the "paired" block instrument - can be specified
                          either as an integer (representing the ID of a Block Instrument on the
                          the local schematic), or a string representing a Block Instrument 
                          running on a remote node - see MQTT networking (default = None)

block_section_ahead_clear(block_id:int) - Returns the state of the ASSOCIATED block instrument
          (i.e. the linked instrument controlling the state of the block section ahead of ours)
          This can be used to implement full interlocking of the Starter signal in our section
          (i.e. signal locked at danger until the box ahead sets their instrument to LINE-CLEAR)
          Returned state is: True = LINE-CLEAR, False = LINE-BLOCKED or TRAIN-ON-LINE
</pre>

## DCC Address Mapping

These functions provide the means to map the signals and points on the layout to the DCC commands 
or DCC command sequences needed to control them.

For colour light signals, either "Truth Table" or "Event Driven" mappings can be defined. 
The "Event Driven" mapping uses a single dcc command (address/state) to change the signal to 
the required aspect - as used by the TrainTech DCC signals. The "Truth Table" mapping provides 
maximum flexibility for commanding DCC Signals as each LED can either be controlled individually 
(i.e. Each LED of the signal is controlled via its own individual address) or via a "Truth Table" 
(where the displayed aspect will depend on the binary "code" written to 2 or more DCC addresses).
This has been successfully tested with the Harman Signallist SC1 DCC Decoder in various modes.
If the signal has a subsidary associated with it, this is mapped to a single DCC address.

"Truth Table" or "Event Driven" mappings can also be defined for the route indications supported 
by the signal (feathers or theatre).

For semaphore signals, a single address is mapped to each signal arm.

Not all signals/points that exist on the layout need to have a DCC Mapping configured - If no DCC mapping 
has been defined, then no DCC commands will be sent. This provides flexibility for including signals on the 
schematic which are "off scene" or for progressively "working up" the signalling scheme for a layout.
<pre>
map_dcc_signal - Map a signal to one or more DCC Addresses
   Mandatory Parameters:
      sig_id:int - The ID for the signal to create a DCC mapping for
   Optional Parameters:
      auto_route_inhibit:bool - If signal inhibits route indication at DANGER (default=False)
      proceed[[add:int,state:bool],] -  DCC addresses/states (default = no mapping)
      danger [[add:int,state:bool],] - DCC addresses/states (default = No mapping)
      caution[[add:int,state:bool],] - DCC addresses/states (default = No mapping)
      prelim_caution[[add:int,state:bool],] - DCC addresses/states (default = No mapping)
      flash_caution[[add:int,state:bool],] - DCC addresses/states (default = No mapping)
      flash_prelim_caution[[add:int,state:bool],] - DCC addresses/states (default = No mapping)
      LH1[[add:int,state:bool],] - DCC addresses/states for "LH45" (default = No Mapping)
      LH2[[add:int,state:bool],] - DCC addresses/states for "LH90" (default = No Mapping)
      RH1[[add:int,state:bool],] - DCC addresses/states for "RH45" (default = No Mapping)
      RH2[[add:int,state:bool],] - DCC addresses/states for "RH90" (default = No Mapping)
      MAIN[[add:int,state:bool],] - DCC addresses/states for "MAIN" (default = No Mapping)
      NONE[[add:int,state:bool],] - DCC addresses/states to inhibit the route indication when 
              the signal is displaying DANGER - unless the DCC signal automatically inhibits
              route indications (see auto_route_inhibit flag above) - Default = None
      THEATRE[["char",[add:int,state:bool],],] - list of theatre states (default = No Mapping)
              Each entry comprises the "char" and the associated list of DCC addresses/states
              that need to be sent to get the theatre indicator to display that character.
              "#" is a special character - which means inhibit all indications (when signal 
              is at danger). You should ALWAYS provide mappings for '#' if you are using a 
              theatre indicator unless the signal automatically inhibits route indications.
      subsidary:int - Single DCC address for the "subsidary" signal (default = No Mapping)

    An example mapping for a  Signalist SC1 decoder with a base address of 1 (CV1=5) is included
    below. This assumes the decoder is configured in "8 individual output" Mode (CV38=8). In this
    example we are using outputs A,B,C,D to drive our signal with E & F each driving a feather 
    indication. The Signallist SC1 uses 8 consecutive addresses in total (which equate to DCC 
    addresses 1 to 8 for this example). The DCC addresses for each LED are: RED = 1, Green = 2, 
    YELLOW1 = 3, YELLOW2 = 4, Feather1 = 5, Feather2 = 6.

           map_dcc_signal (sig_id = 2,
                danger = [[1,True],[2,False],[3,False],[4,False]],
                proceed = [[1,False],[2,True],[3,False],[4,False]],
                caution = [[1,False],[2,False],[3,True],[4,False]],
                prelim_caution = [[1,False],[2,False],[3,True],[4,True]],
                LH1 = [[5,True],[6,False]], 
                MAIN = [[6,True],[5,False]], 
                NONE = [[5,False],[6,False]] )

     A second example DCC mapping, but this time with a Feather Route Indication, is shown below. 
     In this case, the main signal aspects are configured identically to the first example, the
     only difference being the THEATRE mapping - where a display of "1" is enabled by DCC Address
     5 and "2" by DCC Address 6. Note the special "#" character mapping - which defines the DCC 
     commands that need to be sent to inhibit the theatre display.

            map_dcc_signal (sig_id = 2,
                danger = [[1,True],[2,False],[3,False],[4,False]],
                proceed = [[1,False],[2,True],[3,False],[4,False]],
                caution = [[1,False],[2,False],[3,True],[4,False]],
                prelim_caution = [[1,False],[2,False],[3,True],[4,True]],
                THEATRE = [ ["#",[[5,False],[6,False]]],
                            ["1",[[6,False],[5,True]]],
                            ["2",[[5,False],[6,True]]]  ] )

map_traintech_signal - Generate the mappings for a TrainTech signal
   Mandatory Parameters:
      sig_id:int - The ID for the signal to create a DCC mapping for
      base_address:int - Base address of signal (the signal will take 4 consecutive addresses)
   Optional Parameters:
      route_address:int - Address for the route indicator - Default = 0 (no indicator)
      theatre_route:str - Char to be associated with the Theartre - Default = "NONE" (no Text)
      feather_route:route_type - Route to be associated with feather - Default = NONE (no route)

map_semaphore_signal - Generate mappings for a semaphore signal (DCC address mapped to each arm)
   Mandatory Parameters:
      sig_id:int - The ID for the signal to create a DCC mapping for
      main_signal:int     - DCC address for the main signal arm (default = No Mapping)
   Optional Parameters:
      main_subsidary:int  - DCC address for main subsidary arm (default = No Mapping)
      lh1_signal:int      - DCC address for LH1 signal arm (default = No Mapping)
      lh1_subsidary:int   - DCC address for LH1 subsidary arm (default = No Mapping)
      lh2_signal:int      - DCC address for LH2 signal arm (default = No Mapping)
      lh2_subsidary:int   - DCC address for LH2 subsidary arm (default = No Mapping)
      rh1_signal:int      - DCC address for RH1 signal arm  (default = No Mapping)
      rh1_subsidary:int   - DCC address for RH1 subsidary arm (default = No Mapping)
      rh2_signal:int      - DCC address for RH2 signal arm  (default = No Mapping)
      rh2_subsidary:int   - DCC address for RH2 subsidary arm (default = No Mapping)
      THEATRE[["char",[add:int,state:bool],],] - list of theatre states (default = No Mapping)
              Each entry comprises the "char" and the associated list of DCC addresses/states
              that need to be sent to get the theatre indicator to display that character.
              "#" is a special character - which means inhibit all indications (when signal 
              is at danger). You should ALWAYS provide mappings for '#' if you are using a 
              theatre indicator unless the signal automatically inhibits route indications.

     Semaphore signal DCC mappings assume that each main/subsidary signal arm is mapped to a 
     seperate DCC address. In this example, we are mapping a signal with MAIN and LH signal 
     arms and a subsidary arm for the MAIN route. Note that if the semaphore signal had a
     theatre type route indication, then this would be mapped in exactly the same was as for
     the Colour Light Signal example (above).

           map_semaphore_signal (sig_id = 2, 
                                 main_signal = 1 , 
                                 lh1_signal = 2 , 
                                 main_subsidary = 3)

map_dcc_point
   Mandatory Parameters:
      point_id:int - The ID for the point to create a DCC mapping for
      address:int - the single DCC address to use for the point
   Optional Parameters:
      state_reversed:bool - Set to True to reverse the DCC logic (default = false)
</pre>

## Load and Save Layout State

This function enables layout state to loaded on application startup and then to be saved on 
application quit (ready for the next running session).
<pre>
load_layout_state - Loads the initial state for all 'points', 'signals' and 'sections' from file
                    and enables the save of the current layout state to file on application quit.
                    If load is "cancelled" or "file not found" then the default state will be used.
   Optional Parameters:
      file_name:str - to load/save - default = None (will default to 'main-python-script.sig')
      ask_to_load_state:bool - Asks the user if they want to load layout state - default = True
      load_file_dialog:bool - Opens a 'load file' dialog to select a file - default = False
      save_file_dialog:bool - Opens a 'save file' dialog on application quit - default = False
</pre>

## SPROG Interface

This provides a basic CBUS interface for communicating with the SPROG via a serial port. It 
does not provide a fully-functional interface for all DCC command and control functions, just 
the minimum set needed to support the driving of signals and points via a selection of common 
DCC Accessory decoders. Basic CV Programming is also supported - primarily as an aid to testing,  
but for full decoder programming the recommendation is to use JRMI DecoderPro or similar.
<pre>
sprog_connect - Open and configures the serial comms port to the Pi Sprog and issues
                a Request Command Station Status command to confirm connectivity
   Optional Parameters:
      port_name:str - The serial port to use for the Pi-SPROG 3 - Default="/dev/serial0",
      baud_rate:int - The baud rate to use for the serial port - Default = 115200,
      dcc_debug_mode:bool - Set to 'True' to log the CBUS commands being sent to the Pi-SPROG
        returns True - if communications with the Pi-Sprog have been established (otherwise False)

service_mode_read_cv - Queries a CV in direct bit mode and waits for response
                      (events are only sent if the track power is currently switched on)
                      (request times out after 5 secs if the request was unsuccessful)
   Mandatory Parameters:
      cv:int - The CV (Configuration Variable) to be queried
         returns the current value of the CV if a response is received
         returns None - if the request fails or the request times out

service_mode_write_cv - programmes a CV in direct bit mode and waits for response
                      (events are only sent if the track power is currently switched on)
                      (request times out after 5 secs if the request was unsuccessful)
   Mandatory Parameters:
      cv:int - The CV (Configuration Variable) to be programmed
      value:int - The value to programme
         returns True - if we have acknowledgement that the CV has been programmed
         returns False - if the CV programming fails or the request times out

request_dcc_power_on - sends request to switch on the power and waits for acknowledgement
                 (requests only sent if the Comms Port has been successfully opened/configured)
         returns True - if we have  acknowledgement that Track Power has been turned on
         returns False - if the request times out 

request_dcc_power_off - sends request to switch off the power and waits for acknowledgement
                 (requests only sent if the Comms Port has been successfully opened/configured)
         returns True - if we have  acknowledgement that Track Power has been turned off
         returns False - if the request times out
</pre>

## MQTT Networking

These functions provides a basic MQTT Client interface for the Model Railway Signalling Package, 
allowing multiple signalling applications (running on different computers) to share a single 
SPROG DCC interface and to share layout state and events across a MQTT broker network.
 
For example, you could run one signalling application on a computer without a SPROG, configure that 
node to "publish" its DCC command feed to the network and then configure another node (with a SPROG) 
to "subscribe" to the same DCC command feed and then forwarded to the local SPROG interface.

You can also use these features to split larger layouts into multiple signal box areas whilst 
still being able to implement a level of automation between them. Functions are provided for 
publishing and subscribing to signals and track occupancy sections. This enables colour light 
signal aspects to correctly reflect the aspect of the signal ahead and trains to be "passed" 
from one signal box area to the next. MQTT networking also supports the linking of Block Instruments, 
allowing signal boxes to communicate prototypically via signalbox bell codes and block status.

To use these networking functions, you can either set up a local MQTT broker on one of the host 
computers on your local network or alternatively use an 'open source' broker out there on the 
internet - I've been using a test broker at "mqtt.eclipseprojects.io" (note this has no security 
or authentication).

If you do intend using an internet-based broker then it is important to configure it with an 
appropriate level of security. This package does support basic username/password authentication 
for connecting in to the broker but note that these are NOT ENCRYPTED when sending over the 
internet unless you are also using a SSL connection.
<pre>
configure_mqtt_client - Configures the local MQTT client and layout network node
  Mandatory Parameters:
      network_identifier:str - The name to use for this signalling network (any string)
      node_identifier:str - The name to use for this node on the network (can be any string)
  Optional Parameters:
      mqtt_enhanced_debugging:bool - 'True' to enable additional debug logging (default = False)
      publish_shutdown:bool - Publish a shutdown message on appication exit (default = False)
      act_on_shutdown:bool - Make a callback if a shutdown message is received (default = False)
      shutdown_callback - Callback to make on reciept of a shutdown message (default = None)

mqtt_broker_connect - Opens a connection to a local or remote MQTT broker
                   Returns whether the connection was successful or not (True/False)
  Mandatory Parameters:
      broker_host:str - The name/IP address of the MQTT broker host to be used
  Optional Parameters:
      broker_port:int - The network port for the broker host (default = 1883)
      broker_username:str - the username to log into the MQTT Broker (default = None)
      broker_password:str - the password to log into the MQTT Broker (default = None)

set_node_to_publish_dcc_commands - Enables publishing of DCC commands to other network nodes
  Optional Parameters:
      publish_dcc_commands:bool - 'True' to Publish / 'False' to stop publishing (default=False)

subscribe_to_dcc_command_feed - Subcribes to DCC command feed from another node on the network.
          All received DCC commands are automatically forwarded to the local Pi-Sprog interface.
  Mandatory Parameters:
      *nodes:str - The name of the node publishing the feed (multiple nodes can be specified)

subscribe_to_remote_section - Subscribes to a remote track section object
  Mandatory Parameters:
      remote_identifier:str - the remote identifier for the track section in the form 'node-id'
  Optional Parameters:
      section_callback - Function to call when a track section update is received  - default = None

set_sections_to_publish_state - Enable the publication of state updates for track sections.
               All subsequent changes will be automatically published to remote subscribers
  Mandatory Parameters:
      *sec_ids:int - The track sections to publish (multiple Section_IDs can be specified)

subscribe_to_remote_signal - Subscribes to a remote signal object
  Mandatory Parameters:
      remote_identifier:str - the remote identifier for the signal in the form 'node-id'
  Optional Parameters:
      signal_callback - Function to call when a signal update is received - default = None

set_signals_to_publish_state - Enable the publication of state updates for signals.
               All subsequent changes will be automatically published to remote subscribers
  Mandatory Parameters:
      *sig_ids:int - The signals to publish (multiple Signal_IDs can be specified)

subscribe_to_remote_instrument - Subscribes to a remote block instrument object
  Mandatory Parameters:
      remote_identifier:str - the remote identifier for the block instrument in the form 'node-id'

set_instruments_to_publish_state - Enable the publication of state updates for block instruments.
               All subsequent changes will be automatically published to remote subscribers
  Mandatory Parameters:
      *inst_ids:int - The block instruments to publish (multiple Instrument_IDs can be specified)

subscribe_to_remote_sensor - Subscribes to a remote track sensor object
  Mandatory Parameters:
      remote_identifier:str - the remote identifier for the sensor in the form 'node-id'
  Optional Parameters:
      signal_passed:int    - Raise a "signal passed" event for a signal ID - default = None
      signal_approach:int  - Raise an "approach release" event for a signal ID - default = None
      sensor_callback      - Function to call when a sensor has been triggered - default = None
                             Only one of signal_passed, signal_approach or callback can be specified
                             Note that for callback, the function returns (item_id, callback type)

set_sensors_to_publish_state- Enable the publication of state updates for track sensors.
             All subsequent changes will be automatically published to remote subscribers
  Mandatory Parameters:
      *sensor_ids:int - The track sensors to publish (multiple Sensor IDs can be specified)      
</pre>

## Code examples

Some examples are included in the repository: https://github.com/johnrm174/model-railway-signalling 
in the 'code_examples' folder:

<pre>
'test_simple_example.py' - an example of how to use the "signals", "points", "sections" and 
           "sensors" modules to create a basic track schematic with interlocked signals/points 
           and semi-automation of signals using external sensors to provide "signal passed" 
           events as the train progresses across the schematic. Also includes DCC Mapping 
           examples (for both signals and points).

'test_semaphore_example.py' - effectively the same example as above, but using sempahore signals. 
           Includes DCC Mapping examples for the Semaphore signals (different to colour lights).

'test_approach_control.py' - an example of using "approach control" for junction signals. Signals 
           subject to "approach control" display a more restrictive aspect (either red or yellow) 
           when a lower-speed divergent route is set, forcing the approaching train to slow down 
           and be prepared to stop. As the train approaches, the signal is "released", allowing 
           the train to proceed past the signal and onto the divergent route. For Colour light 
           signals, examples of "Approach on Red" and "Approach on Yellow" are provided (for 
           "Approach on yellow", the signals behind will show the correct flashing yellow 
           aspects). For Semaphore signals, an example of using approach control for semi
           automating all the home signals within a block section is provided.

'test_networking_1/2.py' - an example of how to network multiple signalling applications 
           (potentially hosted on seperate computers) together via an external MQTT broker. This 
           demonstrates how signal states, "signal passed" events and track occupancy information 
           can be shared between applications and how block instruments can be configured to
           provide a prototypical method of communication between the applications.

'test_harman-signalist_sc1.py'- developed primarily for testing using the Harmann Signallist SC1 
           decoder. Enables the various modes to be selected (includes programming of CVs) and 
           then tested. I used this decoder as it provided the most flexibility for some of my 
           more complex signal types. Note that some of the modes will be similar/identical to 
           other manufacturer's DCC signals.

'test_colour_light_signals.py'- developed primarily for testing, but it does provide an example 
           of every signal type and the control features currently supported.

'test_semaphore_signals.py'- similar to the above developed primarily for testing, but it does 
           provide an example of every signal type and the control features supported.

</pre>
