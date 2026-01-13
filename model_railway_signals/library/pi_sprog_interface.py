#--------------------------------------------------------------------------------------------------
# This provides a basic CBUS interface fpor communicating with the Pi-SPROG3 via the Raspberry Pi 
# UART. It does not provide a fully-functional interface for all DCC command and control functions,
# just the minimum set needed to support the driving of signals and points via a selection of common
# DCC Accessory decoders. Basic CV Programming is also supported - primarily as an aid to testing. 
# For full decoder programming the recommendation is to use JRMI DecoderPro or similar.
#--------------------------------------------------------------------------------------------------
#
# External API - the classes and functions (used by the Schematic Editor):
# 
#   sprog_connect() - Opens and configures the serial comms port to the Pi Sprog and issues
#                     a 'Request Command Station Status' command to confirm connectivity.
#                     Returns True - if communication has been established (otherwise False)
#      Optional Parameters:
#         port_name:str - The serial port to use for the Pi-SPROG 3 - Default="/dev/serial0",
#         baud_rate:int - The baud rate to use for the serial port - Default = 460800,
#         dcc_address_mode:int - (1 for 'no offset', 2 for '+4', 3 for '-4')
#         dcc_debug_mode:bool - Set to 'True' for enhanced debug logging
#
#   sprog_disconnect() - Performs an ordely shutdown of communications and closes the comms port 
#                     Returns True - if the communications port has been closed (otherwise False)
#
#   service_mode_read_cv - Queries a CV in direct bit mode and waits for response
#                       (events are only sent if the track power is currently switched on)
#                       (request times out after 5 secs if the request was unsuccessful)
#      Mandatory Parameters:
#         cv:int - The CV (Configuration Variable) to be read
#            returns the current value of the CV if a response is received
#            returns None - if the request fails or the request times out
# 
#   service_mode_write_cv - programmes a CV in direct bit mode and waits for response
#                       (events are only sent if the track power is currently switched on)
#                       (request times out after 5 secs if the request was unsuccessful)
#      Mandatory Parameters:
#         cv:int - The CV (Configuration Variable) to be programmed
#         value:int - The value to programme
#            returns True - if we have acknowledgement that the CV has been programmed
#            returns False - if the CV programming fails or the request times out
# 
#   request_dcc_power_on - sends request to switch on the power and waits for acknowledgement
#                  (requests only sent if the Comms Port has been successfully opened/configured)
#            returns True - if we have acknowledgement that Track Power has been turned on
#            returns False - if the request times out
# 
#   request_dcc_power_off - sends request to switch off the power and waits for acknowledgement
#                  (requests only sent if the Comms Port has been successfully opened/configured)
#          returns True - if we have  acknowledgement that Track Power has been turned off
#          returns False - if the request times out
#
#   enable_status_reporting(callback) - Enable reporting
#   disable_status_reporting() - Disable Reporting
#
#   request_loco_session(dcc_address) - generates a loco session and returns session_id
#   release_loco_session(session_id) - releases the locomotive session
#   set_loco_speed_and_direction(session_id:int, speed:int, forward:bool)
#   send_emergency_stop(session_id) - Emergency Stops the loco
#
# API functions used associated with DCC-command-triggered sounds:
#   add_dcc_sound_mapping(address:int, state:bool, fully_qualified_sound_filename:str):
#   reset_dcc_sound_mappings() - Delete all current mappings
#
# Classes and functions used by the other library modules:
#
#   send_accessory_short_event(address:int, active:bool) - sends out a CBUS command to the
#          Pi-Sprog to be translated into a DCC command for transmission on the DCC Bus
#
# --------------------------------------------------------------------------------------------
#
# Note that the Pi-SPROG-3 needs the UART interfaces to be swapped so that
# serial0 is routed to the GPIO connector instead of being used for BlueTooth.
# The configuration procedure is documented below
#
# 1) Download the uart-rtscts overlay:
#    wget https://raw.github.com/HiassofT/AtariSIO/master/contrib/rpi/uart- ctsrts.dtbo
# 2) Copy it to the required directory:
#    sudo cp uart-ctsrts.dtbo /boot/overlays/
# 3) Add the overlays to the end of config.txt:
#    sudo nano /boot/config.txt - and then add the following lines:
#       dtoverlay=miniuart-bt
#       enable_uart=1
#       dtoverlay=uart-ctsrts
# 4) Edit the command line to prevent the Kernel using the UART at startup:
#    sudo nano /boot/cmdline.txt 
#        Remove ‘console=serial0,115200’
#        Note that this file must contain only one line
# 5) Reboot the Raspberry Pi
#
# --------------------------------------------------------------------------------------------

import threading
import serial
import time
import logging
import queue

from . import common

# Global class for the Serial Port (port is configured/opened later)
serial_port = serial.Serial()

# Global constants used when transmitting CBUS messages
can_bus_id = 1                       # The arbitary CANBUS ID we will use for the Pi
pi_cbus_node = 258                   # The CBUS Node ID Of the Pi-Sprog (This is updated with that reported in the STAT)
transmit_delay = 0.02                # The delay between sending CBUS Messages (in seconds)

# Global Flag to enable enhanced debug logging for the Pi-SPROG interface
debug = False                       # Enhanced Debug logging - set by the sprog_connect call

# Global flags used to communicate between the Rx thread and the calling function (in the main thread)
ton_response = False                # Flag to confirm that we have had a response that track power is on
tof_response = False                # Flag to confirm that we have had a response that track power is off
rstat_response = False              # Flag to confirm we have had a RSTAT response (on initialisation)
qnn_response = False                # Flag to confirm we have had a PNN response
service_mode_response = None        # The response code from the sstat response (program a CV)
service_mode_cv_value = None        # The returned value from the pcvs response (query a CV)
service_mode_cv_address = None      # The reported CV address from the pcvs response
service_mode_session_id = None      # The reported session ID from the sstat/pcvs responses

# Global 'one up' session ID (to match up the CV programming responses with the requests)
session_id = 1

# Global variables to coordinate serial port access between the various threads
port_close_initiated = False        # Signal to the Rx/Tx threads to shut down
rx_thread_terminated = True         # Rx thread terminated flag
tx_thread_terminated = True         # Tx thread terminated flag

# The global output buffer for messages sent from the main thread to the SPROG Tx Thread
# We use a seperate thread so we can throttle the Tx rate without blocking the main thread
output_buffer = queue.Queue()

# Global variable to hold the DCC Addressing Mode - address offset applied when sending out
# short accessory commands (1 = No Offset, 2 = Plus 4 Offset, 3 = minus 4 Offset)
address_mode = 1

# Global variable to hold the SPROG status callback reference
status_callback = None

#------------------------------------------------------------------------------
# Common function used by the main thread to wait for responses in other threads.
# When the specified function returns True, the function exits and returns True.
#------------------------------------------------------------------------------

def wait_for_response(timeout:float,test_for_response_function):
    response_received = False
    timeout_end = time.time() + timeout  # Calculate the end time once
    while time.time() < timeout_end:
        response_received = test_for_response_function()
        if response_received: break
        time.sleep(0.002)
    return(response_received)

#------------------------------------------------------------------------------
# Internal thread to write queued CBUS messages to the Serial Port with a
# short delay in between each message. We do this because some decoders don't
# seem to process all messages if sent to them in quick succession - and if the
# decoder "misses" an event the signal/point may end up in an erronous state.
#------------------------------------------------------------------------------

def thread_to_send_buffered_data():
    global tx_thread_terminated
    # Reset the output buffer and clear down the queue to be on the safe side
    if serial_port.is_open: serial_port.reset_output_buffer()
    output_buffer.queue.clear()
    # The main thread triggers a shutdown of this thread by setting port_close_initiated to TRUE
    # Just before this thread exits, it sets tx_thread_active to FALSE to confirm thread is exiting
    tx_thread_terminated = False
    while not (port_close_initiated and output_buffer.empty()):
        # Get the next message to transmit from the buffer
        if not output_buffer.empty():
            command_string = output_buffer.get()
            # Write the CBUS Message to the serial port (as long as the port is open)
            if serial_port.is_open:
                try:
                    serial_port.write(bytes(command_string,"Ascii"))
                    # Print the Transmitted message (if the appropriate debug level is set)
                    if debug: logging.debug("Pi-SPROG: Tx thread - Sent CBUS Message: "+command_string)
                except Exception as exception:
                    logging.error("Pi-SPROG: Tx thread - Error sending CBUS Message: "+command_string+" - "+str(exception))
                    time.sleep(1.0)
            else:
                if debug: logging.debug("Pi-SPROG: Tx thread - Not sending CBUS Message: "+command_string+" - port is closed")
        # Sleep (transmit_delay) before sending the next CBUS message (to throttle the Tx rate). 
        # This also ensures the thread doesn't hog all the CPU time
        time.sleep(transmit_delay)
    if debug: logging.debug("Pi-SPROG: Tx Thread - exiting")
    tx_thread_terminated = True
    return()
    
#------------------------------------------------------------------------------
# Internal thread to read CBUS messages from the Serial Port and process them
# We are only really interested in the response from byte_string [7] onwards
# byte_string[7] and byte_string[8] are the Hex representation of the 1 byte OPCODE 
# The remaining characters represent the data bytes (0 to 7 associated with the OPCODE)
# Finally the string is terminated with a ';' (Note there is no '\r' required)
#------------------------------------------------------------------------------

def thread_to_read_received_data ():
    global rx_thread_terminated
    # Reset the input buffer to be on the safe side
    if serial_port.is_open: serial_port.reset_input_buffer()
    # The main thread triggers a shutdown of this thread by setting port_close_initiated to TRUE
    # Just before this thread exits, it sets rx_thread_active to FALSE to confirm thread is exiting
    rx_thread_terminated = False
    while not port_close_initiated:
        # Read the serial port to retrieve the bytes in the Rx buffer (as long as the port is open)
        if serial_port.is_open:
            # Read from the port until we get the GridConnect Protocol message termination character
            # Or we get notified to shutdown (main thread sets port_close_initiated to True)
            byte_string = bytearray()
            while not port_close_initiated:
                if serial_port.in_waiting > 0:
                    try:
                        received_data = serial_port.read()
                    except Exception as exception:
                        logging.error("Pi-SPROG: Rx thread - Error reading serial port - "+str(exception))
                        time.sleep(1.0)
                    else:
                        byte_string = byte_string + received_data
                        if chr(byte_string[-1]) == ";": break
                # Ensure the loop doesn't hog all the CPU time
                time.sleep(0.001)
            # Process the GridConnect Protocol message (as long as it is complete)
            if len(byte_string) > 0 and chr(byte_string[-1]) == ";":
                # Log the Received message (if the appropriate debug level is set)
                if debug: logging.debug("Pi-SPROG: Rx thread - Received CBUS Message: "+byte_string.decode('Ascii')+"\r")
                # Note that there is exception handling around the decoding of the message to
                # deal with any "edge-case" exceptions we might get with corrupted messages
                try:
                    # Convert to String and remove the start/end markers
                    msg_str = byte_string.decode('Ascii').strip(':;')
                    # Find where the OpCode is in the message (depending on the message type)
                    # Normal(N): N [Data...] - Opcode position is variable - Position of 'N' + 1
                    # Standard (S): S hhhh [OpCode] ...5 (S + 4 hex digits for 11-bit ID)
                    # Extended (X): X hhhhhhhh [OpCode] ...9 (X + 8 hex digits for 29-bit ID)
                    if 'N' in msg_str:
                        start_pos = msg_str.find('N') + 1
                    elif msg_str.startswith('S'):
                        start_pos = 5
                    elif msg_str.startswith('X'):
                        start_pos = 9
                    else:
                        start_pos = 0
                        logging.warning("Pi-SPROG: Rx thread - Unhandled Message Type: "+byte_string.decode('Ascii')+"\r")
                    if start_pos > 0:
                        # Extract exactly 2 characters for the OpCode
                        op_hex = msg_str[start_pos : start_pos + 2]
                        op_code = int(op_hex, 16)
                        # Command Station Status Report (0xE3 = 227 decimal)
                        if op_code == 0xE3: process_stat_message(byte_string)
                        # Response to confirm Track Power is OFF (0x04 = 4 decimal)
                        elif op_code == 0x04: process_tof_message(byte_string)
                        # Response to confirm Track Power is ON (0x05 = 5 decimal)
                        elif op_code == 0x05: process_ton_message(byte_string)
                        # Report CV value in service programming mode (0x85 = 133 decimal)
                        elif op_code == 0x85: process_pcvs_message(byte_string)
                        # Report Service Mode Status response (0x4C = 76 decimal)
                        elif op_code == 0x4C: process_sstat_message(byte_string)
                        # Accessory Data Command for multimeter mode (0xD0 = 208 decimal) 
                        elif op_code == 0xD0: process_accessory_data(byte_string)
                        # Engine Report / Response to DLOC (0xE1 = 225 decimal)
                        elif op_code == 0xE1: process_ploc_message(byte_string)
                        # Error Code (from request session) ERR (0x63)
                        elif op_code == 0x63: process_error_message(byte_string)
                except:
                    # Ignore any heartbeat or Bus Sync Messages
                    if msg_str not in ("S4"):
                        logging.warning("Pi-SPROG: Rx thread - Couldn't decode CBUS Message: "+byte_string.decode('Ascii')+"\r")
        # Ensure the thread doesn't hog all the CPU time
        time.sleep(0.001)
    if debug: logging.debug("Pi-SPROG: Rx Thread - exiting")
    rx_thread_terminated = True
    return()

#------------------------------------------------------------------------------
# Internal function running in the main Tkinter Thread to handle status
# and current telemetry updates from the SPROG. Returned data comprises a
# dictionary of Values that have been updated
#------------------------------------------------------------------------------

def report_status(status:dict):
    if status_callback is not None: status_callback(status)

#------------------------------------------------------------------------------
# Internal function to process Accessory Data Commands (Voltage / Current reporting)
#------------------------------------------------------------------------------

def process_accessory_data(byte_string):
    logging.debug ("Pi-SPROG: Rx thread - Received ADC (Accessory Data Command) message")
    # Process the message (with exception handling just in case)
    try:
        # Convert to String and remove the start/end markers
        msg_str = byte_string.decode('Ascii').strip(':;')
        # The following code uses Indices based on the stripped GridConnect string:
        # Index:    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7
        # String:   S B 0 0 0 N D 0 0 1 0 0 0 1 0 0 7 4
        # N is at index 5. Opcode D0 is at 6,7. Node ID 0102 is at 8,9,10,11.
        n_index = msg_str.find('N')
        # The Telemetry Sub-code (01 or 02) starts 8 characters after 'N'
        # (2 for OpCode, 4 for NodeID, 2 for padding/index)
        type_start = n_index + 9
        data_type_hex = msg_str[type_start : type_start + 2]
        # The Value (4 hex chars) follows immediately
        value_hex = msg_str[type_start + 2 : type_start + 6]
        raw_value = int(value_hex, 16)
        # Work out whether voltage or current is being reported
        if data_type_hex == "01":
            # Current Reporting is in mA so we convert to Amps (e.g., 1200mA -> 1.2A)
            current_amps = float(raw_value / 1000.0)
            if debug: logging.debug(f"Pi-SPROG: Rx thread - Telemetry - DCC Bus Current: {current_amps:.3f} A")
            # Pass the values back into the main Tkinter thread
            common.execute_function_in_tkinter_thread(lambda: report_status({"current": current_amps}))
        elif data_type_hex == "02":
            # Voltage reporting is in decivolts (1/10th Volt) so we convert to Volts (e.g., 145 -> 14.5V)
            voltage_volts = float(raw_value / 10.0)
            if debug: logging.debug(f"Pi-SPROG: Rx thread - Telemetry - DCC Bus Voltage: {voltage_volts:.1f} V")
            # Pass the values back into the main Tkinter thread
            common.execute_function_in_tkinter_thread(lambda: report_status({"voltage": voltage_volts}))
    except Exception as exception:
        logging.error("Pi-SPROG: Error parsing Accessory Data Command (ADC/D0) Message")
        logging.error(exception)
    return()

#------------------------------------------------------------------------------
# Internal function to process a Command Station Status Report (STAT message)
# Sets the rstat_response flag - to signal back into the main thread
#------------------------------------------------------------------------------

def process_stat_message(byte_string):
    global rstat_response, pi_cbus_node
    # Respond to the trigger function (waiting in the main thread for a response)
    rstat_response = True
    logging.debug ("Pi-SPROG: Rx thread - Received STAT (Command Station Status) message")
    # Process the message (with exception handling just in case)
    try:
        # Convert to String and remove the start/end markers
        msg_str = byte_string.decode('Ascii').strip(':;')
        # Find where the OpCode is in the message (depending on the message type)
        # Normal(N): N [Data...] - Opcode position is variable - Position of 'N' + 1
        # The following code uses Indices based on the stripped GridConnect string:
        # Index:    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3
        # String:   S B 0 0 0 N E 3 D 0 0 1 0 2 0 8 0 3 0 1 0 A 7 4
        # Find 'N', then skip 'N' (1 char) and the OpCode 'E3' (2 chars) = +3
        d_start = msg_str.find('N') + 3
        # Extract values using dynamic offsets from d_start
        # Node ID (2 bytes / 4 hex chars)
        pi_cbus_node = int(msg_str[d_start : d_start+4], 16)
        # Command Station ID (1 byte / 2 hex chars)
        command_station_id = int(msg_str[d_start+4 : d_start+6], 16)
        # Flags (1 byte / 2 hex chars)
        flags = int(msg_str[d_start+6 : d_start+8], 16)
        # Firmware Version (3 bytes / 6 hex chars)
        v_maj = int(msg_str[d_start+8 : d_start+10], 16)
        v_min = int(msg_str[d_start+10 : d_start+12], 16)
        v_bld = int(msg_str[d_start+12 : d_start+14], 16)
        firmware_version = f"{v_maj}.{v_min}.{v_bld}"
        # Flag Mapping (Standard CBUS / SPROG)
        sprog_error_flag     = bool(flags & 0x01)       # Bit 0
        track_error_flag     = bool(flags & 0x02)       # Bit 1
        track_power_on_flag  = bool(flags & 0x04)       # Bit 2
        bus_active_flag      = bool(flags & 0x08)       # Bit 3
        emergency_stop_flag  = bool(flags & 0x10)       # Bit 4
        reset_performed_flag = bool(flags & 0x20)       # Bit 5
        service_mode_flag    = bool(flags & 0x40)       # Bit 6
        # Report the status back into the main Tkinter Thread
        status = {
            "cbus_node"        : str(pi_cbus_node),
            "firmware_version" : firmware_version,
            "service_mode"     : str(service_mode_flag),
            "reset_performed"  : str(reset_performed_flag),
            "track_power_on"   : str(track_power_on_flag),
            "track_error"      : str(track_error_flag),
            "bus_active_flag"  : str(bus_active_flag),
            "sprog_error"      : str(sprog_error_flag),
            "emergency_stop"   : str(emergency_stop_flag) }
        common.execute_function_in_tkinter_thread(lambda: report_status(status))
        # Log out the status report
        if debug:
            logging.debug("    CBUS Node Id       :"+str(pi_cbus_node))
            logging.debug("    Command Station Id :"+str(command_station_id))
            logging.debug("    Firmware Version   :"+str(firmware_version))
            logging.debug("    Service Mode       :"+str(service_mode_flag))
            logging.debug("    Reset Done         :"+str(reset_performed_flag))
            logging.debug("    Emg Stop Perf      :"+str(emergency_stop_flag))
            logging.debug("    Track Power On     :"+str(track_power_on_flag))
            logging.debug("    DCC Bus Active     :"+str(bus_active_flag))
            logging.debug("    Track Power Error  :"+str(track_error_flag))
            logging.debug("    SPROG Error        :"+str(sprog_error_flag))
    except Exception as exception:
        logging.error("Pi-SPROG: Error parsing Command Station Status (STAT) Message")
        logging.error(exception)
    return()

#------------------------------------------------------------------------------
# Internal function to process a Track power responses (TOF/TON messages)
# Sets the appropriate acknowledge flag - to signal back into the main thread
#------------------------------------------------------------------------------

def process_tof_message(byte_string):
    global tof_response
    # Respond to the trigger function (waiting in the main thread for a response)
    tof_response = True
    logging.debug ("Pi-SPROG: Rx thread - Received TOF (Track OFF) acknowledgement")
    return()
                        
def process_ton_message(byte_string):
    global ton_response
    # Respond to the trigger function (waiting in the main thread for a response)
    ton_response = True
    logging.debug ("Pi-SPROG: Rx thread - Received TON (Track ON) acknowledgement")
    return()

#------------------------------------------------------------------------------
# Internal function to process a Report CV response (PCVS message)
# Sets the service_mode_cv_value - to signal back into the main thread
#------------------------------------------------------------------------------

def process_pcvs_message(byte_string):
    global service_mode_cv_value, service_mode_cv_address, service_mode_session_id
    logging.debug ("Pi-SPROG: Rx thread - Received PCVS (CV Response) message")
    # Process the message (with exception handling just in case)
    try:
        # Convert to String and remove the start/end markers
        msg_str = byte_string.decode('Ascii').strip(':;')
        # The following code uses Indices based on the stripped GridConnect string:
        # Index:    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7
        # String:   S B 0 0 0 N 8 5 0 1 0 0 0 A 0 5 7 4
        # Find 'N', then skip 'N' (1 char) and the OpCode '85' (2 chars) = +3
        d_start = msg_str.find('N') + 3
        # Extract values using dynamic offsets from d_start
        # Session ID (1 byte / 2 hex chars)
        session_id = int(msg_str[d_start : d_start+2], 16)
        # CV Address is 2 bytes (High Byte + Low Byte)
        # We extract both and combine them (High << 8 | Low)
        cv_high = int(msg_str[d_start+2 : d_start+4], 16)
        cv_low  = int(msg_str[d_start+4 : d_start+6], 16)
        cv = (cv_high << 8) | cv_low
        # CV Value (1 byte / 2 hex chars)
        value = int(msg_str[d_start+6 : d_start+8], 16)
        if debug: logging.debug(f"Pi-SPROG: Rx thread - Received PCVS (Report CV) - Session:{session_id}, CV:{cv}, Value:{value}")
        # Respond to the trigger function (waiting in the main thread for a response)
        service_mode_session_id = session_id
        service_mode_cv_address = cv
        service_mode_cv_value = value
    except Exception as exception:
        logging.error("Pi-SPROG: Error parsing Report CV (PCVS) Message")
        logging.error(exception)
        return()

#------------------------------------------------------------------------------
# Internal function to process a service mode status response (SSTAT message)
# Sets the service_mode_response - to signal back into the main thread
#------------------------------------------------------------------------------

def process_sstat_message(byte_string):
    global service_mode_response
    global service_mode_session_id
    logging.debug ("Pi-SPROG: Rx thread - Received SSTAT (Service Mode Status Response) message")
    # Process the message (with exception handling just in case)
    try:
        # Convert to String and remove the start/end markers
        msg_str = byte_string.decode('Ascii').strip(':;')
        # The following code uses Indices based on the stripped GridConnect string:
        # Index:    0 1 2 3 4 5 6 7 8 9 0 1 2 3
        # String:   S B 0 0 0 N 4 C 0 1 0 3 7 4
        # Find 'N', then skip 'N' (1 char) and the OpCode '4C' (2 chars) = +3
        d_start = msg_str.find('N') + 3
        # Extract values using dynamic offsets from d_start
        # Session ID (1 byte / 2 hex chars)
        session_id = int(msg_str[d_start : d_start+2], 16)
        # Service Mode Status Code (1 byte / 2 hex chars)
        service_mode_status = int(msg_str[d_start+2 : d_start+4], 16)
        # Map the status code to a human-readable string
        if service_mode_status == 0: status_text = "Reserved"
        elif service_mode_status == 1: status_text = "No Acknowledge"
        elif service_mode_status == 2: status_text = "Overload on Programming Track"
        elif service_mode_status == 3: status_text = "Write Acknowledge"
        elif service_mode_status == 4: status_text = "Busy"
        elif service_mode_status == 5: status_text = "CV Out of Range"
        else: status_text = f"Unrecognised response code: {service_mode_status}"
        if debug: logging.debug(f"Pi-SPROG: Rx thread - Received SSTAT (Service Mode Status) - Session:{session_id}, Status:{status_text}")
        # Respond to the trigger function (waiting in the main thread for a response)
        service_mode_session_id = session_id
        service_mode_response = service_mode_status
    except Exception as exception:
        logging.error("Pi-SPROG: Error parsing Service Mode Status (SSTAT) Message")
        logging.error(exception)
    return()

#------------------------------------------------------------------------------
# Internal function to process any ERR messages received from the SPROG
#------------------------------------------------------------------------------

def process_error_message(byte_string):
    logging.debug("Pi-SPROG: Rx thread - Received ERROR message")
    try:
        msg_str = byte_string.decode('Ascii').strip(':;')
        # :SB000N63000302;
        # OpCode is 63. Address is 0003. Error is 02.
        d_start = msg_str.find('N') + 3
        error_code = int(msg_str[d_start+4 : d_start+6], 16)
        if error_code == 1:
            logging.error("Pi-SPROG: Received Error Message - Loco Stack Full")
        if error_code == 2:
            logging.error("Pi-SPROG: Received Error Message - Loco Address Taken")
        if error_code == 3:
            logging.error("Pi-SPROG: Received Error Message - Session not Present")
        if error_code == 4:
            logging.error("Pi-SPROG: Received Error Message - Consist (loco groups) Empty")
        if error_code == 5:
            logging.error("Pi-SPROG: Received Error Message - Loco not Found")
        if error_code == 6:
            logging.error("Pi-SPROG: Received Error Message - Can Bus Error")
        if error_code == 7:
            logging.error("Pi-SPROG: Received Error Message - Invalid Request")
        if error_code == 8:
            logging.error("Pi-SPROG: Received Error Message - Session Cancelled")
    except Exception as exception:
        logging.error("Pi-SPROG: Error parsing ERROR message")
        logging.error(exception)
    return()

#------------------------------------------------------------------------------
# Internal function to encode a CBUS Command in the GridConnect protocol and send to
# the specified comms port. The format of a CBUS Command is summarised as follows:
#
# CBUS Commands are sent as an ASCII strings starting with ':' and followed by 'S'
# The next 4 characters are the Hex representation of the 11 bit CAN Header
#         Major Priority - Bits 9 & 10 (00 = Emergency; 01 = High Priority, 10 = Normal)
#         Minor Priority - Bits 7 & 8 (00 = High, 01 = Above Normal, 10 = Normal, 11 = Low)
#         CAN BUS ID - Bits 0-6 (CAN segment unique ID)
#     Note that The 11 CAN Header Bits are encoded into the 2 Bytes LEFT JUSTIFIED
#     So the Header bytes end up as: P P P P A A A A | A A A 0 0 0 0 0
# The next character is 'N' - specifying a 'Normal' CBUS Frame (all we need to use)
# The next 2 characters are the Hex representation of the 1 byte OPCODE 
# The remaining characters represent the data bytes (0 to 7 associated with the OPCODE)
# Finally the string is terminated with a ';' (Note there is no '\r' required)
#
# References for Header Encoding - CBUS Developers Guide - Section 6.1, 6.4, 12.2
#
# Example - can_id=99 , mj_pri=2, min_pri=2, op_code=9 (RTON - request track on)
# encodes into a CBUS Command 'SAC60N09;'
#------------------------------------------------------------------------------

def send_cbus_command (mj_pri:int, min_pri:int, op_code:int, *data_bytes:int):
    if (mj_pri < 0 or mj_pri > 2):
        logging.error("Pi-SPROG: CBUS Command - Invalid Major Priority "+str(mj_pri))
    elif (min_pri < 0 or min_pri > 3):
        logging.error("Pi-SPROG: CBUS Command - Invalid Minor Priority "+str(min_pri))
    elif (op_code < 0 or op_code > 255):
        logging.error("Pi-SPROG: CBUS Command - Op Code out of range "+str(op_code))
    else:
        # Encode the CAN Header (11-bit Identifier)
        # Pri1 (bits 10-9), Pri2 (bits 8-7), CAN ID (bits 6-0)
        header_val = (mj_pri << 9) | (min_pri << 7) | can_bus_id
        # Start building the GridConnect Protocol string
        # :S hhhh N [OpCode][Data...];
        command_string = ":S" + format(header_val, "04X") + "N" + format(op_code, "02X")
        # Add the Data Bytes associated with the OpCode
        for data_byte in data_bytes:
            command_string = command_string + format(data_byte, "02X")
        # Finally - add the command string termination character
        command_string = command_string + ";"
        # Add the command to the output buffer (to be picked up by the Tx thread)
        output_buffer.put(command_string)
        if debug: logging.debug("Pi-SPROG: Tx thread - Queued CBUS Command: " + command_string)
        return()

#------------------------------------------------------------------------------
# Externally Called Function to establish basic comms with the PI-SPROG
# (opening the port and sending an RSTAT command to confirm connectivity)
# With dcc_debug_mode=True an "enhanced" level of debug logging is enabled
# namely logging of all the CBUS commands sent to the Pi SPROG and other
# log messages associated with internal state of the threads
#------------------------------------------------------------------------------

def sprog_connect (port_name:str="/dev/serial0",
                   baud_rate:int = 115200,
                   dcc_address_mode:int=1,
                   dcc_debug_mode:bool = False):
    global debug, address_mode
    pi_sprog_connected = False
    if not isinstance(port_name, str):
        logging.error("Pi-SPROG: sprog_connect - Port name must be specified as a string")
    elif not isinstance(baud_rate, int):
        logging.error("Pi-SPROG: sprog_connect - Baud rate must be specified as an integer")
    elif not isinstance(dcc_address_mode, int) or dcc_address_mode < 1 or dcc_address_mode > 3:
        logging.error("Pi-SPROG: sprog_connect - dcc_address_mode  must be specified as an integer (1-3)")
    elif not isinstance(dcc_debug_mode, bool):
        logging.error("Pi-SPROG: sprog_connect - Enhanced debug flag must be specified as a boolean")
    else:
        # If the serial port is already open then close it before re-configuring
        if serial_port.is_open: sprog_disconnect()
        # Assign the global "enhanced debugging" flag and address_mode parameters
        debug = dcc_debug_mode
        address_mode = dcc_address_mode
        # Configure the port - note the zero timeout so the Rx thread does not block
        # The Rx thread combines the data read from the port into 'complete' CBUS messages
        serial_port.port = port_name
        serial_port.baudrate = baud_rate
        serial_port.bytesize = 8
        serial_port.timeout = 0  # Non blocking - returns immediately
        serial_port.parity = serial.PARITY_NONE
        serial_port.stopbits = serial.STOPBITS_ONE
        # Try to open the serial port (catching any exceptions)
        logging.debug("Pi-SPROG: Opening Serial Port: "+port_name+" - baud: "+str(baud_rate))
        try:
            serial_port.open()
        except Exception as exception:
            # If the attempt to open the serial port fails then we catch the exception (and return)
            logging.error("Pi-SPROG: Error opening Serial Port - "+str(exception))
        else:
            # The port has been successfully opened. We now start the Rx and Tx threads.
            # These are shut down in a controlled manner by the sprog_disconnect function but
            # if all else fails we set to Daemon so they will terminate with the main programme
            if rx_thread_terminated:
                if debug: logging.debug("Pi-SPROG: Starting Rx Thread")
                rx_thread = threading.Thread (target=thread_to_read_received_data)
                rx_thread.setDaemon(True)
                rx_thread.start()
            if tx_thread_terminated:
                if debug: logging.debug("Pi-SPROG: Starting Tx Thread")
                tx_thread = threading.Thread (target=thread_to_send_buffered_data)
                tx_thread.setDaemon(True)
                tx_thread.start()
            # Short delay to allow the threads to fully start up before we continue
            time.sleep(0.1)
            # To verify full connectivity, we query the command station status
            # query_command_station_status will return TRUE if a response was received
            pi_sprog_connected = query_command_station_status()
            if pi_sprog_connected: logging.info("Pi-SPROG: Successfully connected to Pi-SPROG")
    return(pi_sprog_connected)

#------------------------------------------------------------------------------
# Externally Called Function to disconnect from the PI-SPROG (close the port)
# so that the port is free for other applications to use if required.
#------------------------------------------------------------------------------

def sprog_disconnect():
    global port_close_initiated
    def response_received(): return(rx_thread_terminated and tx_thread_terminated)
    pi_sprog_disconnected = False
    if serial_port.is_open:
        # Ensure Status reporting is turned off before we disconnect
        if status_callback is not None:
            disable_status_reporting()
            time.sleep(0.3)
        if debug: logging.debug("Pi-SPROG: Shutting down Tx and Rx Threads")
        port_close_initiated = True
        # Wait until we get confirmation the Threads have been terminated
        wait_for_response(1.0, response_received)
        if not tx_thread_terminated: logging.error("Pi-SPROG: Tx thread failed to terminate")
        if not rx_thread_terminated: logging.error("Pi-SPROG: Rx thread failed to terminate") 
        # Try to close the serial port (with exception handling)
        if debug: logging.debug ("Pi-SPROG: Closing Serial Port")
        try:
            serial_port.close()
        except Exception as exception:
            logging.error("Pi-SPROG: Error closing Serial Port - "+str(exception))
    if not serial_port.is_open:
        logging.info("Pi-SPROG: Successfully disconnected from Pi-SPROG")
        pi_sprog_disconnected = True
    # Reset the port_close_initiated flag (ready for the next time)
    port_close_initiated = False
    return(pi_sprog_disconnected)

#------------------------------------------------------------------------------
# Function to send a RSTAT (Request command Station Status) command (response logged)
# Returns True if successful and False if no response is received (timeout)
# Results in a character string of ':SA020N0C' being sent out to the Pi-SPROG
# The only bit we really care about is the bit after the 'N', which is the op code
# we are seding out (in this case '0C' ) - see above for info on the header
#------------------------------------------------------------------------------

def query_command_station_status():
    global rstat_response
    def response_received(): return(rstat_response)
    rstat_response = False
    # Only bother sending commands to the Pi Sprog if the serial port has been opened
    if serial_port.is_open:
        # Query the status of the command station to confirm connectivity
        logging.debug("Pi-SPROG: Sending RSTAT command (Request Command Station Status)")
        # For RSTAT(0C), TON(09)and TOF(08) the Priority must be set to high
        send_cbus_command(mj_pri=0, min_pri=0, op_code=0x0C)
        # Wait for the response (with a 5 second timeout)
        wait_for_response(5.0, response_received)
        if rstat_response: logging.debug ("Pi-SPROG: Received STAT (Command Station Status Report)")
        else: logging.error("Pi-SPROG: Request Command Station Status failed")
    else:
        logging.warning("Pi-SPROG: Cannot Request Command Station Status - SPROG is disconnected")
    return(rstat_response)

#------------------------------------------------------------------------------
# Externally Called Function to Register for DCC power status updates
#------------------------------------------------------------------------------

registered_dcc_power_state_callbacks = []
def register_power_state_callback(callback):
    global registered_dcc_power_state_callbacks
    if callback not in registered_dcc_power_state_callbacks:
        registered_dcc_power_state_callbacks.append(callback)

#------------------------------------------------------------------------------
# Externally Called Function to turn on the track power
#------------------------------------------------------------------------------

def request_dcc_power_on():
    global ton_response
    def response_received(): return(ton_response)
    ton_response = False
    # Only bother sending commands to the Pi Sprog if the serial port has been opened
    if serial_port.is_open:
        # Send the command to switch on the Track Supply (to the DCC Bus)
        logging.debug ("Pi-SPROG: Sending RTON command (Request Track Power On)")
        # For RSTAT(0C), TON(09)and TOF(08) the Priority must be set to high
        send_cbus_command (mj_pri=0, min_pri=0, op_code=0x09)
        # Wait for the response (with a 1 second timeout)
        wait_for_response(5.0, response_received)
        if ton_response: logging.info("Pi-SPROG: Track power has been turned ON")
        else: logging.error("Pi-SPROG: Request to turn on Track Power failed")
        # Give things time to get established before sending out any commands
        time.sleep (0.2)
        # Tell the application to send out any DCC commands that may have been 'issued' before
        # DCC Power was turned on but not transmitted (as they would have been silently ignored)
        # We also transmit the DCC power state to anyone who has registered a callback
        if ton_response:
            for power_status_changed_callback in registered_dcc_power_state_callbacks:
                power_status_changed_callback(True)
            common.sprog_transmit_all()
    return(ton_response)

#------------------------------------------------------------------------------
# Externally Called Function to turn off the track power
#------------------------------------------------------------------------------

def request_dcc_power_off():
    global tof_response
    def response_received(): return(tof_response)
    tof_response = False
    # Only bother sending commands to the Pi Sprog if the serial port has been opened
    if serial_port.is_open:
        # Send the command to switch on the Track Supply (to the DCC Bus)
        logging.debug("Pi-SPROG: Sending RTOF command (Request Track Power Off)")
        # For RSTAT(0C), TON(09)and TOF(08) the Priority must be set to high
        send_cbus_command(mj_pri=0, min_pri=0, op_code=0x08)
        # Wait for the response (with a 1 second timeout)
        wait_for_response(5.0, response_received)
        if tof_response:
            logging.info("Pi-SPROG: Track power has been turned OFF")
            # We transmit the DCC power state to anyone who has registered a callback
            for power_status_changed_callback in registered_dcc_power_state_callbacks:
                power_status_changed_callback(False)
        else:
            logging.error("Pi-SPROG: Request to turn off Track Power failed")
    return(tof_response)

#------------------------------------------------------------------------------
# Externally Called Functions to register and di-register for multimeter updates
# We only ever expect a single external function to register for these updates
#------------------------------------------------------------------------------

def request_status_report():
    if status_callback is not None and serial_port.is_open:
        if debug: logging.debug("Pi-SPROG: Sending RSTAT command (Request Command Station Status)")
        send_cbus_command(mj_pri=0, min_pri=0, op_code=0x0C)
        # Schedule the next poll in 2000ms (2 seconds)
        common.root_window.after(2000, request_status_report)
    return()

def enable_status_reporting(callback):
    global status_callback
    status_callback = callback
    if serial_port.is_open:
        # NVSET (OpCode 0x96) - Write to Node Variable 10 to enable telemetry
        # Logic: mj_pri=0, min_pri=2, op_code=0x96, Data: NN_high, NN_low, NV_index, NV_value
        logging.debug("Pi-SPROG: Enabling SPROG Telemetry Reporting (NVSET Command)")
        # Early Firmware versions (Node 258)
        send_cbus_command(0, 2, 0x96, 0x01, 0x02, 10, 1)
        # Later Firmware Versions (Global/Alias)
        send_cbus_command(0, 2, 0x96, 0xFF, 0xFE, 10, 1)
        # Kick off the first regular poll after 1000ms
        common.root_window.after(1000, request_status_report)
        return()

def disable_status_reporting():
    global status_callback
    status_callback = None
    if serial_port.is_open:
        logging.debug("Pi-SPROG: Disabling SPROG Telemetry Reporting (NVSET Command)")
        # NVSET (OpCode 0x96) - Write 0 to Node Variable 10 to disable telemetry
        # Early Firmware versions
        send_cbus_command(0, 2, 0x96, 0x01, 0x02, 10, 0)
        # Later Firmware Versions
        send_cbus_command(0, 2, 0x96, 0xFF, 0xFE, 10, 0)
    return()

#------------------------------------------------------------------------------
# Externally Called Function to send an Accessory Short CBUS On/Off Event
#------------------------------------------------------------------------------

def send_accessory_short_event(address:int, active:bool):
    if not isinstance(address, int):
        logging.error("Pi-SPROG: send_accessory_short_event - Address must be specified as an integer")
    elif not isinstance(active, bool):
        logging.error("Pi-SPROG: send_accessory_short_event - State must be specified as a boolean")
    else:
        # Apply any address mode offsets (1 = None, 2 = +4, 3 = -4)
        if address_mode == 2:
            address_to_send = address + 4
            offset_text = " (Address Offset '+4')"
        elif address_mode == 3:
            address_to_send = address - 4
            offset_text = " (Address Offset '-4')"
        else:
            offset_text = ""
            address_to_send = address
        # Validate the modified address - Log the address we have been given - not the one with offsets applied
        if (address_to_send < 1 or address_to_send > 2047):
            logging.error("Pi-SPROG: send_accessory_short_event - Invalid address specified: "+ str(address)+offset_text)
        # Only bother sending commands to the Pi Sprog if the serial port has been opened
        elif serial_port.is_open:
            # Split Node ID and Address into High/Low bytes
            # pi_cbus_node is usually the fixed node ID of the command station
            node_hi = (pi_cbus_node >> 8) & 0xFF
            node_lo = pi_cbus_node & 0xFF
            addr_hi = (address_to_send >> 8) & 0xFF
            addr_lo = address_to_send & 0xFF
            # Send ASON (0x98) or ASOF (0x99)- mj_pri=2, min_pri=3 (standard for accessory events)
            if active:
                logging.debug(f"Pi-SPROG: Sending ASON (Accessory Short ON) to DCC address: {address}{offset_text}")
                send_cbus_command(2, 3, 0x98, node_hi, node_lo, addr_hi, addr_lo)
            else:
                logging.debug(f"Pi-SPROG: Sending ASOF (Accessory Short OFF) to DCC address: {address}{offset_text}")
                send_cbus_command(2, 3, 0x99, node_hi, node_lo, addr_hi, addr_lo)
        elif debug:
            # Note we only log the discard messages in enhanced debugging mode (to reduce the spam in the logs)
            # Note we log the address we have been given - not the one with offsets applied
            state_label = "ASON" if active else "ASOF"
            logging.debug(f"Pi-SPROG: Discarding {state_label} command to DCC address: {address}{offset_text} - SPROG disconnected")
            if active: log_string ="Discarding ASON command to DCC address: "+ str(address)+offset_text
            else: log_string = "Discarding ASOF command to DCC address: "+ str(address)+offset_text
            logging.debug("Pi-SPROG: "+log_string+" - SPROG is disconnected")
        # Play any sound files that are triggered by the DCC command
        play_dcc_sound_file(address, active)
    return ()

#------------------------------------------------------------------------------
# Externally Called Function to read a single CV (used for testing)
# Returns (Value) if successfull or (None) if the request timed out
#------------------------------------------------------------------------------

def service_mode_read_cv(cv:int):
    global service_mode_cv_value
    global service_mode_cv_address
    global service_mode_session_id
    global session_id
    def response_received(): return(service_mode_cv_value is not None)
    service_mode_cv_value = None
    service_mode_cv_address = None
    if not isinstance(cv, int):
        logging.error("Pi-SPROG: service_mode_read_cv - CV to read must be specified as an integer")
    elif (cv < 0 or cv > 1023):
        logging.error(f"Pi-SPROG: service_mode_read_cv - Invalid CV specified: {cv}")
    # Only bother sending commands to the Pi SPROG if the serial port has been opened
    elif serial_port.is_open:
        # Encode the message into the required bytes
        byte1 = session_id             # Session ID
        byte2 = (cv >> 8) & 0xFF       # High CV Byte
        byte3 = cv & 0xFF              # Low CV Byte
        byte4 = 1                      # Mode (1 = Direct Byte)
        logging.debug(f"Pi-SPROG: Sending QCVS (Read CV in Service Mode) - Session:{byte1}, CV:{cv}")
        # Command 0x84 (132 Decimal) - Read CV in Service Mode (QCVS)
        send_cbus_command(2, 2, 0x84, byte1, byte2, byte3, byte4)
        # Wait for the response (5 second timeout as service mode reads involve physical DCC pulses)
        if wait_for_response(5.0, response_received):
            logging.debug(f"Pi-SPROG: Received PCVS (Report CV) - Session:{service_mode_session_id}, CV:{service_mode_cv_address}, Value:{service_mode_cv_value}")
            # Validation checks to ensure the response matches the request
            if service_mode_cv_address != cv:
                logging.error(f"Pi-SPROG: Failed to read CV {cv} - Responded with incorrect CV address: {service_mode_cv_address}")
                service_mode_cv_value = None
            elif service_mode_session_id != session_id:
                logging.error(f"Pi-SPROG: Failed to read CV {cv} - Responded with incorrect Session ID")
                service_mode_cv_value = None
            else:
                logging.info(f"Pi-SPROG: Successfully read CV {service_mode_cv_address} - value: {service_mode_cv_value}")
        else:
            logging.error(f"Pi-SPROG: Failed to read CV {cv} - Timeout awaiting response")
        # Increment the session ID for the next transaction (keeping it within 1-255)
        session_id = session_id + 1
        if session_id > 255: session_id = 1
    else:
        logging.warning(f"Pi-SPROG: Failed to read CV {cv} - SPROG is disconnected")
    return(service_mode_cv_value)

#------------------------------------------------------------------------------
# Externally Called Function to programme a single CV (used for testing)
# Returns True if successful and False if no response is received (timeout)
#------------------------------------------------------------------------------

def service_mode_write_cv(cv:int, value:int):
    global service_mode_response
    global service_mode_session_id
    global session_id
    def response_received(): return(service_mode_response is not None)
    service_mode_response = None
    service_mode_session_id = None
    if not isinstance(cv, int):
        logging.error("Pi-SPROG: service_mode_write_cv - CV to write must be specified as an integer")
    elif not isinstance(value, int):
        logging.error("Pi-SPROG: service_mode_write_cv - Value to write must be specified as an integer")
    elif (cv < 0 or cv > 1023):
        logging.error(f"Pi-SPROG: service_mode_write_cv - Invalid CV specified: {cv}")
    elif (value < 0 or value > 255):
        logging.error(f"Pi-SPROG: service_mode_write_cv - CV {cv} - Invalid value specified: {value}")
    # Only try to send the command if the PI-SPROG-3 is connected
    elif serial_port.is_open:
        # Encode the message into the required bytes
        byte1 = session_id             # Session ID
        byte2 = (cv >> 8) & 0xFF       # High CV Byte
        byte3 = cv & 0xFF              # Low CV Byte
        byte4 = 1                      # Mode (1 = Direct Byte)
        byte5 = value                  # Value to write
        logging.debug(f"Pi-SPROG: Sending WCVS (Write CV in Service Mode) - Session:{byte1}, CV:{cv}, Value:{value}")
        # Command 0xA2 (162 Decimal) - Write CV in Service mode (WCVS)
        send_cbus_command(2, 2, 0xA2, byte1, byte2, byte3, byte4, byte5)
        # Wait for the response (5 second timeout for programming acknowledgment)
        if wait_for_response(5.0, response_received):
            logging.debug(f"Pi-SPROG: Received SSTAT (Service Mode Status) - Session:{service_mode_session_id}, Status:{service_mode_response}")
            # Validation checks
            if service_mode_session_id != session_id:
                logging.error(f"Pi-SPROG: Failed to write CV {cv} - Responded with incorrect Session ID")
                service_mode_response = None
            elif service_mode_response != 3:
                # Status 3 is 'Write Acknowledge' (Success)
                logging.error(f"Pi-SPROG: Failed to write CV {cv} - Error Code: {service_mode_response}")
                service_mode_response = None
            else:
                logging.info(f"Pi-SPROG: Successfully programmed CV {cv} with value: {value}")
        else:
            logging.error(f"Pi-SPROG: Failed to write CV {cv} - Timeout awaiting response")
        # Increment the session ID (keeping it within 1-255)
        session_id = session_id + 1
        if session_id > 255: session_id = 1
    else:
        logging.warning(f"Pi-SPROG: Failed to write CV {cv} - SPROG is disconnected")
    return(service_mode_response == 3)

#########################################################################################
# Functions for Basic Locomotive control - mj_pri=2, min_pri=2 (Standard for Loco setup).
# In the land of DCC, Locomotive addresses fall into two type: Short Addresses: 1 to 127
# and Long Addresses: 0 to 10239 (sent as two bytes). Understanding is that the Pi-Sprog
# interprets 1–127 as short addrersses and 128-10239 as Long addressed.
#
# Summary of CBUS commands used:
#     Request Locomotive Session (RLOC) - Opcode 0x40
#     Session Keep Alive (DKEEP) - Opcode 0x23
#     Release Locomotove (KLOC) - Opcode 0x21
#     Set Loco Speed and Direction (DSPD) - Opcode 0x47
#     set_loco_function  (DFNON/DFNOF) - Opcodes 0x49/0x4A
#
#########################################################################################

# locomotive_sessions is a dict, comprising an entry for each session
# {"loco_address": session_id:int, heartbeat:tkinter_reference}
locomotive_sessions={}

#------------------------------------------------------------------------------
# Internal Helper function to find the dcc address for a session (0 if not found)
#------------------------------------------------------------------------------

def find_dcc_address_for_session(session_id:int):
    dcc_address = 0
    for str_dcc_address, locomotive_session in locomotive_sessions.items():
        if locomotive_session["sessionid"] == session_id:
            dcc_address = int(str_dcc_address)
            break
    return(dcc_address)

#------------------------------------------------------------------------------
# API function to request a loco session (returns session ID or 0 if unsuccessful)
# CBUS Command is Request Locomotive Session (RLOC) - Opcode 0x40
#------------------------------------------------------------------------------

def request_loco_session(dcc_address:int):
    def response_received():
        return(locomotive_sessions[str(dcc_address)]["sessionid"] > 0)
    if not isinstance(dcc_address, int) or dcc_address < 1 or dcc_address > 10239:
        logging.error(f"Pi-SPROG: request_loco_session - Invalid DCC Address {dcc_address} - must be an int (1-10239)")
    else:
        logging.debug(f"Pi-SPROG: Requesting Loco Session for DCC address {dcc_address}")
        # Check if the DCC address is already in use - if so there is an active session so we error
        if not str(dcc_address) in locomotive_sessions.keys():
            locomotive_sessions[str(dcc_address)] = {}
            locomotive_sessions[str(dcc_address)]["sessionid"] = 0
            locomotive_sessions[str(dcc_address)]["heartbeat"] = None
            # Range of Addresses that can be used is 1 to 10239
            if dcc_address < 128:
                # Standard Short Address - Use 0x01 to set the 'Steal' bit on high byte
                addr_hi = 0x01
                addr_lo = dcc_address
            else:
                # Extended Addresses - Use raw hex and set the steal bit
                addr_hi = (dcc_address >> 8) | 0xC1
                addr_lo = dcc_address & 0xFF
            # Request the session and wait for a response
            send_cbus_command(2, 2, 0x40, addr_hi, addr_lo)
            if wait_for_response(2.0, response_received):
                # The Pi-SPROG 3 has a hardware timeout (often set to 20 seconds). If it does not receive a
                # command (speed change, function toggle, or KLOC) for a specific session within that window,
                # it will "purge" the session, stopping the locomotive and releasing the session ID.
                heartbeat = common.root_window.after(5000, lambda:send_loco_keep_alive(locomotive_sessions[str(dcc_address)]["sessionid"]))
                locomotive_sessions[str(dcc_address)]["heartbeat"] = heartbeat
                session_id_to_return = locomotive_sessions[str(dcc_address)]["sessionid"]
            else:
                # Return Session ID of zero (could not create session)
                logging.error(f"Pi-SPROG: request_loco_session - Timeout awaiting response for DCC address {dcc_address}")
                del(locomotive_sessions[str(dcc_address)])
                session_id_to_return = 0
        else:
            # Return Session ID of zero (could not create session)
            logging.error(f"Pi-SPROG: request_loco_session - DCC Address {dcc_address} is already allocated to a loco session")
            session_id_to_return = 0
    return(session_id_to_return)

#------------------------------------------------------------------------------
# Internal heartbeat function to keep a loco session alive until released
# CBUS command is Session Keep Alive (DKEEP) - Opcode 0x23
#------------------------------------------------------------------------------

def send_loco_keep_alive(session_id:int):
    # Find the DCC address associated with this session
    # If DCC address > 0 The session is still in our dict of active sessions
    dcc_address = find_dcc_address_for_session(session_id)
    if dcc_address > 0:
        send_cbus_command(2, 2, 0x23, session_id)
        new_heartbeat = common.root_window.after(5000, lambda:send_loco_keep_alive(session_id))
        locomotive_sessions[str(dcc_address)]["heartbeat"] = new_heartbeat
    return()

#------------------------------------------------------------------------------
# API function to release a loco session
# CBUS command is Release Locomotove (KLOC) - Opcode 0x21
#------------------------------------------------------------------------------

def release_loco_session(session_id:int):
    if not isinstance(session_id, int):
        logging.error(f"Pi-SPROG: release_loco_session - Invalid Session ID {session_id} - must be an int")
    else:
        logging.debug(f"Pi-SPROG: Releasing Loco Session {session_id}")
        # Check that the session is still active (in our list of active sessions)
        dcc_address = find_dcc_address_for_session(session_id)
        if dcc_address > 0:
            # Kill the heartbeat thread and send the release locomotive command
            heartbeat = locomotive_sessions[str(dcc_address)]["heartbeat"]
            common.root_window.after_cancel(heartbeat)
            locomotive_sessions[str(dcc_address)]["heartbeat"] = None
            locomotive_sessions[str(dcc_address)]["sessionid"] = None
            send_cbus_command(2, 2, 0x21, session_id)
            # Delete the Session entry from the list of active sessions
            del(locomotive_sessions[str(dcc_address)])
        else:
            logging.error(f"Pi-SPROG: release_loco_session - Session ID {session_id} not found")
    return()

#------------------------------------------------------------------------------
# Internal function to process the PLOC message (response to RLOC) and
# save the session ID so it can be returned to the calling programme
#------------------------------------------------------------------------------

def process_ploc_message(byte_string):
    logging.debug("Pi-SPROG: Rx thread - Received PLOC (Engine Report) message")
    # Process the message (with exception handling just in case)
    try:
        # Convert to String and remove the start/end markers
        msg_str = byte_string.decode('Ascii').strip(':;')
        # GridConnect Example: :SB000NE10100038F000000;
        # Find 'N', then skip 'N' (1 char) and the OpCode 'E1' (2 chars) = +3
        d_start = msg_str.find('N') + 3
        # Session Handle (1 byte)
        session_handle = int(msg_str[d_start : d_start+2], 16)
        # Loco Address (2 bytes: High + Low)
        addr_high = int(msg_str[d_start+2 : d_start+4], 16)
        addr_low  = int(msg_str[d_start+4 : d_start+6], 16)
        # If addr_high has the top two bits set (0xC0), it's a masked long address
        if addr_high >= 0xC0:
            # Strip the 0xC0 (1100 0000) mask to get the real high bits
            dcc_address = ((addr_high & 0x3F) << 8) | addr_low
            address_type = "Long"
        else:
            # For short addresses, addr_high is just flags/padding
            dcc_address = addr_low
            address_type = "Short"
            # The following parameters are only used for debug logging
        # Speed and Direction (1 byte) - Bit 7 is direction (1 = Forward, 0 = Reverse), Bits 0-6 are speed
        speed_and_direction = int(msg_str[d_start+6 : d_start+8], 16)
        direction = "Forward" if speed_and_direction & 0x80 else "Reverse"
        speed = speed_and_direction & 0x7F
        # Function Maps - Bytes following speed usually represent F0-F4, F5-F8, etc.
        function_group1 = int(msg_str[d_start+8 : d_start+10], 16)
        # Extended debug logging
        if debug:
            logging.debug(f"    Session:{session_handle}, Address:{dcc_address} ({address_type})")
            logging.debug(f"    Speed:{speed}, Direction:{direction}, Function-Map1:0x{function_group1:02X}")
        # Store the session address
        if str(dcc_address) in locomotive_sessions.keys():
            locomotive_sessions[str(dcc_address)]["sessionid"] = session_handle
    except Exception as exception:
        logging.error("Pi-SPROG: Error parsing Engine Report (PLOC) Message")
        logging.error(exception)
    return()

#------------------------------------------------------------------------------
# API function to set Loco Speed and direction
# CBUS Command is Set Loco Speed and Direction (DSPD) - Opcode 0x47
#------------------------------------------------------------------------------

def set_loco_speed_and_direction(session_id:int, speed:int, forward:bool, allow_emergency_stop:bool=False):
    if not isinstance(session_id, int):
        logging.error(f"Pi-SPROG: set_loco_speed_and_direction - Invalid Session ID {session_id} - must be an int")
    elif not isinstance(speed, int) or speed < 0 or speed > 127:
        logging.error(f"Pi-SPROG: set_loco_speed_and_direction - Invalid speed for session {session_id} - must be an int (0-127)")
    # Inhibit the Emergency Stop (unless overridden in the function call)
    if not allow_emergency_stop and speed == 1: speed = 0
    # Direction bit: 1 for Forward, 0 for Reverse
    # Speed is in the range 0-127 where 0 is normal Stop and 1 is Emergency Stop
    dcc_address = find_dcc_address_for_session(session_id)
    if dcc_address > 0:
        dir_val = 128 if forward else 0
        # DCC Speed 1 is usually Emergency Stop, so we map 0-127
        speed_byte = (speed & 0x7F) | dir_val
        logging.debug(f"Pi-SPROG: Locomotive Session {session_id} Speed {speed} Forward {forward}")
        send_cbus_command(2, 2, 0x47, session_id, speed_byte)
    else:
        logging.error(f"Pi-SPROG: set_loco_speed_and_direction - Session {session_id} not found")
    return()

#------------------------------------------------------------------------------
# API function for the Locomotive Emergency Stop
#------------------------------------------------------------------------------

def send_emergency_stop(session_id:int):
    set_loco_speed_and_direction(session_id, speed=1, forward=True, allow_emergency_stop=True)
    return()

#------------------------------------------------------------------------------
# API function to set The Locomotive Functions On/Off
# OpCodes are either 0x49 for ON (DFNON), 0x4A for OFF (DFNOF)
#------------------------------------------------------------------------------

def set_loco_function(session_id:int, function_id:int, state:bool):
    if not isinstance(session_id, int):
        logging.error(f"Pi-SPROG: set_loco_function - Invalid Session ID {session_id} - must be an int")
    elif not isinstance(function_id, int) or function_id < 0 or function_id > 28:
        logging.error(f"Pi-SPROG: set_loco_function - Invalid function ID {function_id} for session {session_id} - must be 0-28")
    # Check if the session is valid before sending
    dcc_address = find_dcc_address_for_session(session_id)
    if dcc_address > 0:
        # Select OpCode based on state
        if state: opcode = 0x49
        else: opcode = 0x4A
        logging.debug(f"Pi-SPROG: Locomotive Session {session_id} (Addr {dcc_address}) Function F{function_id} set to {'ON' if state else 'OFF'}")
        # CBUS command format for DFNON/DFNOF: [OpCode] [Session] [Function_Number]
        # Data length is 2 bytes (Session and Function ID)
        send_cbus_command(2, 2, opcode, session_id, function_id)
    else:
        logging.error(f"Pi-SPROG: set_loco_function - Session {session_id} not found")
    return()

#------------------------------------------------------------------------------
# API function for Emergency Stop All
# CBUS Command for Emergency Stop (RESP) - Opcode 0x06
#------------------------------------------------------------------------------

def send_emergency_stop_all():
    send_cbus_command(0, 0, 0x06)
    return()

#------------------------------------------------------------------------------
# Function to encode a standard 3-byte DCC Accessory Decoder Packet into 3 bytes
# for transmission to the PI-SPROG as a RDCC3 Command (Request 3-byte DCC Packet).
# Calls the 'send_cbus_command' function to actually encode and send the command
# The DCC Packet is sent <repeat> times - but not refreshed on a regular basis
# Acknowledgement to Java NMRA implementation (which this function follows closely)
# 
# Packets are represented by an array of bytes. Preamble/postamble not included.
# Note that this is a data representation, NOT a representation of the waveform!
# From the NMRA RP: 0 10AAAAAA 0 1AAACDDD 0 EEEEEEEE 1, Where
#    A = Address bits
#    D = the output channel to set
#    C = the State (1 = ON, 0 = OFF) 
#    E = the error detection bits
#
# Accessory Digital Decoders can control momentary or constant-on devices, the duration
# of time that each output is active being pre-configured by CVs #515 through #518.
# Bit 3 of the second byte "C" is used to activate or deactivate the addressed device.
# (Note if the duration the device is intended to be on is less than or equal the
# pre-configured duration, no deactivation is necessary)
#
# Since most devices are paired, the convention is that bit "0" of the second byte
# is used to distinguish between which of a pair of outputs the accessory decoder is
# activating or deactivating.
#
# Bits 1 and 2 of the second byte is used to indicate which of 4 pairs of outputs the
# accessory decoder is activating or deactivating
#
# The significant bits of the 9 bit address are bits 4-6 of the second data byte.
# By convention these three bits are in ones complement. The use of bit 7 of the second
# byte is reserved for future use.
#
# NOTE - This function is currently untested as I have been unable to confirm
# (either via research or Test) whether the Pi-SPROG-3 supports the RDDC3 Command 
#------------------------------------------------------------------------------
# 
# def send_DCC_accessory_decoder_packet (address:int, active:bool, output_channel:int = 0, repeat:int = 3):
#     global track_power_on
#     if (address < 1 or address > 511):
#         logging.info("Error: send_accessory_decoder_packet - Invalid address "+str(address))
#     elif (output_channel < 0 or output_channel > 7):
#         logging.info("Error: send_accessory_decoder_packet - Invalid output channel " +
#                       str(output_channel)+" for address "+str(address))    
#     elif (repeat < 0 or repeat > 255):
#         logging.info("Error: send_accessory_decoder_packet - Invalid Repeat Value " +
#                       str(repeat)+" for address "+str(address))
#     # Only try to send the command if the PI-SPROG-3 has initialised correctly
#     elif track_power_on:
#         low_addr = address & 0x3F
#         high_addr = (( ~ address) >> 6) & 0x07
#         byte1 = (0x80 | low_addr)
#         byte2 = (0x80 | (high_addr << 4) | (active << 3) | output_channel & 0x07)
#         byte3 = (byte1 ^ byte2)
#         #  Send a RDCC3 Command (Request 3-Byte DCC Packet) via the CBUS
#         logging.debug ("PI >> SPROG - RDCC3 (Send 3 Byte DCC Packet) : Address:"
#                         + str(address) + "  Channel:" + str(output_channel) +"  State:" + str(active))
#         send_cbus_command (2, 2, 128, repeat, byte1, byte2, byte3)
#     return ()
#
#------------------------------------------------------------------------------
# Function to encode a standard Extended DCC Accessory Decoder Packet into 4 bytes
# for transmission to the PI-SPROG as a RDCC4 Command (Request 4-byte DCC Packet).
# Calls the 'send_cbus_command' function to actually encode and send the command
# The DCC Packet is sent <repeat> times - but not refreshed on a regular basis
# Acknowledgement to Java NMRA implementation (which this function follows closely)
#
# Packets are represented by an array of bytes. Preamble/postamble not included.
# From the NMRA RP:  10AAAAAA 0 0AAA0AA1 0 000XXXXX 0 EEEEEEEE 1}
#    A = Address bits
#    X = The Aspect to display
#    E = the error detection bits
#
# The addressing is not clear in te NRMA standard - Two interpretations are provided
# in the code (albeit one commented out) - thanks again to the Java NMRA implementation
#
# NOTE - This function is currently untested as I have been unable to confirm
# (either via research or Test) whether the Pi-SPROG-3 supports the RDDC4 Command 
#------------------------------------------------------------------------------
# 
# def send_extended_DCC_accessory_decoder_packet (address:int, aspect:int, repeat:int = 3, alt_address = False):
#     global track_power_on
#     if (address < 1 or address > 2044):
#         logging.info("Error: send_extended_DCC_accessory_decoder_packet - Invalid address "+str(address))
#     elif (aspect < 0 or aspect > 31):
#         logging.info("Error: send_extended_DCC_accessory_decoder_packet - Invalid aspect "+str(aspect))
#     elif track_power_on:
#         # DCC Address interpretation 1 and 2
#         address -= 1
#         low_addr = (address & 0x03)
#         board_addr = (address >> 2)
#         if alt_address: board_addr = board_addr+1
#         mid_addr = board_addr & 0x3F
#         high_addr = ((~board_addr) >> 6) & 0x07
#         byte1 = (0x80 | mid_addr)
#         byte2 = (0x01 | (high_addr << 4) | (low_addr << 1))
#         byte3 = (0x1F & aspect)
#         byte4 = (byte1 ^ byte2 ^ byte3)
#         #  Send a RDCC4 Command (Request 4-Byte DCC Packet) via the CBUS
#         logging.debug ("PI >> SPROG - RDCC4 (Send 4 Byte DCC Packet) : Address:"
#                         + str(address) + "  Aspect:" + str(aspect))
#         send_cbus_command (2, 2, 160, repeat, byte1, byte2, byte3, byte4)
#     return()
#
#------------------------------------------------------------------------------
# Function to send a QNN (Query Node Number) command (response will be logged)
# Returns True if successful and False if no response is received (timeout)
#------------------------------------------------------------------------------
# 
# def query_node_number():
#     global qnn_response
#     def response_received(): return(qnn_response)
#     qnn_response = False
#     # Only bother sending commands to the Pi Sprog if the serial port has been opened
#     if serial_port.is_open:
#         # Retry sending the command (3 attempts) if we don't get a response
#         attempts = 0
#         while attempts < 3:
#             logging.debug ("Pi-SPROG: Sending QNN command (Query Node Number)")
#             send_cbus_command (mj_pri=2, min_pri=3, op_code=13)
#             # Wait for the response (with a 1 second timeout)
#             if wait_for_response(1.0, response_received): break
#             attempts = attempts + 1
#             logging.warning("Pi-SPROG: Query Node Number timeout - retrying")
#         if qnn_response: logging.debug ("Pi-SPROG: Received PNN (Response to Query Node)")
#         else: logging.error("Pi-SPROG: Query Node Number failed")
#     else:
#         logging.warning("Pi-SPROG: Cannot Query Node Number - port is closed")
#     return(qnn_response)
#
#------------------------------------------------------------------------------
# Internal function to process a Query Node response (PNN message)
# Sets the qnn_response flag - to signal back into the main thread
# Response to Query Node op code is (0xB6 = 182 decimal) so the following
# line would need to be added into the receive data thread:
#   elif op_code == 182: process_pnn_message(byte_string)
#------------------------------------------------------------------------------
# 
# def process_pnn_message(byte_string):
#     global qnn_response
#     # Print out the status report (if the appropriate debug level is set)
#     if debug:
#         logging.debug ("Pi-SPROG: Rx thread - Received PNN (Response to Query Node):")
#         logging.debug ("    Node Id   :"+str(int(chr(byte_string[9]) + chr(byte_string[10])
#                                               + chr(byte_string[11]) + chr(byte_string[12]),16)))
#         logging.debug ("    Mfctre ID :"+str(int(chr(byte_string[13]) + chr(byte_string[14]),16)))
#         logging.debug ("    Module ID :"+str(int(chr(byte_string[15]) + chr(byte_string[16]),16)))
#         # Get the Flags - we only need the last hex character (to get the 4 bits)
#         flags = int(chr(byte_string[18]),16)
#         logging.debug ("    Bldr Comp :"+str((flags & 0x08)==0x08))
#         logging.debug ("    FLiM Mode :"+str((flags & 0x04)==0x04))
#         logging.debug ("    Prod Node :"+str((flags & 0x02)==0x02))
#         logging.debug ("    Cons Node :"+str((flags & 0x01)==0x01)+"\r")
#     # Respond to the trigger function (waiting in the main thread for a response)
#     qnn_response = True
#     return()
#
###################################################################################
# Functions to Play sound files, triggered by DCC commands. These should really be
# located in a seperate library module, but I've put them here for the time being
# as the playing of the audio files is triggered from DCC commands, and the
# 'send_accessory_short_event' function in this module already gets called for
# every DCC command generated by the application or received via the MQTT broker.
# Note that, unlike block instruments audio, I've taken the conscious descision
# to only load in the audio files when playback is triggered. From the limited
# testing I've done, this doesn't seem to have any real impact on performance.
###################################################################################

# The global flag to indicate if audio is enabled or not
try:
    import simpleaudio
    audio_enabled = True
except Exception:
    audio_enabled = False

# The global dictionary to hold the sound file mappings. The key is the DCC
# address. Each entry comprises a list of [state:bool, sound_file:str]
dcc_sound_mappings = {}

# API function to add a new DCC sound file mapping
def add_dcc_sound_mapping(address:int, state:bool, fully_qualified_sound_filename:str):
    global dcc_sound_mappings
    dcc_sound_mappings[address] = [state, fully_qualified_sound_filename]
    return()

# API function to delete all DCC sound file mappings
def reset_dcc_sound_mappings():
    global dcc_sound_mappings
    dcc_sound_mappings = {}
    return()

# Internal function to play a sound file if a mapping exists for the DCC command
def play_dcc_sound_file(address:int, active:bool):
    if audio_enabled:
        if address in dcc_sound_mappings.keys() and active == dcc_sound_mappings[address][0]:
            dcc_sound_file_to_load_and_play = dcc_sound_mappings[address][1]
            logging.debug("Pi-SPROG: Triggering sound file: "+dcc_sound_file_to_load_and_play)
            try:
                audio_object = simpleaudio.WaveObject.from_wave_file(dcc_sound_file_to_load_and_play)
                audio_object.play()
            except Exception as exception:
                logging.error("Pi-SPROG: Error playing sound file: "+dcc_sound_file_to_load_and_play)
                logging.error("Pi-SPROG: Reported exception: "+str(exception))
    return()

######################################################################################


