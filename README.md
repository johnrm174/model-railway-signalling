# model-railway-signalling
A model railway signalling library written in Python for the Raspberry Pi with a DCC control of Signals and Points and train 
detection via the GPIO ports on the Pi. For details of the "Public" API - scroll down the page

A simple interface to the Pi-SPROG-3 DCC Command station enables DCC control of the signals and points out on the layout. 
The GPIO interface allows external train detectors such as the BlockSignalling BOD2-NS to be connected in via opto-isolators.

All of the functions for creating and managing 'signals', 'points' and 'sections' have been developed as a Python Package 
to promote re-use across other layouts. This includes functions to support the interlocking of signals and points to enable 
fully prototypical signalling schemes to be developed. The signals and points opjects can be easily mapped to one or more DCC 
addresses in a manner that should be compatible with the majority of DCC signal/points decoders currently on the market. 
Track sensors can also be easily integrated (via the Raspberry Pi's GPIO interface) to enable full automatic control.

Most types of colour light signals (and ground position light signals) are supported. Semaphores are still on my TODO list.

Note that I have tried to make the package platform independent so you can use it to develop your own layout signalling schemes 
without a Raspberry Pi or the associated Pi-SPROG-3 DCC Command station (track sensors can be manually 'triggered' via the
layout schematic to ensure your code is doing what its supposed to do). Full logging is provided to help you develop/debug 
your own schemes - just set the log level to info to see what the package is doing 'under the hood'. And when you do enable
the DCC control aspects, a log level of DEBUG will show you the commands being sent out to the Pi-SPROG-3

Comments and suggestions welcome - but please be kind - the last time I coded anything it was in Ada96 ;)

## Installation
To install use:
<pre>
$ pip install model-railway-signals
</pre>
or alternatively:
<pre>
$ python3 -m pip install model-railway-signals 
</pre>
You may need to ensure you have the latest version of pip installed:
<pre>
$ pip install --upgrade pip
</pre>
or alternatively:
<pre>
$ python3 -m pip install --upgrade pip
</pre>

## Using the package

To use the "public" functions for developing your own layout signalling system:
<code> from model_railway_signals import * </code>

Some examples are included in the repository: https://github.com/johnrm174/model-railway-signalling:

<pre>
'test_simple_example.py' - a simple example of how to use the "signals" and "points" modules to create a
           basic track schematic with interlocked signals/points. Also includes a simple DCC Mapping example
           (1 signal and 2 points) and an external track sensor to provide a "signal passed" event.

'test_approach_control.py' - an example of using automated "approach control" for junction signals. This 
           is where a signal displays a more restrictive aspect (either red or yellow) when a lower-speed 
           divergent route is set, forcing the approaching train to slow down and be prepared to stop. As 
           the train approaches, the signal is "released", allowing the train to proceed past the signal 
           and onto the divergent route. Examples of "Approach on Red" and "Approach on Yellow" are provided. 
           For "Approach on yellow", the signals behind will show the correct flashing yellow aspects.

'test_harman-signalist_sc1.py'- developed primarily for testing using the Harmann Signallist SC1 decoder. 
           Enables the various modes to be selected (includes programming of CVs) and then tested. I used 
           this decoder as it provided the most flexibility for some of my more complex signal types.
           Note that some of the modes will be similar/identical to other manufacturer's DCC signals.

'test_colour_light_signals.py'- developed primarily for testing, but it does provide an example of every 
           signal type and all the control features currently supported.
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
      auto:bool - If the point is to be fully automatic (e.g switched by another point - Default False.

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
Currently supported types:
   Colour Light Signals - 3 or 4 aspect or 2 aspect (home, distant or red/ylw)
          - with or without a position light subsidary signal
          - with or without route indication feathers (maximum of 5)
          - with or without a theatre type route indicator
   Ground Position Light Signals
          - groud position light or shunt ahead position light
          - either early or modern (post 1996) types

signal_sub_type (use when creating colour light signals):
  signal_sub_type.home         (2 aspect - Red/Green)
  signal_sub_type.distant      (2 aspect - Yellow/Green
  signal_sub_type.red_ylw      (2 aspect - Red/Yellow
  signal_sub_type.three_aspect (3 aspect - Red/Yellow/Green)
  signal_sub_type.four_aspect  (4 aspect - Red/Yellow/Double-Yellow/Green)

route_type (use for specifying the route - thise equate to the route feathers):
  route_type.NONE   (no route indication - i.e. not used)
  route_type.MAIN   (main route)
  route_type.LH1    (immediate left)
  route_type.LH2    (far left)
  route_type.RH1    (immediate right)
  route_type.RH2    (rar right)

sig_callback_type (tells the calling program what has triggered the callback):
    sig_callback_type.sig_switched (signal has been switched)
    sig_callback_type.sub_switched (subsidary signal has been switched)
    sig_callback_type.sig_passed ("signal passed" button activated - or triggered by a Timed signal)
    sig_callback_type.sig_updated (signal aspect has been updated as part of a timed sequence)
    sig_callback_type.sig_released (signal "approach release" button has been activated)

create_colour_light_signal - Creates a colour light signal
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the point is to be displayed
      sig_id:int - The ID for the signal - also displayed on the signal button
      x:int, y:int - Position of the point on the canvas (in pixels) 
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
                'update_signal' function use for 3/4 aspect signals - where the displayed aspect will
                depend on the signal ahead - Default True 
      fully_automatic:bool - Creates a signal without any manual controls - Default False

create_ground_position_signal - create a ground position light signal
  Mandatory Parameters:
      Canvas - The Tkinter Drawing canvas on which the point is to be displayed
      sig_id:int - The ID for the signal - also displayed on the signal button
      x:int, y:int - Position of the point on the canvas (in pixels) 
  Optional Parameters:
      orientation:int- Orientation in degrees (0 or 180) - Default is zero
      sig_callback:name - Function to call when a signal event happens - Default is no callback
                        Note that the callback function returns (item_id, callback type)
      sig_passed_button:bool - Creates a "signal Passed" button for automatic control - Default False
      shunt_ahead:bool - Specifies a shunt ahead signal (yellow/white aspect) - default False
      modern_type: bool - Specifies a modern type ground position signal (post 1996) - Default False

set_route_ - Set (and change) the route indication (either feathers or theatre text)
  Mandatory Parameters:
      sig_id:int - The ID for the signal
  Optional Parameters:
      route:signals_common.route_type - MAIN, LH1, LH2, RH1 or RH2 - default 'NONE'
      theatre_text:str  - The text to display in the theatre route indicator - default "NONE"

update_signal - update the aspect of a signal ( based on the aspect of a signal ahead)
              - intended for 3 and 4 aspect and 2 aspect distant colour light signals
  Mandatory Parameters:
      sig_id:int - The ID for the signal
  Optional Parameters:
      sig_ahead_id:int - The ID for the signal "ahead" of the one we want to set

toggle_signal(sig_id) - use for route setting (can use 'signal_clear' to find the state first)

toggle_subsidary(sig_id) - use for route setting (can use 'subsidary_clear' to find the state first)

lock_signal(*sig_id) - use for point/signal interlocking (multiple Signal_IDs can be specified)

unlock_signal(*sig_id) - use for point/signal interlocking (multiple Signal_IDs can be specified)

lock_subsidary(*sig_id) - use for point/signal interlocking (multiple Signal_IDs can be specified)

unlock_subsidary(*sig_id) use for point/signal interlocking (multiple Signal_IDs can be specified)

signal_clear(sig_id) - returns the signal state (True='clear') - to support interlocking

subsidary_clear(sig_id) - returns the subsidary state (True='clear') - to support interlocking

set_signal_override (sig_id*) - Overrides the signal and sets it to DANGER (multiple Signals can be specified)

clear_signal_override (sig_id*) - Reverts the signal to its controlled state (multiple Signals can be specified)

pulse_signal_passed_button (sig_id) - Pulses the signal passed button - use to indicate track sensor events

pulse_signal_release_button (sig_id) - Pulses the approach release button - use to indicate track sensor events

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
                       signal, the signal will be "released" to display the normal aspect. Normally used for
                       diverging routes which have a lower speed restriction to the main line. When a signal
                       is set in "approach control" mode then the signals behind will display the appropriate
                       aspects when updated (based on the signal ahead). for "Release on Red" these would be 
                       the normal aspects. For "Release on Yellow", assuming 4 aspect signals, the signals  
                       behind will display flashing single yellow and flashing double yellow 
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
      sensor_timeout:float - The time period during which further triggers are ignored (default = 3 seconds)
      trigger_period:float - The duration that the sensor needs to remain active before raising a trigger (default = 0.001 seconds)
      sensor_callback - The function to call when the sensor triggers (default is no callback)
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

  map_traintech_signal - Generate the mappings for a TrainTech signal
     Mandatory Parameters:
        sig_id:int - The ID for the signal to create a DCC mapping for
        base_address:int - The base address of the signal (the signal will take 4 consecutive addresses)
     Optional Parameters:
        route_address:int - The address for the route indicator (Feather or Theatre) - Default = 0 (no indicator)
        theatre_route:str - The character to be associated with the Theartre display - Default = "NONE" (no Text)
        feather_route:route_type - The route to be associated with the feather - Default = NONE (no route)

  map_dcc_point
     Mandatory Parameters:
        point_id:int - The ID for the point to create a DCC mapping for
        address:int - the single DCC address for the point
     Optional Parameters:
        state_reversed:bool - Set to True to reverse the DCC logic (default = false)
</pre>

## Pi-Sprog Interface Functions

This provides a basic CBUS interface fpor communicating with the Pi-SPROG3 via the Raspberry Pi UART. It does not provide
a fully-functional interface for All DCC command and control functions - just the minimum set needed to support the driving
of signals and points via a selection of common DCC Accessory decoders.Basic CV Programming is also supported - primarily 
as an aid to testing, but for full decoder programming the recommendation is to use JRMI DecoderPro.
<pre>
  initialise_pi_sprog (Open the comms port to the Pi Sprog)
     Optional Parameters:
        port_name:str - The Serial port to use for communicating with the Pi-SPROG 3 - Default="/dev/serial0",
        baud_rate:int - The baud rate to use for the serial port - Default = 115200,
        dcc_debug_mode:bool - Sets an additional level of logging for the CBUS commands being sent to the Pi-SPROG. 
                            - Will also Request and report the command station status (from the Pi-SPROG-3)

  service_mode_write_cv (programmes a CV in direct bit mode and waits for response)
             (events are only sent if we think the track power is currently switched on)
             (if acknowledgement isn't received within 5 seconds then the request times out)
     Mandatory Parameters:
        cv:int - The CV (Configuration Variable) to be programmed
        value:int - The value to programme

  request_dcc_power_on (sends a request to switch on the track power and waits for acknowledgement)
         returns True if we have received acknowledgement that Track Power has been turned on
         returns False if acknowledgement isn't received within 5 seconds (i.e. request timeout)

  request_dcc_power_off (sends a request to switch off the track power and waits for acknowledgement)
         returns True if we have received acknowledgement that Track Power has been turned off
         returns False if acknowledgement isn't received within 5 seconds (i.e. request timeout)
</pre>



