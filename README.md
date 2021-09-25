# model-railway-signalling
A model railway signalling library written in Python for the Raspberry Pi with a DCC control of Signals and Points and train 
detection via the GPIO ports on the Pi. For details of the "Public" API - scroll down the page

A simple interface to the Pi-SPROG-3 DCC Command station enables DCC control of the signals and points out on the layout. 
The GPIO interface allows external train detectors such as the BlockSignalling BOD2-NS to be connected in via opto-isolators.

All of the functions for creating and managing 'signals', 'points', 'sections' and 'sensors' have been developed as a Python Package 
to promote re-use across other layouts. This includes functions to support the interlocking of signals and points to enable 
fully prototypical signalling schemes to be developed. The signals and points opjects can be easily mapped to one or more DCC 
addresses in a manner that should be compatible with the majority of DCC signal/points decoders currently on the market. 
Track sensors can also be easily integrated (via the Raspberry Pi's GPIO interface) to enable full automatic control.

Most types of colour light signals, semaphore signals, ground position light signals and ground disc signals are supported.

Note that I have tried to make the package platform independent so you can use it to develop your own layout signalling schemes 
without a Raspberry Pi or the associated Pi-SPROG-3 DCC Command station (track sensors can be manually 'triggered' via the
layout schematic to ensure your code is doing what its supposed to do). Full logging is provided to help you develop/debug 
your own schemes - just set the log level to INFO to see what the package is doing 'under the hood'. And when you do enable
the DCC control aspects, a log level of DEBUG will show you the commands being sent out to the Pi-SPROG-3

Comments and suggestions welcome - but please be kind - the last time I coded anything it was in Ada96 ;)

![Example Screenshot](https://github.com/johnrm174/model-railway-signalling/blob/main/README_screenshot1.png)

## Installation
For a first time installation use:
<pre>
$ python3 -m pip install model-railway-signals 
</pre>
To upgrade to the latest version use:
<pre>
$ python3 -m pip install --upgrade model-railway-signals 
</pre>
You may need to ensure you have the latest version of pip installed:
<pre>
$ python3 -m pip install --upgrade pip
</pre>

## Using the package

To use the "public" functions for developing your own layout signalling system:
<code> from model_railway_signals import * </code>

Some examples are included in the repository: https://github.com/johnrm174/model-railway-signalling:

<pre>
'test_simple_example.py' - a simple example of how to use the "signals" and "points" modules to create a
           basic track schematic with interlocked signals/points and semi-automation of signals using 
           external track sensors to provide "signal passed" events as the train progresses across the 
           schematic. Also includes DCC Mapping examples (for both signals and points).

'test_semaphore_example.py' - effectively the same example as above, but using sempahore signals. 
           Includes DCC Mapping examples for the Semaphore signals (different to colour lights).

'test_approach_control.py' - an example of using "approach control" for automation of junction signals. This 
           is where a signal displays a more restrictive aspect (either red or yellow) when a lower-speed 
           divergent route is set, forcing the approaching train to slow down and be prepared to stop. As 
           the train approaches, the signal is "released", allowing the train to proceed past the signal 
           and onto the divergent route. Examples of "Approach on Red" and "Approach on Yellow" are provided. 
           For "Approach on yellow", the signals behind will show the correct flashing yellow aspects.

'test_semaphore_approach_control' - Similar to the above, but this simulates/automates the series of 
           signals within a block section (e.g. outer home, inner home, starter, advanced starter etc). 
           In this scenario, the distant and home signals should never be cleared for an approaching train 
           if a subsequent home signal (in the same 'Block Section') is set to DANGER. In this case each 
           preceding home signal (and the distant) would remain ON to slow down the train on the approach
           to the first home signal. As the signal is approached, the signal would then be cleared to 
           enable the train to continue (at low speed) towards the next home signal.

'test_harman-signalist_sc1.py'- developed primarily for testing using the Harmann Signallist SC1 decoder. 
           Enables the various modes to be selected (includes programming of CVs) and then tested. I used 
           this decoder as it provided the most flexibility for some of my more complex signal types.
           Note that some of the modes will be similar/identical to other manufacturer's DCC signals.

'test_colour_light_signals.py'- developed primarily for testing, but it does provide an example of every 
           signal type and all the control features currently supported.

'test_semaphore_signals.py'- similar to the above developed primarily for testing, but it does provide  
           an example of every signal type and all the control features currently supported.

</pre>

Or alternatively, go to https://github.com/johnrm174/layout-signalling-scheme to see the scheme for my layout

## Point Functions
<pre>
point_type (use when creating points)
  point_type.RH
  point_type.LH

point_callback_type (tells the calling program what has triggered the callback):
  point_callback_type.point_switched (point has been switched)
  point_callback_type.fpl_switched (facing point lock has been switched)

create_point - Creates a point object and returns a list of the tkinter drawing objects (lines) that 
               make up the point (so calling programs can later update them if required (e.g. change 
               the colour of the lines to represent the route that has been set up)
               Returned list comprises: [straight blade, switched blade, straight route ,switched route]
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the point is to be displayed
      point_id:int - The ID for the point - also displayed on the point button
      pointtype:point_type - either point_type.RH or point_type.LH
      x:int, y:int - Position of the point on the canvas (in pixels)
      colour:str - Any tkinter colour can be specified as a string
  Optional Parameters:
      orientation:int- Orientation in degrees (0 or 180) - Default is zero
      point_callback - The function to call when a point button is pressed - default is no callback
                        Note that the callback function returns (item_id, callback type)
      reverse:bool - If the switching logic is to be reversed - Default is False
      fpl:bool - If the point is to have a Facing point lock (FPL) - Default is False (no FPL)
      also_switch:int - the Id of another point to automatically switch with this point - Default none
      auto:bool - If the point is to be fully automatic (e.g switched by another point) - Default False.

lock_point(*point_id) - use for point/signal interlocking (multiple Point_IDs can be specified)

unlock_point(*point_id) - use for point/signal interlocking (multiple Point_IDs can be specified)

toggle_point(point_id) - use for route setting (can use 'point_switched' to find the state first)

toggle_fpl(point_id) - use for route setting (can use 'fpl_active' to find the state first)

point_switched (point_id) - returns the state of the point (True/False) - to support point/signal interlocking

fpl_active (point_id) - returns the state of the FPL (True/False) - to support point/signal interlocking
                      - Will always return True if the point does not have a Facing point Lock - to enable full 
                      - interlocking logic to be written for layouts but then inhibited for simplified control 
</pre>

## Signal Functions
<pre>
Currently supported signal types:

    Colour Light Signals - 3 or 4 aspect or 2 aspect (home, distant or red/ylw)
          - with or without a position light subsidary signal
          - with or without route indication feathers (maximum of 5)
          - with or without a theatre type route indicator
          - With or without a "Signal Passed" Button
          - With or without a "Approach Release" Button
          - Main signal manual or fully automatic
    Semaphore Signals - Home or Distant
          - with or without junction arms (RH1, RH2, LH1, LH2 arms supported)
          - with or without subsidaries (Main, LH1, LH2, RH1, RH2 arms supported) - Home signals only
          - with or without a theatre type route indicator (for Home signals only)
          - With or without a "Approach Release" Button
          - Main signal manual or fully automatic
    Ground Position Light Signals
          - normal ground position light or shunt ahead position light
          - either early or modern (post 1996) types
    Ground Disc Signals
          - normal ground disc (red banner) or shunt ahead ground disc (yellow banner)

Summary of features supported by each signal type:

    Colour Light signals
           - set_route_indication (Route Type and theatre text)
           - update_signal (based on a signal Ahead) - apart from 2 Aspect Home and Red/Yellow
           - toggle_signal / toggle_subsidary
           - lock_subsidary / unlock_subsidary
           - lock_signal / unlock_signal
           - set_signal_override / clear_signal_override
           - set_approach_control (Release on Red or Yellow) / clear_approach_control
           - trigger_timed_signal
           - query signal state (signal_clear, subsidary_clear, signal_overridden, approach_control_set)
    Semaphore signals:
           - set_route_indication (Route Type and theatre text)
           - update_signal (based on a signal Ahead) - for home signals with a secondary distant arm
           - toggle_signal / toggle_subsidary
           - lock_subsidary / unlock_subsidary
           - lock_signal / unlock_signal
           - set_signal_override / clear_signal_override
           - set_approach_control (Release on Red only) / clear_approach_control
           - trigger_timed_signal
           - query signal state (signal_clear, subsidary_clear, signal_overridden, approach_control_set)
    Ground Position Colour Light signals:
           - lock_signal / unlock_signal
           - set_signal_override / clear_signal_override
           - query signal state (signal_clear, signal_overridden)
    Ground Disc signals
           - lock_signal / unlock_signal
           - set_signal_override / clear_signal_override
           - query signal state (signal_clear, signal_overridden)

Public types and functions:

signal_sub_type (use when creating colour light signals):
  signal_sub_type.home         (2 aspect - Red/Green)
  signal_sub_type.distant      (2 aspect - Yellow/Green
  signal_sub_type.red_ylw      (2 aspect - Red/Yellow
  signal_sub_type.three_aspect (3 aspect - Red/Yellow/Green)
  signal_sub_type.four_aspect  (4 aspect - Red/Yellow/Double-Yellow/Green)

route_type (use for specifying the route):
  route_type.NONE   (no route indication - i.e. not used)
  route_type.MAIN   (main route)
  route_type.LH1    (immediate left)
  route_type.LH2    (far left)
  route_type.RH1    (immediate right)
  route_type.RH2    (rar right)
These equate to the colour light signal route feathers or the Sempahore junction "arms"

sig_callback_type (tells the calling program what has triggered the callback):
    sig_callback_type.sig_switched (signal has been switched)
    sig_callback_type.sub_switched (subsidary signal has been switched)
    sig_callback_type.sig_passed ("signal passed" button / sensor event - or triggered by Timed signal)
    sig_callback_type.sig_updated (signal aspect has been updated as part of a timed sequence)
    sig_callback_type.sig_released (signal "approach release" button / sensor event)

create_colour_light_signal - Creates a colour light signal
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the point is to be displayed
      sig_id:int - The ID for the signal - also displayed on the signal button
      x:int, y:int - Position of the signal on the canvas (in pixels) 
  Optional Parameters:
      signal_subtype:sig_sub_type - type of signal to create - Default is signal_sub_type.four_aspect
      orientation:int- Orientation in degrees (0 or 180) - Default is zero
      sig_callback:name - Function to call when a signal event happens - Default is no callback
                        Note that the callback function returns (item_id, callback type)
      sig_passed_button:bool - Creates a "signal Passed" button for automatic control - Default False
      approach_release_button:bool - Creates an "Approach Release" button - Default False
      position_light:bool - Creates a subsidary position light signal - Default False
      lhfeather45:bool - Creates a LH route indication feather at 45 degrees - Default False
      lhfeather90:bool - Creates a LH route indication feather at 90 degrees - Default False
      rhfeather45:bool - Creates a RH route indication feather at 45 degrees - Default False
      rhfeather90:bool - Creates a RH route indication feather at 90 degrees - Default False
      mainfeather:bool - Creates a MAIN route indication feather - Default False
      theatre_route_indicator:bool -  Creates a Theatre Type route indicator - Default False
      refresh_immediately:bool - When set to False the signal aspects will NOT be automaticall updated 
                when the signal is changed and the external programme will need to call the seperate 
                'update_signal' function. Primarily intended for use with 3/4 aspect signals, where the
                displayed aspect will depend on the signal ahead if the signal is clear - Default True 
      fully_automatic:bool - Creates a signal without a manual control button - Default False

create_semaphore_signal - Creates a Semaphore signal
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the point is to be displayed
      sig_id:int - The ID for the signal - also displayed on the signal button
      x:int, y:int - Position of the point on the canvas (in pixels) 
  Optional Parameters:
      distant:bool - True to create a Distant signal - False to create Home signal - default False
      associated_home:bool - Option only valid when creating distant signals - Set to True to associate
                             the distant signal with a previously created home signal - default False
                             (this option enables a distant signal to "share" the same post as the
                              home signal - specify the same x and y coordinates as the home signal) 
      orientation:int - Orientation in degrees (0 or 180) - Default is zero
      sig_callback:name - Function to call when a signal event happens - Default is no callback
                          Note that the callback function returns (item_id, callback type)
      sig_passed_button:bool - Creates a "signal Passed" button for automatic control - Default False
      approach_release_button:bool - Creates an "Approach Release" button - Default False
      main_signal:bool - To create a signal arm for the main route - default True
                      (Only set this to False for the case of creating a distant signal "associated 
                       with" a home signal where a distant arm for the main route is not required)
      lh1_signal:bool - To create a LH1 post with a main (junction) arm - default False
      lh2_signal:bool - To create a LH2 post with a main (junction) arm - default False
      rh1_signal:bool - To create a RH1 post with a main (junction) arm - default False
      rh2_signal:bool - To create a RH2 post with a main (junction) arm - default False
      main_subsidary:bool - To create a subsidary signal under the "main" signal - default False
      lh1_subsidary:bool - To create a LH1 post with a subsidary arm - default False
      lh2_subsidary:bool - To create a LH2 post with a subsidary arm - default False
      rh1_subsidary:bool - To create a RH1 post with a subsidary arm - default False
      rh2_subsidary:bool - To create a RH2 post with a subsidary arm - default False
      theatre_route_indicator:bool -  Creates a Theatre Type route indicator - Default False
      refresh_immediately:bool - When set to False the signal aspects will NOT be automaticall updated 
                when the signal is changed and the external programme will need to call the seperate 
                'update_signal' function. Primarily intended for use with home signals that have a
                secondary distant arm, which will reflect the state of the signal ahead (i.e. if the
                signal ahead is at DANGER then the secondary distant arm will be ON) - Default True 
      fully_automatic:bool - Creates a signal without a manual control button - Default False

create_ground_position_signal - create a ground position light signal
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the point is to be displayed
      sig_id:int - The ID for the signal - also displayed on the signal button
      x:int, y:int - Position of the signal on the canvas (in pixels) 
  Optional Parameters:
      orientation:int- Orientation in degrees (0 or 180) - Default is zero
      sig_callback:name - Function to call when a signal event happens - Default is no callback
                        Note that the callback function returns (item_id, callback type)
      sig_passed_button:bool - Creates a "signal Passed" button for automatic control - Default False
      shunt_ahead:bool - Specifies a shunt ahead signal (yellow/white aspect) - default False
      modern_type: bool - Specifies a modern type ground position signal (post 1996) - Default False

create_ground_disc_signal - Creates a ground disc type signal
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the point is to be displayed
      sig_id:int - The ID for the signal - also displayed on the signal button
      x:int, y:int - Position of the signal on the canvas (in pixels) 
 Optional Parameters:
      orientation:int- Orientation in degrees (0 or 180) - Default is zero
      sig_callback:name - Function to call when a signal event happens - Default is no callback
                        Note that the callback function returns (item_id, callback type)
      sig_passed_button:bool - Creates a "signal Passed" button for automatic control - Default False
      shunt_ahead:bool - Specifies a shunt ahead signal (yellow banner) - default False (red banner)

set_route - Set (and change) the route indication (either feathers or theatre text)
  Mandatory Parameters:
      sig_id:int - The ID for the signal
  Optional Parameters:
      route:signals_common.route_type - MAIN, LH1, LH2, RH1 or RH2 - default 'NONE'
      theatre_text:str - The text to display in the theatre route indicator - default "NONE"

update_signal - update the aspect of a signal ( based on the aspect of a signal ahead)
              - intended for 3 and 4 aspect and 2 aspect distant colour light signals
              - also for semaphore home signals created with with secondary distant arms
  Mandatory Parameters:
      sig_id:int - The ID for the signal
  Optional Parameters:
      sig_ahead_id:int - The ID for the signal "ahead" of the one to be updated

toggle_signal(sig_id) - use for route setting (can use 'signal_clear' to find the state first)

toggle_subsidary(sig_id) - use for route setting (can use 'subsidary_clear' to find the state first)

lock_signal(*sig_id) - use for point/signal interlocking (multiple Signal_IDs can be specified)

unlock_signal(*sig_id) - use for point/signal interlocking (multiple Signal_IDs can be specified)

lock_subsidary(*sig_id) - use for point/signal interlocking (multiple Signal_IDs can be specified)

unlock_subsidary(*sig_id) use for point/signal interlocking (multiple Signal_IDs can be specified)

signal_clear(sig_id) - returns the signal state (True='clear') - to support interlocking

subsidary_clear(sig_id) - returns the subsidary state (True='clear') - to support interlocking

signal_overridden (sig_id) - returns the signal override state (True='overridden') - to support interlocking

approach_control_set (sig_id) - returns the approach control state (True='active') - to support interlocking

set_signal_override (sig_id*) - Overrides the signal and sets it to DANGER (multiple Signals can be specified)

clear_signal_override (sig_id*) - Reverts the signal to its controlled state (multiple Signals can be specified)

trigger_timed_signal - Sets the signal to DANGER and then cycles through the aspects back to PROCEED
                      - If a start delay >0 is specified then a 'sig_passed' callback event is generated
                      - when the signal is changed to DANGER - For each subsequent aspect change (all the
                      - way back to PROCEED) a 'sig_updated' callback event will be generated
  Mandatory Parameters:
      sig_id:int - The ID for the signal
  Optional Parameters:
      start_delay:int - Delay (in seconds) before changing to DANGER (default=5)
      time_delay:int - Delay (in seconds) for cycling through the aspects (default=5)

set_approach_control - Puts the signal into "Approach Control" Mode where the signal will display a particular
                       aspect/state (either Red or Yellow) to approaching trains. As the Train approaches the
                       signal, the signal should then be "released" to display the normal aspect. Normally used
                       for diverging routes which have a lower speed restriction to the main line. When a signal
                       is set in "approach control" mode then the signals behind will display the appropriate
                       aspects when updated (based on the signal ahead). for "Release on Red" these would be 
                       the normal aspects. For "Release on Yellow", assuming 4 aspect signals, the signals  
                       behind will display flashing single yellow and flashing double yellow aspects.
  Mandatory Parameters:
      sig_id:int - The ID for the signal
  Optional Parameters:
      release_on_yellow:Bool - True = Yellow Approach aspect, False = Red Approach aspect (default=False)

clear_approach_control - This "releases" the signal to display the normal aspect and should be called when
                           a train is approaching the signal (so the signal clears in front of the driver)
                           Note that signals can also be released when the "release control button" is activated
                           (which is displayed just in front of the signal if specified at signal creation time)
  Mandatory Parameters:
      sig_id:int - The ID for the signal
</pre>

## Track Occupancy Functions
<pre>
section_callback_type (tells the calling program what has triggered the callback):
    section_callback_type.section_switched - The section has been toggled (occupied/clear) by the user

create_section - Creates a Track Occupancy section object
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the section is to be displayed
      section_id:int - The ID to be used for the section 
      x:int, y:int - Position of the section on the canvas (in pixels)
  Optional Parameters:
      section_callback - The function to call if the section is manually toggled - default: null
                        Note that the callback function returns (item_id, callback type)
      label - The label to display on the section when occupied - default: "Train On Line"

section_occupied (section_id)- Returns the current state of the section (True=Occupied, False=Clear)

set_section_occupied (section_id) - Sets the specified section to "occupied"

clear_section_occupied (section_id)- Sets the specified section to "clear"
</pre>

## Track Sensor Functions
<pre>
sensor_callback_type (tells the calling program what has triggered the callback):
    track_sensor_callback_type.sensor_triggered - The section has been toggled by the user

create_sensor - Creates a sensor object
  Mandatory Parameters:
      sensor_id:int - The ID to be used for the sensor 
      gpio_channel:int - The GPIO port number  to use for the sensor (not the physical pin number):
  Optional Parameters:
      sensor_timeout:float - The time period during which further triggers are ignored - default = 3.0 secs
      trigger_period:float - Duration that the sensor needs to remain active before triggering - default = 0.001 secs
      signal_passed:int    - Raise a "signal passed" event for the specified signal ID when triggered - default = None
      signal_approach:int  - Raise an "approach release" event for the specified signal ID when triggered - default = None
      sensor_callback      - The function to call when triggered (if signal events have not been specified) - default = None
                                  Note that the callback function returns (item_id, callback type)


sensor_active (sensor_id) - Returns the current state of the sensor (True/False)
</pre>

## DCC Address Mapping Functions

These functions provide the means to map the signals and points on the layout to the series of DCC 
commands needed to control them.

For the main signal aspects, either "Truth Table" or "Event Driven" mappings can be defined
The "Event Driven" mapping uses a single dcc command (address/state) to change the signal to 
the required aspect - as used by the TrainTech DCC signals. The "Truth Table" mapping provides
maximum flexibility for commanding DCC Signals as each "led" can either be controlled individually 
(i.e. Each LED of the signal is controlled via its own individual address) or via a "Truth Table" 
(where the displayed aspect will depend on the binary "code" written to 2 or more DCC addresses)
This has been successfully tested with the Harman Signallist SC1 DCC Decoder in various modes

"Truth Table" or "Event Driven" mappings can alos be defined for the Route indications supported by
the signal (feathers or theatre). If the signal has a subsidary associated with it, this is always
mapped to a single DCC address.

Not all signals/points that exist on the layout need to have a DCC Mapping configured - If no DCC mapping 
has been defined, then no DCC commands will be sent. This provides flexibility for including signals on the 
schematic which are "off scene" or for progressively "working up" the signalling scheme for a layout.
<pre>
map_dcc_signal - Map a signal to one or more DCC Addresses
   Mandatory Parameters:
      sig_id:int - The ID for the signal to create a DCC mapping for
   Optional Parameters:
      auto_route_inhibit:bool - If the signal inhibits route indications at DANGER (default=False)
      proceed[[add:int,state:bool],] - List of DCC addresses/states (default = no mapping)
      danger [[add:int,state:bool],] - List of DCC addresses/states (default = No mapping)
      caution[[add:int,state:bool],] - List of DCC addresses/states (default = No mapping)
      prelim_caution[[add:int,state:bool],] - List of DCC addresses/states (default = No mapping)
      LH1[[add:int,state:bool],] - List of DCC addresses/states for "LH45" (default = No Mapping)
      LH2[[add:int,state:bool],] - List of DCC addresses/states for "LH90" (default = No Mapping)
      RH1[[add:int,state:bool],] - List of DCC addresses/states for "RH45" (default = No Mapping)
      RH2[[add:int,state:bool],] - List of DCC addresses/states for "RH90" (default = No Mapping)
      MAIN[[add:int,state:bool],] - List of DCC addresses/states for "MAIN" (default = No Mapping)
      NONE[[add:int,state:bool],] - List of DCC addresses/states to inhibit routes (default = No Mapping)
              Note that you should ALWAYS provide mappings for NONE if you are using feather route indications
              unless the DCC signal automatically inhibits route indications when displaying a DANGER aspect
      THEATRE[["character",[add:int,state:bool],],] - List of possible theatre indicator states (default = No Mapping)
              Each entry comprises the "character" and the associated list of DCC addresses/states
              "#" is a special character - which means inhibit all indications (when signal is at danger)
              Note that you should ALWAYS provide mappings for '#' if you are using a theatre route indicator
              unless the DCC signal itself inhibits route indications when displaying a DANGER aspect
      subsidary:int - Single DCC address for the "position light" indication (default = No Mapping)

    An example DCC mapping for a  Signalist SC1 decoder with a base address of 1 (CV1=5) is included below.
    This assumes the decoder is configured in "8 individual output" Mode (CV38=8). In this example we are using
    outputs A,B,C,D to drive our signal with E & F driving the feather indications. The Signallist SC1 uses 8 
    consecutive addresses in total (which equate to DCC addresses 1 to 8 for this example). The DCC addresses for
    each LED are: RED = 1, Green = 2, YELLOW1 = 3, YELLOW2 = 4, Feather1 = 5, Feather2 = 6.

           map_dcc_signal (sig_id = 2,
                danger = [[1,True],[2,False],[3,False],[4,False]],
                proceed = [[1,False],[2,True],[3,False],[4,False]],
                caution = [[1,False],[2,False],[3,True],[4,False]],
                prelim_caution = [[1,False],[2,False],[3,True],[4,True]],
                LH1 = [[5,True],[6,False]], 
                MAIN = [[6,True],[5,False]], 
                NONE = [[5,False],[6,False]] )

     A second example DCC mapping, but this time with a Feather Route Indication, is shown below. In this case,
     the main signal aspects are configured identically to the first example. The only difference is the THEATRE
     mapping - where a display of "1" is enabled by DCC Address 5 and "2" by DCC Address 6. Note the special "#"
     character mapping - which defines the DCC commands that need to be sent to inhibit the theatre display.

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
      base_address:int - The base address of the signal (the signal will take 4 consecutive addresses)
   Optional Parameters:
      route_address:int - The address for the route indicator (Feather or Theatre) - Default = 0 (no indicator)
      theatre_route:str - The character to be associated with the Theartre display - Default = "NONE" (no Text)
      feather_route:route_type - The route to be associated with the feather - Default = NONE (no route)

map_semaphore_signal - Generate the mappings for a semaphore signal (DCC address mapped to each arm)
   Mandatory Parameters:
      sig_id:int - The ID for the signal to create a DCC mapping for
      main_signal:int     - single DCC address for the main signal arm (default = No Mapping)
   Optional Parameters:
      main_subsidary:int  - single DCC address for the main subsidary arm (default = No Mapping)
      lh1_signal:int      - single DCC address for the LH1 signal arm (default = No Mapping)
      lh1_subsidary:int   - single DCC address for the LH1 subsidary arm (default = No Mapping)
      lh2_signal:int      - single DCC address for the LH2 signal arm (default = No Mapping)
      lh2_subsidary:int   - single DCC address for the LH2 subsidary arm (default = No Mapping)
      rh1_signal:int      - single DCC address for the RH1 signal arm  (default = No Mapping)
      rh1_subsidary:int   - single DCC address for the RH1 subsidary arm (default = No Mapping)
      rh2_signal:int      - single DCC address for the RH2 signal arm  (default = No Mapping)
      rh2_subsidary:int   - single DCC address for the RH2 subsidary arm (default = No Mapping)
      THEATRE[["character",[add:int,state:bool],],] - List of possible theatre indicator states (default = No Mapping)
              Each entry comprises the "character" and the associated list of DCC addresses/states
              "#" is a special character - which means inhibit all indications (when signal is at danger)
              Note that you should ALWAYS provide mappings for '#' if you are using a theatre route indicator
              unless the DCC signal itself inhibits route indications when displaying a DANGER aspect

     Semaphore signal DCC mappings assume that each main/subsidary signal arm is mapped to a seperate DCC address.
     In this example, we are mapping a signal with MAIN and LH signal arms and a subsidary arm for the MAIN route.
     Note that if the semaphore signal had a theatre type route indication, then this would be mapped in exactly
     the same was as for the Colour Light Signal example above)

           map_semaphore_signal (sig_id = 2, 
                        main_signal = 1 , 
                        lh1_signal = 2 , 
                        main_subsidary = 3)

map_dcc_point
   Mandatory Parameters:
      point_id:int - The ID for the point to create a DCC mapping for
      address:int - the single DCC address for the point
   Optional Parameters:
      state_reversed:bool - Set to True to reverse the DCC logic (default = false)
</pre>

## Pi-Sprog Interface Functions

This provides a basic CBUS interface fpor communicating with the Pi-SPROG3 via the Raspberry Pi UART. It does not provide
a fully-functional interface for all DCC command and control functions - just the minimum set needed to support the driving
of signals and points via a selection of common DCC Accessory decoders. Basic CV Programming is also supported - primarily 
as an aid to testing. For full decoder programming the recommendation is to use JRMI DecoderPro.
<pre>
initialise_pi_sprog - Open and configures the serial comms port to the Pi Sprog
   Optional Parameters:
      port_name:str - The Serial port to use for communicating with the Pi-SPROG 3 - Default="/dev/serial0",
      baud_rate:int - The baud rate to use for the serial port - Default = 115200,
      dcc_debug_mode:bool - Set to True to log the CBUS commands being sent to the Pi-SPROG (default = False). 
                          - If set to True, this initialisation function will also Request and report the 
                            command station status (from the Pi-SPROG-3)

service_mode_write_cv - programmes a CV in direct bit mode and waits for response
                      (events are only sent if we think the track power is currently switched on)
                      (if acknowledgement isn't received within 5 seconds then the request times out)
   Mandatory Parameters:
      cv:int - The CV (Configuration Variable) to be programmed
      value:int - The value to programme

request_dcc_power_on - sends a request to switch on the track power and waits for acknowledgement
                     (requests are only sent if the Pi Sprog Comms Port has been successfully opened/configured)
       returns True if we have received acknowledgement that Track Power has been turned on
       returns False if acknowledgement isn't received within 5 seconds (i.e. request timeout)

request_dcc_power_off - sends a request to switch off the track power and waits for acknowledgement
                     (requests are only sent if the Pi Sprog Comms Port has been successfully opened/configured)
       returns True if we have received acknowledgement that Track Power has been turned off
       returns False if acknowledgement isn't received within 5 seconds (i.e. request timeout)
</pre>



