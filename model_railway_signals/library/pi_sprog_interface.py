#--------------------------------------------------------------------------------------------------
# This provides a basic CBUS interface fpor communicating with the Pi-SPROG3 via the Raspberry Pi 
# UART. It does not provide a fully-functional interface for all DCC command and control functions,
# just the minimum set needed to support the driving of signals and points via a selection of common
# DCC Accessory decoders. Basic CV Programming is also supported - primarily as an aid to testing. 
# For full decoder programming the recommendation is to use JRMI DecoderPro or similar.
#--------------------------------------------------------------------------------------------------
#
# Public Types and Functions:
# 
# initialise_pi_sprog - Open and configures the serial comms port to the Pi Sprog and issues
#                       a Request Command Station Status command to confirm connectivity
#    Optional Parameters:
#       port_name:str - The serial port to use for the Pi-SPROG 3 - Default="/dev/serial0",
#       baud_rate:int - The baud rate to use for the serial port - Default = 115200,
#       dcc_debug_mode:bool - Set to 'True' to log the CBUS commands being sent to the Pi-SPROG
#         returns True - if communications with the Pi-Sprog have been established (otherwise False) 
# service_mode_write_cv - programmes a CV in direct bit mode and waits for response
#                       (events are only sent if the track power is currently switched on)
#                       (request times out after 5 secs if the request was unsuccessful)
#    Mandatory Parameters:
#       cv:int - The CV (Configuration Variable) to be programmed
#       value:int - The value to programme
#          returns True - if we have acknowledgement that the CV has been programmed
#          returns False - if the CV programming fails or the request times out
# 
# request_dcc_power_on - sends request to switch on the power and waits for acknowledgement
#                  (requests only sent if the Comms Port has been successfully opened/configured)
#          returns True - if we have acknowledgement that Track Power has been turned on
#          returns False - if the request times out
# 
# request_dcc_power_off - sends request to switch off the power and waits for acknowledgement
#                  (requests only sent if the Comms Port has been successfully opened/configured)
#          returns True - if we have  acknowledgement that Track Power has been turned off
#          returns False - if the request times out
# 
# Functions are also included in the Code base for sending direct DCC accessory Packets
# and Extended DCC Accessory Packets. However, I have as yet been unable to get these
# Working with the Signallist SC1 Decoder - so these are unproven
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

# Create a new class of the Serial Port (port is configured/opened later)
serial_port = serial.Serial ()

# Global Variables (constants used by the fuctions in the module)
can_bus_id = 1                # The arbitary CANBUS ID we will use for the Pi
pi_cbus_node = 1              # The arbitary CBUS Node ID we will use for the Pi
transmit_delay = 0.02         # The delay between sending CBUS Messages (in seconds)

# Global Variables (configured/changed by the functions in the module)
debug = False                 # Enhanced Debug logging - set when Pi Sprog is initialised
threads_started = False       # if the Tx and Rx threads have been started then don't start again
track_power_on = None         # if track power is OFF or unknown (None) we wont send DCC Bus commands
rstat_response = None         # Flag to test for a RSTAT response (on initialisation)
qnn_response = None           # Flag to test for a PNN response (on initialisation)
service_mode_status = 0       # The response code from programming a CV

# This is the output buffer for messages to be sent to the SPROG
# We use a buffer so we can throttle the transmit rate without blocking
output_buffer = queue.Queue()

#------------------------------------------------------------------------------
# Internal thread to write queued CBUS messages to the Serial Port with a
# short delay inbetween each message. We do this because some decoders don't
# seem to process messages sent to them in quick succession - and if the
# decoder "misses" an event the signal/point may end up in an erronous state
#------------------------------------------------------------------------------

def thread_to_send_buffered_data ():
    global transmit_delay
    global logging
    global debug
    while True:
        command_string = output_buffer.get()
        #Print the Transmitted message (if the appropriate debug level is set)
        if debug:logging.debug ("Pi-SPROG - Transmit CBUS Message: " + command_string)
        # Write the CBUS Message to the serial port (with exception handling
        # We just handle any exceptions (we'll get exceptions during port re-configuration)
        try: serial_port.write(bytes(command_string,"Ascii"))
        except: pass
        # Sleep before sending the next CBUS message
        time.sleep(transmit_delay)
    return()
    
#------------------------------------------------------------------------------
# Internal thread to read CBUS messages from the Serial Port and make a callback
# We're not receiving anything else on this port so its OK to set up the port 
# without a timeout - as we are only interested in "complete" messages
#------------------------------------------------------------------------------

def thread_to_read_received_data ():
    global track_power_on
    global service_mode_status
    global logging
    global rstat_response
    global qnn_response
    global debug
    while True:
        # Enbsure the thread doesn't hog all the CPU
        time.sleep(0.0001)
        # Read from the port until we get the GridConnect Protocol message termination character
        # We just handle any exceptions (we'll get exceptions during port re-configuration)
        try: byte_string = serial_port.read_until(b";")
        except: pass
        else:
            # Log the Received message (if the appropriate debug level is set
            if debug:logging.debug("Pi-SPROG - Received CBUS Message: " + byte_string.decode('Ascii') + "\r")
            # Extract the OpCode - so we can decide what to do - Note that we put an exception handler around
            # The remainder of this code to handle "edge-case" exceptions (port config being changed)
            try:
                op_code = int((chr(byte_string[7]) + chr(byte_string[8])),16)
                
                # Process selected commands (note that only a subset is supported)
                
                if op_code == 227:  # Command Station Status Report
                                
                    # Print out the status report (if the appropriate debug level is set)
                    logging.info ("Pi-SPROG: Received STAT (Command Station Status Report):")
                    logging.info ("    Node Id       :"+str(int(chr(byte_string[9]) + chr(byte_string[10])
                                                              + chr(byte_string[11]) + chr(byte_string[12]),16)))
                    logging.info ("    CS Number     :"+str(int(chr(byte_string[13]) + chr(byte_string[14]),16)))
                    logging.info ("    Version       :"+str(int(chr(byte_string[17]) + chr(byte_string[18]),16))+"."
                                                       +str(int(chr(byte_string[19]) + chr(byte_string[20]),16))+"."
                                                       +str(int(chr(byte_string[21]) + chr(byte_string[22]),16)))
                    # Get the Flags - we only need the last hex character (to get the 4 bits)
                    flags = int(chr(byte_string[16]),16)
                    logging.info ("    Reserved      :"+str((flags & 0x080)==0x80))
                    logging.info ("    Service Mode  :"+str((flags & 0x040)==0x40))
                    logging.info ("    Reset Done    :"+str((flags & 0x02)==0x20))
                    logging.info ("    Emg Stop Perf :"+str((flags & 0x10)==0x10))
                    logging.info ("    Bus On        :"+str((flags & 0x08)==0x08))
                    logging.info ("    Track On      :"+str((flags & 0x04)==0x04))
                    logging.info ("    Track Error   :"+str((flags & 0x02)==0x02))
                    logging.info ("    H/W Error     :"+str((flags & 0x01)==0x01)+"\r")
                    rstat_response = True
                    
                elif op_code == 182:  # Response to Query Node
                            
                    # Print out the status report (if the appropriate debug level is set)
                    logging.info ("Pi-SPROG: Received PNN (Response to Query Node)")
                    logging.info ("    Node Id   :"+str(int(chr(byte_string[9]) + chr(byte_string[10])
                                                          + chr(byte_string[11]) + chr(byte_string[12]),16)))
                    logging.info ("    Mfctre ID :"+str(int(chr(byte_string[13]) + chr(byte_string[14]),16)))
                    logging.info ("    Module ID :"+str(int(chr(byte_string[15]) + chr(byte_string[16]),16)))
                    # Get the Flags - we only need the last hex character (to get the 4 bits)
                    flags = int(chr(byte_string[18]),16)
                    logging.info ("    Bldr Comp :"+str((flags & 0x08)==0x08))
                    logging.info ("    FLiM Mode :"+str((flags & 0x04)==0x04))
                    logging.info ("    Prod Node :"+str((flags & 0x02)==0x02))
                    logging.info ("    Cons Node :"+str((flags & 0x01)==0x01)+"\r")
                    qnn_response = True
                    
                elif op_code == 4:  # Track Power is OFF
                    
                    logging.info ("Pi-SPROG: Received TOF (Track OFF) acknowledgement")
                    track_power_on = False

                elif op_code == 5:  # Track Power is ON
                    
                    logging.info ("Pi-SPROG: Received TON (Track ON) acknowledgement")
                    track_power_on = True
                    
                elif op_code == 76:  # Service Mode Status response
                    
                    session_id = int(chr(byte_string[9]) + chr(byte_string[10]),16)
                    service_mode_status = int(chr(byte_string[11]) + chr(byte_string[12]),16)
                    if service_mode_status == 0: status = "Reserved"
                    elif service_mode_status == 1: status = "No Acknowledge"
                    elif service_mode_status == 2: status = "Overload on Programming Track"
                    elif service_mode_status == 3: status = "Write Acknowledge"
                    elif service_mode_status == 4: status = "Busy"
                    elif service_mode_status == 5: status = "CV Out of Range"
                    else: status = "Unrecognised response code" + str (service_mode_status)
                    logging.debug ("Pi-SPROG: Received SSTAT (Service Mode Status) - Session: "
                                           + str(session_id) + ", Status: " + status)
            except:
                logging.error("Pi-SPROG: Couldn't decode CBUS Message: "+byte_string.decode('Ascii')+"\r")
            
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
    global logging
    global can_bus_id
    if (mj_pri < 0 or mj_pri > 2):
        logging.error("CBUS Command - Invalid Major Priority "+str(mj_pri))
    elif (min_pri < 0 or min_pri > 3):
        logging.error("CBUS Command - Invalid Minor Priority "+str(min_pri))
    elif (op_code < 0 or op_code > 255):
        logging.error("CBUS Command - Op Code out of range "+str(op_code))
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
# namely logging of all the CBUS commands sent to the Pi SPROG
#------------------------------------------------------------------------------


def initialise_pi_sprog (port_name:str="/dev/serial0",
                         baud_rate:int = 115200,
                         dcc_debug_mode:bool = False):
    global logging
    global debug
    global threads_started
    # Assign the global "enhanced debugging" flag
    debug = dcc_debug_mode
    # Rx and Tx threads are Daemon so they will terminate with the main programme
    if not threads_started:
        logging.info ("Pi-SPROG: Starting Tx and Rx Threads")
        rx_thread = threading.Thread (target=thread_to_read_received_data)
        rx_thread.setDaemon(True)
        rx_thread.start()
        tx_thread = threading.Thread (target=thread_to_send_buffered_data)
        tx_thread.setDaemon(True)
        tx_thread.start()
        threads_started = True
    # First try to configure the port (capturing any exceptions)
    logging.info ("Pi-SPROG: Configuring Serial Port")
    try:    
        # We're not receiving anything else on this port so its OK to set up the port without
        # a timeout - as we are only interested in "complete" messages (terminated by ';')
        serial_port.port = port_name
        serial_port.baudrate = baud_rate
        serial_port.bytesize = 8
        serial_port.timeout = None
        serial_port.parity = serial.PARITY_NONE
        serial_port.stopbits = serial.STOPBITS_ONE
    except Exception as exception:
        # If the attempt to configure the serial port fails then we catch the exception
        logging.error("Pi-SPROG: Error configuring Serial Port - "+str(exception))
    # Next, try to open the port (again, catching any exceptions)
    if not serial_port.is_open:
        logging.info ("Pi-SPROG: Opening Serial Port")
        try:
            serial_port.open()
            serial_port.reset_input_buffer()
            serial_port.reset_output_buffer()
        except Exception as exception:
            # If the attempt to open the serial port fails then we catch the exception (and return)
            logging.error("Pi-SPROG: Error opening Serial Port - "+str(exception))
    # finally, we query the command station status to verify connectivity
    if serial_port.is_open and threads_started:
        pi_sprog_connected = query_command_station_status()
    else:
        pi_sprog_connected = False
    return(pi_sprog_connected)

#------------------------------------------------------------------------------
# Function to send a RSTAT (Request command Station Status) command (response logged)
# Returns True if successful and False if no response is received (timeout)
#------------------------------------------------------------------------------

def query_command_station_status():
    global rstat_response
    # Query the status of the command station to confirm connectivity
    rstat_response = False
    logging.info ("Pi-SPROG: Sending RSTAT command (Request Command Station Status)")
    send_cbus_command (mj_pri=2, min_pri=2, op_code=12)
    # If the SPROG hasn't responded in 2 seconds its not going to respond at all
    timeout_start = time.time()
    while time.time() < timeout_start + 2:
        if rstat_response: break
        time.sleep(0.001)
    if rstat_response != True:
        logging.error("Pi-SPROG: Request Command Station Status failed")
    return (rstat_response==True)

#------------------------------------------------------------------------------
# Function to send a QNN (Query Node Number) command (response will be logged)
# Returns True if successful and False if no response is received (timeout)
#------------------------------------------------------------------------------

def query_node_number():
    global qnn_response
    qnn_response = False
    logging.info ("Pi-SPROG: Sending QNN command (Query Node Number)")
    send_cbus_command (mj_pri=2, min_pri=3, op_code=13)
    # If the SPROG hasn't responded in 2 seconds its not going to respond at all
    timeout_start = time.time()
    while time.time() < timeout_start + 2:
        if qnn_response: break
        time.sleep(0.001)
    if qnn_response != True:
        logging.error("Pi-SPROG: Query Node Number failed")
    return(qnn_response)

#------------------------------------------------------------------------------
# Function called on shutdown to turn off DCC bus power and close the comms port
#------------------------------------------------------------------------------

def sprog_shutdown():
    global logging
    # First switch off the DCC bus supply
    if track_power_on: request_dcc_power_off()
    # Now close the comms port
    if serial_port.is_open:
        logging.info ("Pi-SPROG: Closing Serial Port")
        try:
            serial_port.close()
        except Exception as exception:
            # If the attempt to open the serial port fails then we catch the exception
            logging.error("Pi-SPROG: Error closing Serial Port - "+str(exception))
    return()

#------------------------------------------------------------------------------
# Externally Called Function to turn on the track power
#------------------------------------------------------------------------------

def request_dcc_power_on():
    global track_power_on
    global logging
    track_power_on = None    
    # Only bother sending commands to the Pi Sprog if the serial port has been opened
    if serial_port.is_open:
        # Send the command to switch on the Track Supply (to the DCC Bus)
        logging.info ("Pi-SPROG: Sending RTON command (Request Track Power On)")
        send_cbus_command (mj_pri=2, min_pri=2, op_code=9)
        # Now wait until we get confirmation thet the Track power is on
        # If the SPROG hasn't responded in 2 seconds its not going to respond at all
        timeout_start = time.time()
        while time.time() < timeout_start + 2:
            if track_power_on: break
            time.sleep(0.001)
        # Give things time to get established before sending out any commands
        time.sleep (0.5)
    if track_power_on != True:
        logging.error("Pi-SPROG: Request to turn on Track Power failed")
    return(track_power_on == True)

#------------------------------------------------------------------------------
# Externally Called Function to turn off the track power
#------------------------------------------------------------------------------

def request_dcc_power_off():
    global track_power_on
    global logging
    track_power_on = None
    # Only bother sending commands to the Pi Sprog if the serial port has been opened
    if serial_port.is_open:
        # Send the command to switch on the Track Supply (to the DCC Bus)
        logging.info ("Pi-SPROG: Sending RTOF command (Request Track Power Off)")
        send_cbus_command (mj_pri=2, min_pri=2, op_code=8)
        # Now wait until we get confirmation thet the Track power is on
        # If the SPROG hasn't responded in 2 seconds its not going to respond at all
        timeout_start = time.time()
        while time.time() < timeout_start + 2:
            if not track_power_on:break
            time.sleep(0.001)
        time.sleep (0.5)
    if track_power_on != False:
        logging.error("Pi-SPROG: Request to turn off Track Power failed")
    return(track_power_on == False)

#------------------------------------------------------------------------------
# Externally Called Function to send an Accessory Short CBUS On/Off Event
#------------------------------------------------------------------------------

def send_accessory_short_event (address:int, active:bool):
    global pi_cbus_node
    global track_power_on
    global logging
    if (address < 1 or address > 2047):
        logging.error ("Pi-SPROG: Invalid DCC short event accessory address: "+ str(address))
    # Only try to send the command if the PI-SPROG-3 has initialised correctly
    elif track_power_on:
        byte1 = (pi_cbus_node & 0xff00) >> 8
        byte2 = (pi_cbus_node & 0x00ff)
        byte3 = (address & 0xff00) >> 8
        byte4 = (address & 0x00ff)
        #  Send a ASON or ASOF Command (Accessoy Short On or Accessory Short Off)
        if active:
            logging.debug ("Pi-SPROG: Sending DCC command ASON (Accessory Short ON) to DCC address: "+ str(address))
            send_cbus_command (2, 3, 152, byte1, byte2, byte3, byte4)
        else:
            logging.debug ("Pi-SPROG: Sending DCC command ASOF (Accessory Short OFF) to DCC address: "+ str(address))
            send_cbus_command (2, 3, 153, byte1, byte2, byte3, byte4)
    return ()

#------------------------------------------------------------------------------
# Externally Called Function to programme a single CV (used for testing)
# Returns True if successful and False if no response is received (timeout)
#------------------------------------------------------------------------------

def service_mode_write_cv (cv:int, value:int):
    global track_power_on
    global service_mode_status
    global logging
    if (cv < 0 or cv > 1023):
        logging.error("Pi-SPROG: WCVS (Write CV in Service Mode) - Invalid CV "+str(cv))
    elif (value < 0 or value > 255):
        logging.error("Pi-SPROG: WCVS (Write CV in Service Mode) - Invalid value for CV"+str(value))
    # Only try to send the command if the PI-SPROG-3 has initialised correctly
    elif track_power_on:
        byte1 = 255                    # Session ID
        byte2 = (cv & 0xff00) >> 8     # High CV
        byte3 = (cv & 0x00ff)          # Low CV
        byte4 = 1                      # Mode (1 = Direct bit)
        byte5 = value                  # value to write
        #  Send a Command to write the CV
        logging.info ("Pi-SPROG: WCVS (Write CV in Service Mode) - Session: "
                             + str(byte1) + ", CV: " + str(cv) + ", Value: " + str(value))
        send_cbus_command (2, 2, 162, byte1, byte2, byte3, byte4, byte5)
        # Now wait until we get a response that the CV has been programmed
        # If the SPROG hasn't responded in 5 seconds its not going to respond at all
        service_mode_status = 0
        timeout_start = time.time()
        while time.time() < timeout_start + 5:
            if service_mode_status == 3: break
            time.sleep(0.001)
        if service_mode_status != 3: logging.error("Pi-SPROG: WCVS (Write CV in Service Mode) - Failed")
        time.sleep (0.1)
    return (service_mode_status == 3)

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

def send_DCC_accessory_decoder_packet (address:int, active:bool, output_channel:int = 0, repeat:int = 3):
    global track_power_on
    global logging
    if (address < 1 or address > 511):
        logging.info("Error: send_accessory_decoder_packet - Invalid address "+str(address))
    elif (output_channel < 0 or output_channel > 7):
        logging.info("Error: send_accessory_decoder_packet - Invalid output channel " +
                      str(output_channel)+" for address "+str(address))    
    elif (repeat < 0 or repeat > 255):
        logging.info("Error: send_accessory_decoder_packet - Invalid Repeat Value " +
                      str(repeat)+" for address "+str(address))
    # Only try to send the command if the PI-SPROG-3 has initialised correctly
    elif track_power_on:
        low_addr = address & 0x3F
        high_addr = (( ~ address) >> 6) & 0x07
        byte1 = (0x80 | low_addr)
        byte2 = (0x80 | (high_addr << 4) | (active << 3) | output_channel & 0x07)
        byte3 = (byte1 ^ byte2)
        #  Send a RDCC3 Command (Request 3-Byte DCC Packet) via the CBUS
        logging.debug ("PI >> SPROG - RDCC3 (Send 3 Byte DCC Packet) : Address:"
                        + str(address) + "  Channel:" + str(output_channel) +"  State:" + str(active))
        send_cbus_command (2, 2, 128, repeat, byte1, byte2, byte3)
    return ()

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

def send_extended_DCC_accessory_decoder_packet (address:int, aspect:int, repeat:int = 3, alt_address = False):
    global track_power_on
    global logging
    if (address < 1 or address > 2044):
        logging.info("Error: send_extended_DCC_accessory_decoder_packet - Invalid address "+str(address))
    elif (aspect < 0 or aspect > 31):
        logging.info("Error: send_extended_DCC_accessory_decoder_packet - Invalid aspect "+str(aspect))
    elif track_power_on:
        # DCC Address interpretation 1 and 2
        address -= 1
        low_addr = (address & 0x03)
        board_addr = (address >> 2)
        if alt_address: board_addr = board_addr+1
        mid_addr = board_addr & 0x3F
        high_addr = ((~board_addr) >> 6) & 0x07
        byte1 = (0x80 | mid_addr)
        byte2 = (0x01 | (high_addr << 4) | (low_addr << 1))
        byte3 = (0x1F & aspect)
        byte4 = (byte1 ^ byte2 ^ byte3)
        #  Send a RDCC4 Command (Request 4-Byte DCC Packet) via the CBUS
        logging.debug ("PI >> SPROG - RDCC4 (Send 4 Byte DCC Packet) : Address:"
                        + str(address) + "  Aspect:" + str(aspect))
        send_cbus_command (2, 2, 160, repeat, byte1, byte2, byte3, byte4)
    return()

###########################################################################
