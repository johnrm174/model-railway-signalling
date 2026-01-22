####################################################################################################
# This is a WiThrottle Server for the DCC Signalling system providing the following:
#
# 1) Loco Roster - loco names, dcc_addresses, function key labels and function key types
# 2) Acquire loco (via the roster or DCC address provided by the client) / Release loco
# 3) Control the loco - speed, direction, function keys (F0-F12 only)
# 4) Control DCC Bus Power - ON /OFF
#
# Fully Tested with Engine Driver (Android)
# Cab engineer (Android) mmostly works but all functions are defaulting to momentary
#
# More info Here: https://www.jmri.org/help/en/package/jmri/jmrit/withrottle/Protocol.shtml
# Acknowledgements to JMRI debugging logs (enabled in  for the WiThrottle elements)
# Add:   <logger name="jmri.jmrit.withrottle" level="DEBUG"/>  to default_lcf.xml
#
# API Functions (for the Editor to call)
#    dcc_power_status_updated(dcc_power:bool) - this is the registered callback for DCC power changes
#    start_throttle_server(allow_list:[name1:str, name2:str, etc], use_allow_list:bool, dcc_power:bool)
#    stop_throttle_server()
#
# Calls the following library functions (for the pi-SPROG interface):
#    library.set_loco_speed_and_direction
#    library.request_dcc_power_on
#    library.request_dcc_power_off
#    library.request_loco_session
#    library.set_loco_function
#    library.release_loco_session
#
# Calls the following editor functions:
#    settings.get_control("locomotiveroster")
#
####################################################################################################


import re
import threading
import asyncio
import socket
import logging
from zeroconf.asyncio import AsyncZeroconf, AsyncServiceInfo

from . import library
from . import settings

#-----------------------------------------------------------------------------------------------
# Global parameters used by the WiThrottle Server
#-----------------------------------------------------------------------------------------------

# Keep track of active writers (connections) and the server loop
connected_clients = set()
server_loop = None
stop_event = None

# These are the constants for Server Identification
server_host = socket.gethostname()
server_name = f"DCCsignalling@{server_host}"
server_port_number = 12021

# Global flags for DCC power state and enhanced debug logging
server_debug = False
dcc_power_state = None
maximum_no_of_functions = 13

# Connection Security - simple whitelist
enforce_allow_list = True
list_of_allowed_clients = ["Nokia G22"]

#-----------------------------------------------------------------------------------------------
# Function for sending the capabilities to WiThrottle Client
#-----------------------------------------------------------------------------------------------

async def send_capabilities(writer):
    # Power capability: 2 = DCC power on/off supported
    power_capability ="PPA2\n"
    writer.write(power_capability.encode())
    if server_debug: logging.debug(f"Throttle Server: Sent Capabilities - Power: {power_capability!r}")
    # No turnout, route or consist count capability blocks for the time being
    # Consist count is set to zero for initialisation
    consist_count ="RCC0\n"
    writer.write(consist_count.encode())
    if server_debug: logging.debug(f"Throttle Server: Sent Capabilities - Consist Count: {consist_count!r}")
    # Heartbeat interval (10 seconds)
    heartbeat_interval ="*10\n"
    writer.write(heartbeat_interval.encode())
    if server_debug: logging.debug(f"Throttle Server: Sent Capabilities - Heartbeat Interval: {heartbeat_interval!r}")
    await writer.drain()
    
#-----------------------------------------------------------------------------------------------
# Function for sending the Roster to WiThrottle Client
#-----------------------------------------------------------------------------------------------

async def send_roster(writer):
    # The roster_data saved/retrieved from settings comprises a dictionary of locomotives
    # (with the loco name as the key) {"loco":[address:int, [list_of_function_settings] ]}
    # where each function setting comprises [key_name:str, latching:bool]
    ROSTER = settings.get_control("locomotiveroster")
    # JMRI-style delimiters to use when compiling the messages to the client
    entry_sep = "]\\["
    field_sep = "}|{"
    # If there are no roster entries then we just send 'RL0' to the client
    if len(ROSTER) == 0:
        roster_message = "RL0\n"
    else:
        roster_entries = []
        for name, data in ROSTER.items():
            # We need to generate a list of function_names from the list_of_function_settings
            # Remember - each entry is [address, [ [key_name, latching], [key_name, latching] ] ]
            address = data[0]
            address_type = "L" if int(address) > 127 else "S" 
            # data[1] is the inner list containing the [name, latching] pairs
            list_of_function_settings = data[1] if len(data) > 1 else []
            # Extract just the names (the first element of each inner pair)
            function_names = [f[0] for f in list_of_function_settings]
            # Build the function part of the string
            if function_names:
                # Join names with field_sep, and put one field_sep at the start
                function_block = field_sep + field_sep.join(function_names)
            else:
                function_block = ""
            # Build entry: Name}|{Address}|{Type}|{F0}|{F1}...
            entry = f"{name}{field_sep}{address}{field_sep}{address_type}{function_block}"
            roster_entries.append(entry)
        # Join all loco entries using the entry separator
        roster_message = f"RL{len(roster_entries)}{entry_sep}{entry_sep.join(roster_entries)}\n"
        writer.write(roster_message.encode())
    if server_debug: logging.debug(f"Throttle Server: Sent Roster: {roster_message!r}")
    await writer.drain()

#-----------------------------------------------------------------------------------------------
# Function for sending the the power state to WiThrottle Client
#-----------------------------------------------------------------------------------------------

async def send_power_state(writer):
    # Sends status based on the global dcc_power_state flag
    state = 1 if dcc_power_state else 0
    power_state = f"PPA{state}\n"
    writer.write(power_state.encode())
    if server_debug: logging.debug(f"Throttle Server: Sent DCC Power state: {power_state!r}")
    await writer.drain()

#-----------------------------------------------------------------------------------------------
# Function for handling connections initiated from each WiThrottle Client
#-----------------------------------------------------------------------------------------------

async def handle_client(reader, writer):
    # The dictionary to map WiThrottle session keys to SPROG session IDs (also tracks other important session info)
    # Format of each entry: {"T1": {"session_id":2, "dcc_address":3, "addr_type":"S", "speed":0, "forward":True},}
    # Where T1 is the Throttle ID sent by the client and session_id is the session ID returned by the Pi-SPROG
    wi_sessions = {}
    # Retrieve the basic client details
    peer = writer.get_extra_info("peername")
    peer_ip_address = peer[0]
    peer_port_number = peer[1]
    client_name = "unknown"
    # Add this connection to the list of writers
    connected_clients.add(writer)
    logging.info(f"Throttle Server: Starting session from {peer_ip_address}:{peer_port_number}")    
    # Send the WiThrottle Protocol version to the client
    protocol_version = "VN2.0\n" 
    writer.write(protocol_version.encode())
    if server_debug: logging.debug(f"Throttle Server: Sent Protocol Version: {protocol_version!r}")    
    await writer.drain()
    # Put exception handling around the client loop just in case
    try: 
        while True:
            # If no data then the client has disconnected. Exception handling is to cover
            # the case of a client being killed before we close the server-side connection
            try: data = await reader.read(1024)
            except: data = None
            if not data: break
            # We have data so we go on to parse the messages
            messages = data.decode('utf-8', errors='ignore').split('\n')
            for message in messages:
                message = message.strip()
                if not message: continue
                if server_debug: logging.debug(f"Throttle Server: Received Message: {message!r}")
                #------------------------------------------------------------
                # Identity 'N' or Hardware Update 'HU' Message
                #------------------------------------------------------------
                if message.startswith("N") or message.startswith("HU"):
                    if message.startswith("N"):
                        client_name = message[1:]
                        # Apply connection security (whitelist)
                        if enforce_allow_list and client_name not in list_of_allowed_clients:
                            logging.warning(f"Throttle Server: REJECTED unauthorized client: '{client_name}'")
                            # WiThrottle doesn't have a standard "Access Denied" message, 
                            # but sending a screen message helps the user understand why it failed.
                            writer.write("HMUnauthorized Device. Closing Connection.\n".encode())
                            await writer.drain()
                            break # Exits the while loop and triggers the 'finally' cleanup
                        else:
                            # Connection is allowed
                            logging.info(f"Throttle Server: Connected WiThrottle Client is '{client_name}'")
                    if message.startswith("HU") and server_debug: logging.debug("Throttle Server: Handling Hardware Update Message")
                    # Send Hardware info and server name
                    hardware_type_response = f"HT{server_name}\n"
                    writer.write(hardware_type_response.encode())
                    if server_debug: logging.debug(f"Throttle Server: Sent Hardware Type: {hardware_type_response!r}")
                    server_name_response = f"*NM{server_name}\n"
                    writer.write(server_name_response.encode())
                    if server_debug: logging.debug(f"Throttle Server: Sent Server Name: {server_name_response!r}")
                    # Send the ACTUAL roster, Send capabilities and power state
                    await send_roster(writer)
                    await send_capabilities(writer)
                    await send_power_state(writer)
                    # End the burst with the terminator
                    burst_terminator = "#\n"
                    writer.write(burst_terminator.encode())
                    if server_debug: logging.debug(f"Throttle Server: Sent Burst Terminator: {burst_terminator!r}")
                    await writer.drain()
                    continue
                #------------------------------------------------------------
                # Handle Heartbeat Message (MUST RESPOND TO KEEP SOCKET OPEN)
                #------------------------------------------------------------
                if message.startswith("*"):
                    if message == "*+":
                        if server_debug: logging.debug("Throttle Server: Handling Heartbeat Timeout Message")
                        heartbeat_response = "*10\n"
                        writer.write(heartbeat_response.encode()) # Start EKG with 10s timeout
                        if server_debug: logging.debug(f"Throttle Server: Sent Heartbeat Response: {heartbeat_response!r}")
                    else:
                        if server_debug: logging.debug("Throttle Server: Handling regular Heartbeat Message")
                        heartbeat_response = "*\n"
                        writer.write(heartbeat_response.encode()) # Standard pulse
                        if server_debug: logging.debug(f"Throttle Server: Sent Heartbeat Response: {heartbeat_response!r}")
                    await writer.drain()
                    continue
                #------------------------------------------------------------
                # Handle DCC Power ON/OFF requests
                #------------------------------------------------------------
                if message.startswith("PPA"):
                    state = message[3:]
                    if state == "1":
                        if server_debug:logging.debug("Throttle Server: Handling Power ON Request")
                        library.request_dcc_power_on()
                    else:
                        if server_debug:logging.debug("Throttle Server: Handling Power OFF Request")
                        library.request_dcc_power_off()
                    # Note that we don't acknowledge the power state change back to app or update the
                    # global dcc_power_state here - we wait for callback confirmation
                    continue
                #---------------------------------------------------------------------------
                # Multi-Throttle Commands (acquire/control/release loco)
                #---------------------------------------------------------------------------
                if message.startswith("M"):
                    # Get the Index for our internal dictionary of registered locos
                    throttle_index = message[1] 
                    # Get the Full Key (for replying to the app, e.g., '0' or 'T0')
                    full_key_match = re.match(r"M([^+\-VRFL<q]+)", message)
                    full_key = full_key_match.group(1) if full_key_match else throttle_index
                    # Get the Action part of the message
                    match = re.search(r"[+\-VRFL<q].*", message)
                    if not match: continue
                    # We have an action match we can handle
                    rest_of_message = match.group(0)
                    #-----------------------------------------------------------------------
                    # ACQUIRE LOCO - This section triggers when the user selects a train
                    #in the App. Incoming message format example: "M0+L4701<;>EClass 47"
                    #-----------------------------------------------------------------------
                    if rest_of_message.startswith("+"):
                        if server_debug: logging.debug("Throttle Server: Handling Acquire Locomotive Request")
                        try:
                            # Parse the raw address with prefix (e.g. "S3" or "L4701")
                            address_match = re.search(r"\+(.*?)<;>", rest_of_message)
                            raw_address = address_match.group(1) if address_match else "3"
                            # Split prefix (S or L) from the Raw Address to get the numerical DCC Address
                            address_type = raw_address[0] if raw_address and raw_address[0] in ("S", "L") else ""
                            dcc_address_str = re.sub(r"\D", "", raw_address)  # numeric-only address for AS messages
                            dcc_address_int = int(dcc_address_str)
                            # See if we have been given a loco name (preserve leading 'H' if client provided it)
                            # If we have, this should match the name in our local roster (that we provided to
                            # the client). If not, then it will be a request to acquire a loco by DCC address.
                            loco_name_match = re.search(r"<;>E(.+)$", rest_of_message)
                            if loco_name_match:
                                loco_name = loco_name_match.group(1)
                            else:
                                if "<;>EH" in rest_of_message:
                                    loco_name = "H" + rest_of_message.split("<;>EH")[1]
                                elif "<;>E" in rest_of_message:
                                    loco_name = rest_of_message.split("<;>E")[1]
                                else:
                                    loco_name = ""
                            # Request a new session for the DCC Address from the Pi-SPROG interface
                            # Note that we only care about the DCC address here (not the loco_name)
                            session_id = library.request_loco_session(dcc_address_int)
                            if session_id > 0:
                                # Session was successfully acquired - save it in the dict we use to track
                                wi_sessions[throttle_index] = {"session_id": session_id,"addr_str": raw_address,"speed": 0,"forward": True}
                                # Echo the loco acquisition back to the client 
                                address_to_send = f"M{full_key}+{raw_address}<;>\n"
                                writer.write(address_to_send.encode())
                                if server_debug: logging.debug(f"Throttle Server: Sent session confirmation for DCC address: {address_to_send!r}")
                                # Retrieve the current Roster from Settings
                                ROSTER = settings.get_control("locomotiveroster")
                                # Remove the 'H' prefix that some WiThrottle clients use for the loco_name
                                roster_lookup = loco_name
                                if roster_lookup.startswith('H') and roster_lookup not in ROSTER:
                                    roster_lookup = roster_lookup[1:]
                                # Create a list of Function Key Names names - If it's a roster match use the name.
                                # If it's a raw DCC address, Then the Client will always use generic button names
                                # and enable all the buttons no matter what we do - so send an empty list.
                                if roster_lookup in ROSTER:
                                    roster_entry = ROSTER[roster_lookup]
                                    function_names = roster_entry[1] if len(roster_entry) > 1 else []
                                else:
                                    function_names = []
                                # Build JMRI-style function-list block using ]\[ delimiters
                                func_name_block = [f[0] for f in function_names]
                                func_list_block = "]\\[" + "]\\[".join(func_name_block) + "]\\["
                                # Send L message (with all the function key names in it
                                roster_label_l_msg = f"M{full_key}L{raw_address}<;>{func_list_block}\n"
                                writer.write(roster_label_l_msg.encode())
                                if server_debug: logging.debug(f"Throttle Server: Sent Function Label message: {roster_label_l_msg!r}")
                                # Send the Latching/Momentary Configuration and sync the initial state (to OFF)
                                for f_idx, (name, is_latching) in enumerate(function_names):
                                    # Specify if the button is Latching (F1) or Momentary (F0) to the client
                                    latch_prefix = "F1" if is_latching else "F0"
                                    function_type_message = f"M{full_key}AS{dcc_address_str}<;>{latch_prefix}{f_idx}\n"
                                    writer.write(function_type_message.encode())
                                    if server_debug: logging.debug(f"Throttle Server: Sent Function Type message: {function_type_message!r}")
                                    # FORCE the function key state to OFF (0) (after latching/non latching has been sent)
                                    function_state_message = f"M{full_key}AS{dcc_address_str}<;>F0{f_idx}\n"
                                    writer.write(function_state_message.encode())
                                    if server_debug: logging.debug(f"Throttle Server: Sent Function State message: {function_state_message!r}")
                                    if server_debug: logging.debug(f"Throttle Server: Configured F{f_idx} (Latch={is_latching}) and initialized OFF")
                                # Other common initial syncs (V, R, s) also use the numeric address
                                writer.write(f"M{full_key}AS{dcc_address_str}<;>V0\n".encode())
                                writer.write(f"M{full_key}AS{dcc_address_str}<;>R1\n".encode())
                                writer.write(f"M{full_key}AS{dcc_address_str}<;>s1\n".encode())
                                await writer.drain()
                                if server_debug: logging.debug(f"Throttle Server: Sent Initial Speed/Direction/Steps for DCC Address: {dcc_address_str!r}")
                                # Finally, Send Messages to the Pi-SPROG to turn off all supported functions and 
                                # set thespeed to zero so we start the session in a known state (just in case)
                                library.set_loco_speed_and_direction(session_id, 0, False)
                                # Send Function OFF commands to the Pi-SPROG interface
                                for function in range(maximum_no_of_functions):
                                    library.set_loco_function(session_id, function, False)
                        except Exception as e:
                            logging.error(f"Acquisition error: {e}")
                        continue
                    #-----------------------------------------------------------------------
                    # CONTROL & QUERIES (V, R, F, q, -) ---
                    #-----------------------------------------------------------------------
                    if throttle_index in wi_sessions:
                        session = wi_sessions[throttle_index]
                        session_id = session["session_id"]
                        address_str = session["addr_str"]
                        # Handle Queries (qV, qR)
                        if "qV" in rest_of_message:
                            if server_debug:logging.debug("Throttle Server: Handling Query Speed Request")
                            speed_response = f"M{full_key}AS{address_str}<;>V{session['speed']}\n"
                            writer.write(speed_response.encode())
                            if server_debug: logging.debug(f"Throttle Server: Sent Speed Response: {speed_response!r}")
                            await writer.drain()
                            continue
                        if "qR" in rest_of_message:
                            if server_debug:logging.debug("Throttle Server: Handling Query Direction Request")
                            direction_value = 1 if session["forward"] else 0
                            direction_response = f"M{full_key}AS{address_str}<;>R{direction_value}\n"
                            writer.write(direction_response.encode())
                            if server_debug: logging.debug(f"Throttle Server: Sent direction Response: {direction_response!r}")
                            await writer.drain()
                            continue
                        # Clean the action string for control commands
                        clean_action = rest_of_message.replace("<;>", "")
                        # SPEED (V)
                        if clean_action.startswith("V"):
                            if server_debug:logging.debug("Throttle Server: Handling Speed Change Request")
                            speed_value = int(clean_action[1:])
                            session["speed"] = speed_value
                            library.set_loco_speed_and_direction(session_id, session["speed"], session["forward"])
                        # DIRECTION (R)
                        elif clean_action.startswith("R"):
                            if server_debug:logging.debug("Throttle Server: Handling Direction Change Request")
                            direction_value = int(clean_action[1:])
                            session["forward"] = (direction_value == 1)
                            library.set_loco_speed_and_direction(session_id, session["speed"], session["forward"])
                        # FUNCTION (F)
                        elif clean_action.upper().startswith("F"):
                            if server_debug:logging.debug("Throttle Server: Handling Function Change Request")
                            try:
                                state = (clean_action[1] == '1')
                                func_id = int(clean_action[2:])
                                library.set_loco_function(session_id, func_id, state)
                                # Echo back to keep app buttons in sync
                                function_response = f"M{full_key}AS{address_str}<;>{clean_action.upper()}\n"
                                writer.write(function_response.encode())
                                if server_debug: logging.debug(f"Throttle Server: Sent Function Response: {function_response!r}")
                                await writer.drain()
                            except Exception as e:
                                logging.error(f"Function Error: {e}")
                        # RELEASE (-)
                        elif clean_action.startswith("-"):
                            if server_debug:logging.debug("Throttle Server: Handling Release Locomotive Request")
                            # Force Loco to stop and turn off functions in hardware before releasing
                            library.set_loco_speed_and_direction(session_id, 0, False) # Speed 0, Reverse
                            for function in range(maximum_no_of_functions):
                                library.set_loco_function(session_id, function, False)
                            # Release from the Pi-SPROG session
                            library.release_loco_session(session_id)
                            # Inform client the loco has been released
                            release_loco_response = f"M{full_key}-*\n"
                            writer.write(release_loco_response.encode())
                            if server_debug:logging.debug(f"Throttle Server: Sent Release Locomotive response: {release_loco_response!r}")
                            await writer.drain()
                            # Remove the Session from the dict of sessions
                            del wi_sessions[throttle_index]
                    continue
                #---------------------------------------------------------------------------
                # Handle Quit notification (Client has gracefully disconnected)
                #---------------------------------------------------------------------------
                if message == "Q":
                    logging.info(f"Throttle Server: Quit command received from {peer_ip_address}:{peer_port_number} ('{client_name}')")
                    break # This exits the while loop and goes to the 'finally' block
                
                #---------------------------------------------------------------------------
                # Handle Queries - This prevents 'M0A*<;>qV' and 'M0A*<;>qR' from crashing the loop
                #---------------------------------------------------------------------------
                if "<;>q" in message:
                    # Optimization: To stop Engine Driver from spamming qV and qR, 
                    # we echo back the current state, but 'continue' is the priority.
                    if server_debug: logging.debug(f"Throttle Server: Ignored Query: {message!r}")
                    continue
    finally:
        # This code runs no matter HOW the loop exits (Quit command, crash, or disconnect)
        if server_debug: logging.debug(f"Throttle Server: Cleaning up session for {peer_ip_address}:{peer_port_number} ('{client_name}')")
        for index in list(wi_sessions.keys()):
            try:
                session_id = wi_sessions[index]["session_id"]
                dcc_address = wi_sessions[index]["addr_str"]
                # Release the loco in the Pi-SPROG hardware
                library.release_loco_session(session_id)
                if server_debug: logging.debug(f"Throttle Server: Released session {session_id} for loco {dcc_address}")
            except Exception as e:
                logging.error(f"Throttle Server: Error releasing session during cleanup: {e}")
        # Close the socket properly
        connected_clients.remove(writer)
        try:
            writer.close()
            await writer.wait_closed()
            logging.info(f"Throttle Server: Session for {peer_ip_address}:{peer_port_number} ('{client_name}') has been terminated")    
        except Exception as e:
            logging.error(f"Throttle Server: Error closing socket: {e}")
    return()

#-----------------------------------------------------------------------------------------------
# Internal Function To broadcast messages to al lconnected clients
#-----------------------------------------------------------------------------------------------

def broadcast_to_all(message):
    if not message.endswith('\n'): message += '\n'
    for writer in connected_clients:
        try:
            writer.write(message.encode("utf-8"))
        except Exception as e:
            logging.error(f"Throttle Server: failed to Broadcast message to client: {e}")
    return()

#-----------------------------------------------------------------------------------------------
# Find the local IP address of the machine we are running on
#-----------------------------------------------------------------------------------------------

def find_local_ip_address():
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        test_socket.connect(('10.255.255.255', 1))
        ip_address = test_socket.getsockname()[0]
        logging.debug("MQTT-Client: Local IP address is "+ip_address)
    except:
        logging.error("MQTT-Client: Could not retrieve local IP address")
        ip_address = "<unknown>"
    finally:
        test_socket.close()
    return(ip_address)

#-----------------------------------------------------------------------------------------------
# The actual WiThrottle Server runs in a seperate thread to the main Tkinter thread
#-----------------------------------------------------------------------------------------------

async def throttle_Server_thread():
    global server_loop, stop_event
    server_loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    server_ip_address = socket.inet_aton(find_local_ip_address())
    # Only continue if we have found the local IP address
    if server_ip_address is not None:
        try:
            readable_ip_address = socket.inet_ntoa(server_ip_address)
            logging.info(f"Throttle Server: Starting Throttle server on {readable_ip_address}:{server_port_number}")
            aiozc = AsyncZeroconf()
            # Start the server and configure the service entry (for discovery)
            server = await asyncio.start_server(handle_client, "0.0.0.0", server_port_number)
            info = AsyncServiceInfo(
                "_withrottle._tcp.local.",
                f"{server_name}._withrottle._tcp.local.",
                addresses=[server_ip_address],
                port=server_port_number,
                properties={"roster": "1",},
                server=server_name,)
            await aiozc.zeroconf.async_register_service(info)
            # Start the server but don't block forever
            serve_task = asyncio.create_task(server.serve_forever())
            logging.info(f"Throttle Server: Throttle Server '{server_name}' registered successfully")
            # This is the key: The thread "hangs" here until stop_event.set() is called
            await stop_event.wait()
            logging.info(f"Throttle Server: Throttle Server {server_name} Shutdown initiated")
            serve_task.cancel()
            
        finally:
            if aiozc: await aiozc.async_close()
            if server: server.close()
            await server.wait_closed()
            logging.info("Throttle Server: Clean Shutdown complete")
    else:
        aiozc, server = None, None
        logging.error(f"Throttle Server: Could not start Throttle server as IP address could not be retrieved")
    return()

#-----------------------------------------------------------------------------------------------
# This is the function called to start the WiThrottle Server (which runs in a seperate thread)
#-----------------------------------------------------------------------------------------------

def start_throttle_server(allow_list:list, use_allow_list:bool, dcc_power:bool):  
    global dcc_power_state
    global enforce_allow_list
    global list_of_allowed_clients
    # Set the global variables
    dcc_power_state = dcc_power
    enforce_allow_list = use_allow_list
    list_of_allowed_clients = allow_list
    # This inner function runs inside the new thread
    def run_loop(): asyncio.run(throttle_Server_thread())
    server_thread = threading.Thread(target=run_loop, daemon=True)
    server_thread.setDaemon(True)
    server_thread.start()
    # Register for DCC Power update callbacks from the SPROG
    library.subscribe_to_dcc_power_updates(dcc_power_status_updated)
    return()

#-----------------------------------------------------------------------------------------------
# This is the function called to stop the WiThrottle Server cleanly (threadsafe)
#-----------------------------------------------------------------------------------------------

def stop_throttle_server():
    global server_loop
    logging.info("Throttle Server: Stopping Throttle Server")
    if server_loop and server_loop.is_running() and stop_event:
        if server_debug: logging.debug("Throttle Server: Stopping Throttle Server Thread")
        server_loop.call_soon_threadsafe(stop_event.set)
    server_loop = None
    # De Register for DCC Power update callbacks from the SPROG
    library.unsubscribe_from_dcc_power_updates(dcc_power_status_updated)
    logging.info("Throttle Server: Throttle Server has been Terminated")
    return()

#-----------------------------------------------------------------------------------------------
# This is the function called to stop the WiThrottle Server cleanly (threadsafe)
#-----------------------------------------------------------------------------------------------

def dcc_power_status_updated(dcc_power:bool):
    global dcc_power_state
    if server_loop and server_loop.is_running():
        if dcc_power:  message1, message2 = "PPA1", "PW1"
        else: message1,message2 = "PPA0", "PW0"    
    try:
        if server_loop: server_loop.call_soon_threadsafe(broadcast_to_all, message1)
        if server_loop: server_loop.call_soon_threadsafe(broadcast_to_all, message2)
    except:
        pass
    return()

########################################################################################################################################

