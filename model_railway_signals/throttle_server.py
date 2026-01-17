####################################################################################################
# This is a WiThrottle Server for the DCC Signalling system providing the following:
#
# 1) Loco Roster - loco names, dcc_addresses, basic function key labels
# 2) Acquire a loco via the roster or DCC address
# 3) Control the loco - speed, direction, functions
# 4) Control DCC Bus Power
#
# Compatible wit the following:
#
# Engine Driver (Android) - All working OK
# Cab engineer (Android) - All functions are defaulting to mandatory???
# WiThrottle (Android) - Not working - won't go past the dashboard screen - doesn't work with JMRI either
#
# More info Here: https://www.jmri.org/help/en/package/jmri/jmrit/withrottle/Protocol.shtml
# Acknowledgements to JMRI debugging logs (enabled in  for the WiThrottle elements)
# Add:   <logger name="jmri.jmrit.withrottle" level="DEBUG"/>  to default_lcf.xml
#
####################################################################################################

### TODO - Latching/Non Latching Function buttons
### TODO - Get fully working with Cab Engineer and WiThrottle
### TODO - Use real roster

import re
import threading
import asyncio
import socket
import logging
from zeroconf.asyncio import AsyncZeroconf, AsyncServiceInfo

from . import library

#-----------------------------------------------------------------------------------------------
# Global parameters used by the WiThrottle Server
#-----------------------------------------------------------------------------------------------

# Keep track of active writers (connections) and the server loop
connected_clients = set()
server_loop = None
stop_event = None

# This is the Server Identification information
server_host = socket.gethostname()
server_name = f"DCCsignalling@{server_host}"
server_port_number = 12021
server_debug = True

dcc_power_state = None

# The dictionary to map WiThrottle session keys to SPROG session IDs (also tracks other important session info)
# Format of each entry: {"T1": {"session_id":2, "dcc_address":3, "addr_type":"S", "speed":0, "forward":True},}
wi_sessions = {}

##############################################
# Example of how it should look:
ROSTER = {
    "HST Set 1": {"address":"3", "functions": ["Lights","F1","Horn"]},
    "Class 47": {"address":"4701", "functions": ["Lights","F1","Horn"]},
    "Flying Scotsman": {"address":"60103", "functions": ["Lights","F1","F3"]}
}###############################################

#-----------------------------------------------------------------------------------------------
# Function for sending the capabilities to WiThrottle Client
#-----------------------------------------------------------------------------------------------

async def send_capabilities(writer):
    # Power capability: 2 = power supported
    power_capability ="PPA2\n"
    writer.write(power_capability.encode())
    if server_debug: logging.debug(f"Throttle Server - Sent Capabilities - Power: {power_capability!r}")
    # No turnout capability block
    # No route capability block
    # Consist count (0 for initialisation)
    consist_count ="RCC0\n"
    writer.write(consist_count.encode())
    if server_debug: logging.debug(f"Throttle Server - Sent Capabilities - Consist Count: {consist_count!r}")
    # Heartbeat interval (10 seconds)
    heartbeat_interval ="*10\n"
    writer.write(heartbeat_interval.encode())
    if server_debug: logging.debug(f"Throttle Server - Sent Capabilities - Heartbeat Interval: {heartbeat_interval!r}")
    await writer.drain()
    
#-----------------------------------------------------------------------------------------------
# Function for sending the Roster to WiThrottle Client
#-----------------------------------------------------------------------------------------------
    
async def send_roster(writer):
    # JMRI-style delimiters: Entry delimiter: ]\[ Field delimiter: }|{
    if len(ROSTER) == 0:
        roster_messsage = "RL0\n"
    else:
        roster_entries = []
        for name, data in ROSTER.items():
            address = data["address"]
            address_type = "L" if int(address) > 127 else "S"
            ########################### FUNCTION LIST NOT WORKING #########################
            # Build function list using }|{
            function_block = ""
            for function in data["functions"]:
                function_block += "}|{" + function
            ###############################################################################
            # Build entry
            entry = (name+"}|{"+address+"}|{"+address_type+function_block)
            roster_entries.append(entry)
        # Join entries using JMRI entry delimiter ]\[
        roster_messsage = "RL" + str(len(roster_entries)) + "]\\[" + "]\\[".join(roster_entries) + "]\n"
    writer.write(roster_messsage.encode())
    if server_debug: logging.debug(f"Throttle Server - Sent Roster: {roster_messsage!r}")
    await writer.drain()

#-----------------------------------------------------------------------------------------------
# Function for sending the the power state to WiThrottle Client
#-----------------------------------------------------------------------------------------------

async def send_power_state(writer):
    state = 1 if dcc_power_state else 0
    power_state = f"PPA{state}\n"
    writer.write(power_state.encode())
    if server_debug: logging.debug(f"Throttle Server - Sent DCC Power state: {power_state!r}")
    await writer.drain()

#-----------------------------------------------------------------------------------------------
# Function for handling connections initiated from each WiThrottle Client
#-----------------------------------------------------------------------------------------------

async def handle_client(reader, writer):
    peer = writer.get_extra_info("peername")
    connected_clients.add(writer)
    # ONLY send the version at the very start - Do NOT send Roster or Capabilities yet.
    protocol_version = "VN2.0\n" 
    writer.write(protocol_version.encode())
    if server_debug: logging.debug(f"Throttle Server - Sent Protocol Version: {protocol_version!r}")    
    await writer.drain()
    # Put exception handling around the client loop
    try: 
        while True:
            # If no data then the client has disconnected
            data = await reader.read(1024)
            if not data: break
            # We have data so we go on to parse the messages
            messages = data.decode().split('\n')
            for message in messages:
                message = message.strip()
                if not message: continue
                if server_debug: logging.debug(f"Throttle Server - Received Message: {message!r}")
                #------------------------------------------------------------
                # Identity 'N' or Hardware Update 'HU' Message
                #------------------------------------------------------------
                if message.startswith("N") or message.startswith("HU"):
                    if message.startswith("N") and server_debug: logging.debug("Throttle Server - Handling Identity Message")
                    if message.startswith("HU") and server_debug: logging.debug("Throttle Server - Handling Hardware Update Message")
                    # Send Hardware info and server name
                    hardware_type_response = f"HT{server_name}\n"
                    writer.write(hardware_type_response.encode())
                    if server_debug: logging.debug(f"Throttle Server - Sent Hardware Type: {hardware_type_response!r}")
                    server_name_response = f"*NM{server_name}\n"
                    writer.write(server_name_response.encode())
                    if server_debug: logging.debug(f"Throttle Server - Sent Server Name: {server_name_response!r}")
                    # Send the ACTUAL roster, Send capabilities and power state
                    await send_roster(writer)
                    await send_capabilities(writer)
                    await send_power_state(writer)
                    # End the burst with the terminator
                    burst_terminator = "#\n"
                    writer.write(burst_terminator.encode())
                    if server_debug: logging.debug(f"Throttle Server - Sent Burst Terminator: {burst_terminator!r}")
                    await writer.drain()
                    continue
                #------------------------------------------------------------
                # Handle Heartbeat Message (MUST RESPOND TO KEEP SOCKET OPEN)
                #------------------------------------------------------------
                if message.startswith("*"):
                    if message == "*+":
                        logging.debug("Throttle Server - Handling Heartbeat Timeout Message")
                        heartbeat_response = "*10\n"
                        writer.write(heartbeat_response.encode()) # Start EKG with 10s timeout
                        if server_debug: logging.debug(f"Throttle Server - Sent Heartbeat Response: {heartbeat_response!r}")
                    else:
                        logging.debug("Throttle Server - Handling regular Heartbeat Message")
                        heartbeat_response = "*\n"
                        writer.write(heartbeat_response.encode()) # Standard pulse
                        if server_debug: logging.debug(f"Throttle Server - Sent Heartbeat Response: {heartbeat_response!r}")
                    await writer.drain()
                    continue
                #------------------------------------------------------------
                # Handle DCC Power ON/OFF requests
                #------------------------------------------------------------
                if message.startswith("PPA"):
                    state = message[3:]
                    if state == "1":
                        if server_debug:logging.debug("Throttle Server - Handling Power ON Request")
                        library.request_dcc_power_on()
                    else:
                        if server_debug:logging.debug("Throttle Server - Handling Power OFF Request")
                        library.request_dcc_power_off()
                    # Acknowledge the power change back to app
                    power_response_message = f"PPA{state}\n"
                    writer.write(power_response_message.encode())
                    if server_debug: logging.debug(f"Throttle Server - Sent Power Response: {power_response_message!r}")
                    await writer.drain()
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
                        if server_debug: logging.debug("Throttle Server - Handling Acquire Locomotive Request")
                        try:
                            # Parse the raw address with prefix (e.g. "S3" or "L4701")
                            addr_match = re.search(r"\+(.*?)<;>", rest_of_message)
                            raw_addr = addr_match.group(1) if addr_match else "3"
                            # Split prefix (S or L) from numeric address
                            addr_prefix = raw_addr[0] if raw_addr and raw_addr[0] in ("S", "L") else ""
                            addr_num = re.sub(r"\D", "", raw_addr)  # numeric-only address for AS messages
                            # Parse roster name (preserve leading 'H' if client provided it)
                            roster_name = ""
                            roster_match = re.search(r"<;>E(.+)$", rest_of_message)
                            if roster_match:
                                roster_name = roster_match.group(1)
                            else:
                                if "<;>EH" in rest_of_message:
                                    roster_name = "H" + rest_of_message.split("<;>EH")[1]
                                elif "<;>E" in rest_of_message:
                                    roster_name = rest_of_message.split("<;>E")[1]
                            # Request session from backend
                            dcc_addr_int = int(re.sub(r"[^0-9]", "", raw_addr))
                            session_id = library.request_loco_session(dcc_addr_int)
                            if session_id > 0:
                                wi_sessions[throttle_index] = {"session_id": session_id,"addr_str": raw_addr,"speed": 0,"forward": True}
                                # A) Echo acquisition to the client (keep prefix form here)
                                address_to_send = f"M{full_key}+{raw_addr}<;>\n"
                                writer.write(address_to_send.encode())
                                if server_debug: logging.debug(f"Throttle Server - Sent Address Confirmation: {address_to_send!r}")
                                # B) Send function LABEL list in the L message (use raw_addr with prefix)
                                # Build function list from ROSTER if found, otherwise blank entries
                                roster_lookup = roster_name
                                if roster_lookup.startswith('H') and roster_lookup not in ROSTER:
                                    roster_lookup = roster_lookup[1:]
                                max_slots = 31  # advertise F0..F30 (matches the JMRI example)
                                if roster_lookup in ROSTER:
                                    funcs = list(ROSTER[roster_lookup].get("functions", []))
                                else:
                                    funcs = []
                                # Pad/truncate to max_slots
                                if len(funcs) < max_slots:
                                    funcs_padded = funcs + [""] * (max_slots - len(funcs))
                                else:
                                    funcs_padded = funcs[:max_slots]
                                # Build JMRI-style function-list block using ]\[ delimiters
                                func_list_block = "]\\[" + "]\\[".join(funcs_padded)
                                # Send L message with prefixed address (S/L) so client knows short/long form
                                roster_label_l_msg = f"M{full_key}L{raw_addr}<;>{func_list_block}\n"
                                writer.write(roster_label_l_msg.encode())
                                if server_debug: logging.debug(f"Throttle Server - Sent Function-label L message: {roster_label_l_msg!r}")
                                # Optionally send human-readable roster name as LN (some clients honor this)
                                if roster_name:
                                    writer.write(f"M{full_key}LN{raw_addr}<;>{roster_name}\n".encode())
                                    if server_debug: logging.debug(f"Throttle Server - Sent Roster Name LN message: {roster_name!r}")
                                # C) State sync: Use numeric address (no S/L) AFTER the AS token
                                # Send initial function states for every advertised slot using numeric address
                                for f in range(len(funcs_padded)):
                                    # Format: M{key}AS{numeric_addr}<;>F0{f}
                                    function_configuration = f"M{full_key}AS{addr_num}<;>F0{f}\n"
                                    writer.write(function_configuration.encode())
                                    if server_debug: logging.debug(f"Throttle Server - Sent Function Configuration: {function_configuration!r}")
                                # Other common initial syncs (V, R, s) also use numeric address
                                writer.write(f"M{full_key}AS{addr_num}<;>V0\n".encode())
                                writer.write(f"M{full_key}AS{addr_num}<;>R1\n".encode())
                                writer.write(f"M{full_key}AS{addr_num}<;>s1\n".encode())
                                if server_debug:
                                    logging.debug(f"Throttle Server - Sent Initial Speed/Direction/Steps using numeric addr: {addr_num!r}")
                                await writer.drain()
                                logging.info(f"Synced {len(funcs)} functions for roster '{roster_lookup}' (raw roster_name='{roster_name}').")
                                logging.info(f"Roster Loco {roster_name} ({raw_addr}) bound successfully.")
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
                        # Handle Queries (qV, qR) - Crucial for UI Sync
                        if "qV" in rest_of_message:
                            if server_debug:logging.debug("Throttle Server - Handling Query Speed Request")
                            speed_response = f"M{full_key}AS{address_str}<;>V{session['speed']}\n"
                            writer.write(speed_response.encode())
                            if server_debug: logging.debug(f"Throttle Server - Sent Speed Response: {speed_response!r}")
                            await writer.drain()
                            continue
                        if "qR" in rest_of_message:
                            if server_debug:logging.debug("Throttle Server - Handling Query Direction Request")
                            direction_value = 1 if session["forward"] else 0
                            direction_response = f"M{full_key}AS{address_str}<;>R{direction_value}\n"
                            writer.write(direction_response.encode())
                            if server_debug: logging.debug(f"Throttle Server - Sent direction Response: {direction_response!r}")
                            await writer.drain()
                            continue
                        # Clean the action string for control commands
                        clean_action = rest_of_message.replace("<;>", "")
                        # SPEED (V)
                        if clean_action.startswith("V"):
                            if server_debug:logging.debug("Throttle Server - Handling Speed Change Request")
                            speed_value = int(clean_action[1:])
                            session["speed"] = speed_value
                            library.set_loco_speed_and_direction(session_id, session["speed"], session["forward"])
                        # DIRECTION (R)
                        elif clean_action.startswith("R"):
                            if server_debug:logging.debug("Throttle Server - Handling Direction Change Request")
                            direction_value = int(clean_action[1:])
                            session["forward"] = (direction_value == 1)
                            library.set_loco_speed_and_direction(session_id, session["speed"], session["forward"])
                        # FUNCTION (F)
                        elif clean_action.upper().startswith("F"):
                            if server_debug:logging.debug("Throttle Server - Handling Function Change Request")
                            try:
                                state = (clean_action[1] == '1')
                                func_id = int(clean_action[2:])
                                library.set_loco_function(session_id, func_id, state)
                                # Echo back to keep app buttons in sync
                                function_response = f"M{full_key}AS{address_str}<;>{clean_action.upper()}\n"
                                writer.write(function_response.encode())
                                if server_debug: logging.debug(f"Throttle Server - Sent Function Response: {function_response!r}")
                                await writer.drain()
                            except Exception as e:
                                logging.error(f"Function Error: {e}")
                        # RELEASE (-)
                        elif clean_action.startswith("-"):
                            if server_debug:logging.debug("Throttle Server - Handling Release Locomotive Request")
                            library.release_loco_session(session_id)
                            release_loco_response = f"M{full_key}-*\n"
                            writer.write(release_loco_response.encode())
                            if server_debug: logging.debug(f"Throttle Server - Sent Release Locomotive response: {release_loco_response!r}")
                            await writer.drain()
                            del wi_sessions[throttle_index]
                    continue
                #---------------------------------------------------------------------------
                # Handle Quit notification (Client has gracefully disconnected)
                #---------------------------------------------------------------------------
                if message == "Q":
                    logging.info(f"Throttle Server - Client {peer} sent Quit command.")
                    break # This exits the while loop and goes to the 'finally' block
                
                #---------------------------------------------------------------------------
                # Handle Queries - This prevents 'M0A*<;>qV' and 'M0A*<;>qR' from crashing the loop
                #---------------------------------------------------------------------------
                if "<;>q" in message:
                    # Optimization: To stop Engine Driver from spamming qV and qR, 
                    # you can echo back the current state, but 'continue' is the priority.
                    if server_debug: logging.debug(f"Ignored Query: {message!r}")
                    continue
    finally:
        # This code runs no matter HOW the loop exits (Quit command, crash, or disconnect)
        logging.debug(f"Throttle Server - Cleaning up sessions for {peer}")
        for index in list(wi_sessions.keys()):
            try:
                session_id = wi_sessions[index]["session_id"]
                addr = wi_sessions[index]["addr_str"]
                # Release the loco in the Pi-SPROG hardware
                library.release_loco_session(session_id)
                logging.debug(f"Released session {session_id} for loco {addr}")
            except Exception as e:
                logging.error(f"Error releasing session during cleanup: {e}")
        wi_sessions.clear()
        connected_clients.remove(writer)
        # Close the socket properly
        writer.close()
        await writer.wait_closed()
        logging.debug(f"Throttle Server - Connection closed for {peer}")
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
            logging.error(f"Throttle Server - failed to Broadcast message to client: {e}")
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
            logging.debug(f"Throttle Server - Starting WiThrottle server on {server_ip_address}:{server_port_number}")
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
            logging.debug(f"Throttle Server - WiThrottle Server {server_name} registered successfully")
            # This is the key: The thread "hangs" here until stop_event.set() is called
            await stop_event.wait()
            logging.debug(f"Throttle Server -- WiThrottle Server {server_name} Shutdown initiated")
            serve_task.cancel()
            
        finally:
            if aiozc: await aiozc.async_close()
            if server: server.close()
            await server.wait_closed()
            logging.debug("Throttle Server - Clean shut down complete")
    else:
        aiozc, server = None, None
        logging.error(f"Throttle Server -Could not start WiThrottle server as IP address could not be retrieved")
    return()

#-----------------------------------------------------------------------------------------------
# This is the function called to start the WiThrottle Server (which runs in a seperate thread)
#-----------------------------------------------------------------------------------------------

def start_throttle_server(dcc_power):
    global dcc_power_state
    dcc_power_state = dcc_power
    if server_debug: logging.debug("Throttle Server: Starting Throttle Server Thread")
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
    if server_debug: logging.debug("Throttle Server: Initiating Throttle Server Shutdown")
    if server_loop and server_loop.is_running() and stop_event:
        if server_debug: logging.debug("Throttle Server: Starting Throttle Server Thread")
        server_loop.call_soon_threadsafe(stop_event.set)
    server_loop = None
    # De Register for DCC Power update callbacks from the SPROG
    library.unsubscribe_from_dcc_power_updates(dcc_power_status_updated)
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

