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

# Global class for the Serial Port (port is configured/opened later)
serial_port = serial.Serial()

# Global constants used when transmitting CBUS messages
can_bus_id = 1                       # The arbitary CANBUS ID we will use for the Pi
pi_cbus_node = 1                     # The arbitary CBUS Node ID we will use for the Pi
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

#------------------------------------------------------------------------------
# Common function used by the main thread to wait for responses in other threads.
# When the specified function returns True, the function exits and returns True.
#------------------------------------------------------------------------------

def wait_for_response(timeout:float,test_for_response_function):
    response_received = False
    timeout_start = time.time()
    while time.time() < timeout_start + timeout:
        response_received = test_for_response_function()
        if response_received: break
        time.sleep(0.001)
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
    while not port_close_initiated:
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
                    # Extract the OpCode and Process the message (only a subset of messages is supported)
                    op_code = int((chr(byte_string[7]) + chr(byte_string[8])),16)
                    # Command Station Status Report (0xE3 = 227 decimal)
                    if op_code == 227: process_stat_message(byte_string)
                    # Response to confirm Track Power is OFF (0x04 = 4 decimal)
                    elif op_code == 4: process_tof_message(byte_string)
                    # Response to confirm Track Power is ON (0x05 = 5 decimal)
                    elif op_code == 5: process_ton_message(byte_string)
                    # Report CV value in service programming mode (0x85 = 133 decimal)
                    elif op_code == 133: process_pcvs_message(byte_string)
                    # Report Service Mode Status response (0x4C = 76 decimal) 
                    elif op_code == 76: process_sstat_message(byte_string)
                except:
                    logging.warning("Pi-SPROG: Rx thread - Couldn't decode CBUS Message: "+byte_string.decode('Ascii')+"\r")
        # Ensure the thread doesn't hog all the CPU time
        time.sleep(0.001)
    if debug: logging.debug("Pi-SPROG: Rx Thread - exiting")
    rx_thread_terminated = True
    return()

#------------------------------------------------------------------------------
# Internal function to process a Command Station Status Report (STAT message)
# Sets the rstat_response flag - to signal back into the main thread
#------------------------------------------------------------------------------

def process_stat_message(byte_string):
    global rstat_response
    # Print out the status report (if the appropriate debug level is set)
    if debug:
        logging.debug ("Pi-SPROG: Rx thread - Received STAT (Command Station Status Report):")
        logging.debug ("    Node Id       :"+str(int(chr(byte_string[9]) + chr(byte_string[10])
                                                  + chr(byte_string[11]) + chr(byte_string[12]),16)))
        logging.debug ("    CS Number     :"+str(int(chr(byte_string[13]) + chr(byte_string[14]),16)))
        logging.debug ("    Version       :"+str(int(chr(byte_string[17]) + chr(byte_string[18]),16))+"."
                                           +str(int(chr(byte_string[19]) + chr(byte_string[20]),16))+"."
                                           +str(int(chr(byte_string[21]) + chr(byte_string[22]),16)))
        # Get the Flags - we only need the last hex character (to get the 4 bits)
        flags = int(chr(byte_string[16]),16)
        logging.debug ("    Reserved      :"+str((flags & 0x080)==0x80))
        logging.debug ("    Service Mode  :"+str((flags & 0x040)==0x40))
        logging.debug ("    Reset Done    :"+str((flags & 0x02)==0x20))
        logging.debug ("    Emg Stop Perf :"+str((flags & 0x10)==0x10))
        logging.debug ("    Bus On        :"+str((flags & 0x08)==0x08))
        logging.debug ("    Track On      :"+str((flags & 0x04)==0x04))
        logging.debug ("    Track Error   :"+str((flags & 0x02)==0x02))
        logging.debug ("    H/W Error     :"+str((flags & 0x01)==0x01)+"\r")
    # Respond to the trigger function (waiting in the main thread for a response)
    rstat_response = True
    return()

#------------------------------------------------------------------------------
# Internal function to process a Track power responses (TOF/TON messages)
# Sets the appropriate acknowledge flag - to signal back into the main thread
#------------------------------------------------------------------------------

def process_tof_message(byte_string):
    global tof_response
    if debug: logging.debug ("Pi-SPROG: Rx thread - Received TOF (Track OFF) acknowledgement")
    # Respond to the trigger function (waiting in the main thread for a response)
    tof_response = True
    return()
                        
def process_ton_message(byte_string):
    global ton_response
    if debug: logging.debug ("Pi-SPROG: Rx thread - Received TON (Track ON) acknowledgement")
    # Respond to the trigger function (waiting in the main thread for a response)
    ton_response = True
    return()

#------------------------------------------------------------------------------
# Internal function to process a Report CV response (PCVS message)
# Sets the service_mode_cv_value - to signal back into the main thread
#------------------------------------------------------------------------------

def process_pcvs_message(byte_string):
    global service_mode_cv_value
    global service_mode_cv_address
    global service_mode_session_id
    # Response contains [header]<85><Session><High CV#><Low CV#><Val>
    session_id = int(chr(byte_string[9]) + chr(byte_string[10]),16)
    cv = ( int(chr(byte_string[11]) + chr(byte_string[12]),16) +
           int(chr(byte_string[13]) + chr(byte_string[14]),16) )
    value = int(chr(byte_string[15]) + chr(byte_string[16]),16)
    if debug: logging.debug ("Pi-SPROG: Rx thread - Received PCVS (Report CV) - Session:"+
                   str(session_id)+", CV:"+str(cv)+", Value:"+str(value))
    # Respond to the trigger function (waiting in the main thread for a response)
    service_mode_session_id = session_id
    service_mode_cv_address = cv
    service_mode_cv_value = value
    return()

#------------------------------------------------------------------------------
# Internal function to process a service mode status response (SSTAT message)
# Sets the service_mode_response - to signal back into the main thread
#------------------------------------------------------------------------------

def process_sstat_message(byte_string):
    global service_mode_response
    global service_mode_session_id
    session_id = int(chr(byte_string[9]) + chr(byte_string[10]),16)
    service_mode_status = int(chr(byte_string[11]) + chr(byte_string[12]),16)
    if service_mode_status == 0: status = "Reserved"
    elif service_mode_status == 1: status = "No Acknowledge"
    elif service_mode_status == 2: status = "Overload on Programming Track"
    elif service_mode_status == 3: status = "Write Acknowledge"
    elif service_mode_status == 4: status = "Busy"
    elif service_mode_status == 5: status = "CV Out of Range"
    else: status = "Unrecognised response code" + str (service_mode_status)
    if debug: logging.debug ("Pi-SPROG: Rx thread - Received SSTAT (Service Mode Status) - Session:"
                           + str(session_id)+", Status:" + status)
    # Respond to the trigger function (waiting in the main thread for a response)
    service_mode_session_id = session_id
    service_mode_response = service_mode_status
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
        # Encode the CAN Header        
        header_byte1 = (mj_pri << 6) | (min_pri <<4) | (can_bus_id >> 3)
        header_byte2 = (0x1F & can_bus_id) << 5
        # Start building the GridConnect Protocol string for the CBUS command
        command_string = (":S" + format(header_byte1,"02X") + format(header_byte2,"02X")
                          + "N" + format (op_code,"02X"))
        # Add the Data Bytes associated with the OpCode (if there are any)
        for data_byte in data_bytes: command_string = command_string + format(data_byte,"02X")
        # Finally - add the command string termination character
        command_string = command_string + ";"
        # Add the command to the output buffer (to be picked up by the Tx thread)
        output_buffer.put(command_string)
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
                   dcc_debug_mode:bool = False):
    global debug
    pi_sprog_connected = False
    if not isinstance(port_name, str):
        logging.error("Pi-SPROG: sprog_connect - Port name must be specified as a string")
    elif not isinstance(baud_rate, int):
        logging.error("Pi-SPROG: sprog_connect - Baud rate must be specified as an integer")
    elif not isinstance(dcc_debug_mode, bool):
        logging.error("Pi-SPROG: sprog_connect - Enhanced debug flag must be specified as a boolean")
    else:
        # If the serial port is already open then close it before re-configuring
        if serial_port.is_open: sprog_disconnect()
        # Assign the global "enhanced debugging" flag
        debug = dcc_debug_mode
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
        if debug: logging.debug("Pi-SPROG: Shutting down Tx and Rx Threads")
        port_close_initiated = True
        # Wait until we get confirmation the Threads have been terminated
        wait_for_response(0.5, response_received)
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
        # Retry sending the command (3 attempts) if we don't get a response
        attempts = 0
        while attempts < 3:
            # Query the status of the command station to confirm connectivity (0x0C = 12 decimal)
            logging.debug("Pi-SPROG: Sending RSTAT command (Request Command Station Status)")
            send_cbus_command(mj_pri=2, min_pri=2, op_code=12)
            # Wait for the response (with a 1 second timeout)
            if wait_for_response(1.0, response_received): break
            attempts = attempts + 1
            logging.warning("Pi-SPROG: Request Command Station Status timeout - retrying")
        if rstat_response: logging.debug ("Pi-SPROG: Received STAT (Command Station Status Report)")
        else: logging.error("Pi-SPROG: Request Command Station Status failed")
    else:
        logging.warning("Pi-SPROG: Cannot Request Command Station Status - SPROG is disconnected")
    return(rstat_response)

#------------------------------------------------------------------------------
# Externally Called Function to turn on the track power
#------------------------------------------------------------------------------

def request_dcc_power_on():
    global ton_response
    def response_received(): return(ton_response)
    ton_response = False
    # Only bother sending commands to the Pi Sprog if the serial port has been opened
    if serial_port.is_open:
        # Retry sending the command (3 attempts) if we don't get a response
        attempts = 0
        while attempts < 3:
            # Send the command to switch on the Track Supply (to the DCC Bus)
            logging.debug ("Pi-SPROG: Sending RTON command (Request Track Power On)")
            send_cbus_command (mj_pri=2, min_pri=2, op_code=9)
            # Wait for the response (with a 1 second timeout)
            if wait_for_response(1.0, response_received): break
            attempts = attempts + 1
            logging.warning("Pi-SPROG: Request Track Power On timeout - retrying")
        if ton_response:
            logging.debug("Pi-SPROG: Received TON (Track ON) acknowledgement")
            logging.info("Pi-SPROG: Track power has been turned ON")
        else: logging.error("Pi-SPROG: Request to turn on Track Power failed")
        # Give things time to get established before sending out any commands
        time.sleep (0.1)
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
        # Retry sending the command (3 attempts) if we don't get a response
        attempts = 0
        while attempts < 3:
            # Send the command to switch on the Track Supply (to the DCC Bus)
            logging.debug("Pi-SPROG: Sending RTOF command (Request Track Power Off)")
            send_cbus_command(mj_pri=2, min_pri=2, op_code=8)
            # Wait for the response (with a 1 second timeout)
            if wait_for_response(1.0, response_received): break
            attempts = attempts + 1
            logging.warning("Pi-SPROG: Request Track Power Off timeout - retrying")
        if tof_response:
            logging.debug("Pi-SPROG: Received TOF (Track OFF) acknowledgement")
            logging.info("Pi-SPROG: Track power has been turned OFF")
        else: logging.error("Pi-SPROG: Request to turn off Track Power failed")
    return(tof_response)

#------------------------------------------------------------------------------
# Externally Called Function to send an Accessory Short CBUS On/Off Event
#------------------------------------------------------------------------------

def send_accessory_short_event(address:int, active:bool):
    if not isinstance(address, int):
        logging.error("Pi-SPROG: send_accessory_short_event - Address must be specified as an integer")
    elif not isinstance(active, bool):
        logging.error("Pi-SPROG: send_accessory_short_event - State must be specified as a boolean")
    elif (address < 1 or address > 2047):
        logging.error("Pi-SPROG: send_accessory_short_event - Invalid address specified: "+ str(address))
    # Only bother sending commands to the Pi Sprog if the serial port has been opened
    elif serial_port.is_open:
        # Encode the message into the required number of bytes
        byte1 = (pi_cbus_node & 0xff00) >> 8
        byte2 = (pi_cbus_node & 0x00ff)
        byte3 = (address & 0xff00) >> 8
        byte4 = (address & 0x00ff)
        #  Send a ASON or ASOF Command (Accessoy Short On or Accessory Short Off)
        if active:
            logging.debug("Pi-SPROG: Sending DCC command ASON (Accessory Short ON) to DCC address: "+ str(address))
            send_cbus_command(2, 3, 152, byte1, byte2, byte3, byte4)
        else:
            logging.debug("Pi-SPROG: Sending DCC command ASOF (Accessory Short OFF) to DCC address: "+ str(address))
            send_cbus_command(2, 3, 153, byte1, byte2, byte3, byte4)
    elif debug:
        # Note we only log the discard messages in enhanced debugging mode (to reduce the spam in the logs)
        if active: log_string ="Discarding ASON command to DCC address: "+ str(address)
        else: log_string = "Discarding ASOF command to DCC address: "+ str(address)
        logging.debug("Pi-SPROG: "+log_string+" - SPROG is disconnected or DCC power is OFF")
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
        logging.error("Pi-SPROG: service_mode_read_cv - Invalid CV specified: "+str(cv))
    # Only bother sending commands to the Pi Sprog if the serial port has been opened
    elif serial_port.is_open:
        # Encode the message into the required number of bytes
        byte1 = session_id             # Session ID
        byte2 = (cv & 0xff00) >> 8     # High CV
        byte3 = (cv & 0x00ff)          # Low CV
        byte4 = 1                      # Mode (1 = Direct bit)
        # Sending the QCVS command (without any re-tries)
        logging.debug ("Pi-SPROG: Sending QCVS (Read CV in Service Mode) - Session:"+str(byte1)+", CV:"+str(cv))
        # Command to send is 0x84 (=132 Decimal) - Read CV in Service Mode (QCVS) 
        send_cbus_command(2, 2, 132, byte1, byte2, byte3, byte4)
        # Wait for the response (with a 5 second timeout - this takes a long time)
        if wait_for_response(5.0, response_received):
            logging.debug("Pi-SPROG: Received PCVS (Report CV) - Session:"+ str(service_mode_session_id)+
                           ", CV:"+str(service_mode_cv_address)+", Value:"+str(service_mode_cv_value))
            if service_mode_cv_address != cv:
                logging.error("Pi-SPROG: Failed to read CV "+str(cv)+" - Responded with incorrect CV address")
                service_mode_cv_value = None
            elif service_mode_session_id != session_id:
                logging.error("Pi-SPROG: Failed to read CV "+str(cv)+" - Responded with incorrect Session ID")
                service_mode_cv_value = None
            else:
                logging.info("Pi-SPROG: Successfully read CV"+str(service_mode_cv_address)+
                              " - value:"+str(service_mode_cv_value))
        else:
            logging.error("Pi-SPROG: Failed to read CV "+str(cv)+" - Timeout awaiting response")
        # Increment the 'one up' session Id for the next time
        session_id = session_id + 1
        if session_id > 255: session_id = 1
    else:
        logging.warning("Pi-SPROG: Failed to read CV "+str(cv)+" - SPROG is disconnected or DCC power is off")
    return (service_mode_cv_value)

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
        logging.error("Pi-SPROG: service_mode_write_cv - Invalid CV specified: "+str(cv))
    elif (value < 0 or value > 255):
        logging.error("Pi-SPROG: service_mode_write_cv - CV "+str(cv)+" - Invalid value specified: "+str(value))
    # Only try to send the command if the PI-SPROG-3 has initialised correctly
    elif serial_port.is_open:
        # Encode the message into the required number of bytes
        byte1 = session_id             # Session ID
        byte2 = (cv & 0xff00) >> 8     # High CV
        byte3 = (cv & 0x00ff)          # Low CV
        byte4 = 1                      # Mode (1 = Direct bit)
        byte5 = value                  # value to write
        # Sending the WCVS command (without any re-tries)
        logging.debug("Pi-SPROG: Sending WCVS (Write CV in Service Mode) command - Session:"
                         +str(byte1)+", CV:"+str(cv)+", Value:"+str(value))
        # Command to send is 0xA2 (=162 Decimal) - Write CV in Service mode (WCVS)
        send_cbus_command(2, 2, 162, byte1, byte2, byte3, byte4, byte5)
        # Wait for the response (with a 5 second timeout)
        if wait_for_response(5.0, response_received):
            logging.debug("Pi-SPROG: Received SSTAT (Service Mode Status) - Session:"
                    +str(service_mode_session_id)+", Status:"+str(service_mode_response))
            if service_mode_session_id != session_id:
                logging.error("Pi-SPROG: Failed to write CV "+str(cv)+" - Responded with incorrect Session ID")
                service_mode_response = None
            elif service_mode_response != 3:
                logging.error("Pi-SPROG: Failed to write CV "+str(cv)+" - Error Code: "+str(service_mode_response))
                service_mode_response = None
            else:
                logging.info("Pi-SPROG: Successfully programmed CV"+str(cv)+" with value:"+str(value))
        else:
            logging.error("Pi-SPROG: Failed to write CV "+str(cv)+" - Timeout awaiting response")
        # Increment the 'one up' session Id for the next time
        session_id = session_id + 1
        if session_id > 255: session_id = 1
    else:
        logging.warning("Pi-SPROG: Failed to write CV "+str(cv)+" - SPROG is disconnected or DCC power is off")
    return(service_mode_response == 3)

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
######################################################################################


