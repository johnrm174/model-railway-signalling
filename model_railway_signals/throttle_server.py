import re
import threading
import asyncio
import socket
import logging
from zeroconf.asyncio import AsyncZeroconf, AsyncServiceInfo

from . import library


############################################################################################
### TODO - Function buttons, Timeout for Cab engineer????, Test with WiThrottle, Roster ####
############################################################################################

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
# Global parameters used by the WiThrottle Server
#-----------------------------------------------------------------------------------------------

# Keep track of active writers (connections) and the server loop
connected_clients = set()
server_loop = None
stop_event = None

server_host = socket.gethostname()
server_name = "DCCsignalling"
server_ip_address = socket.inet_aton(find_local_ip_address())
server_port_number = 12021
server_debug = True

dcc_power_state = None
# A The dictionary to map WiThrottle keys to CBUS session IDs and DCC addresses
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
# Functions for sending specific Responses to WiThrottle Client
#-----------------------------------------------------------------------------------------------

async def send_initial_connection_info(writer):
    """Send all initial connection information immediately after client connects"""
    # Protocol version
    writer.write(b"VN2.0\n")
    # Server type
    writer.write(b"HTJMRI\n")
    # Server description
    writer.write(f"Ht{server_name}\n".encode())
    # Roster
    await send_roster(writer)
    # Capabilities
    await send_capabilities(writer)
    # Power state
    await send_power_state(writer)
    # Web port (required even if not used)
    writer.write(b"PW12080\n")
    await writer.drain()
    if server_debug: logging.debug("Throttle Server - Initial connection info sent")

async def send_capabilities(writer):
    # Power capability: 2 = power supported
    writer.write(b"PPA2\n")

    # No turnout capability block
    # No route capability block

    # Consist count (0 for initialisation)
    writer.write(b"RCC0\n")

    # Heartbeat interval (10 seconds)
    writer.write(b"*10\n")

    await writer.drain()
    if server_debug:
        logging.debug("Throttle Server - Capabilities sent (minimal)")
    
async def send_roster(writer):
    # JMRI-style delimiters:
    # Entry delimiter: ]\[
    # Field delimiter: }|{
    
    if len(ROSTER) == 0:
        writer.write(b"RL0\n")
        await writer.drain()
        return

    entries = []

    for name, data in ROSTER.items():
        address = data["address"]
        addr_type = "L" if int(address) > 127 else "S"

        print("LOCO:", name)
        print("  Address:", address)
        print("  Type:", addr_type)

        # Build function list using }|{
        func_block = ""
        for fn in data["functions"]:
            func_block += "}|{" + fn
        print("  FUNC BLOCK:", func_block)

        # Build entry
        entry = (
            name +
            "}|{" + address +
            "}|{" + addr_type +
            func_block
        )

        print("  ROSTER ENTRY:", entry)
        entries.append(entry)

    # Join entries using JMRI entry delimiter ]\[
    roster_msg = "RL" + str(len(entries)) + "]\\[" + "]\\[".join(entries) + "]\n"

    print("ROSTER MSG:", roster_msg)

    writer.write(roster_msg.encode())
    await writer.drain()





async def send_power_state(writer):
    state = 1 if dcc_power_state else 0
    writer.write(f"PPA{state}\n".encode())
    await writer.drain()
    if server_debug:
        logging.debug(f"Throttle Server - DCC Power state {state} sent")

#-----------------------------------------------------------------------------------------------
# Function for handling connections initiated from each WiThrottle Client
#-----------------------------------------------------------------------------------------------


async def handle_client(reader, writer):
    peer = writer.get_extra_info("peername")
    connected_clients.add(writer)
    
    # 1. ONLY send the version at the very start.
    # Do NOT send Roster or Capabilities yet.
    writer.write(b"VN2.0\n")
    await writer.drain()

    try: 
        while True:
            data = await reader.read(1024)
            if not data: break
            
            messages = data.decode().split('\n')
            for msg in messages:
                msg = msg.strip()
                if not msg: continue
                
                if server_debug: logging.debug(f"RX: {msg}")

                # 2. WAIT for the Identity 'N' or Hardware Update 'HU'
                if msg.startswith("N") or msg.startswith("HU"):
                    # Send Hardware info
                    writer.write(f"HT{server_name}\n".encode())
                    writer.write(f"*NM{server_name}\n".encode())
                    
                    # Send the ACTUAL roster instead of hardcoded RL0
                    await send_roster(writer)
                    
                    # Send capabilities and power
                    await send_capabilities(writer)
                    await send_power_state(writer)
                    
                    # End the burst with the terminator
                    writer.write(b"#\n")
                    await writer.drain()
                    logging.info("Sent actual configuration burst after App Identity.")
                    continue
                
                # 1. Handle Heartbeat (MUST RESPOND TO KEEP SOCKET OPEN)
                if msg.startswith("*"):
                    if msg == "*+":
                        writer.write(b"*10\n") # Start EKG with 10s timeout
                        if server_debug: logging.debug("TX Heartbeat: *10")
                    else:
                        writer.write(b"*\n") # Standard pulse
                    await writer.drain()
                    continue
                
                # 4. Handle DCC Power
                if msg.startswith("PPA"):
                    state = msg[3:]
                    if state == "1": library.request_dcc_power_on()
                    else: library.request_dcc_power_off()
                    # Acknowledge the power change back to app
                    writer.write(f"PPA{state}\n".encode())
                    await writer.drain()
                    continue


                #---------------------------------------------------------------------------
                # 4 Multi-Throttle Commands (acquire/release loco)
                #---------------------------------------------------------------------------
                
                if msg.startswith("M"):
                    # 1. Get the Index (for our internal dictionary)
                    throttle_index = msg[1] 
                    
                    # 2. Get the Full Key (for replying to the app, e.g., '0' or 'T0')
                    full_key_match = re.match(r"M([^+\-VRFL<q]+)", msg)
                    full_key = full_key_match.group(1) if full_key_match else throttle_index
                    
                    # 3. Get the Action part
                    match = re.search(r"[+\-VRFL<q].*", msg)
                    if not match: continue
                    rest = match.group(0)

                    # --- ACQUIRE (+) ---
                    if rest.startswith("+"):
                        try:
                            addr_match = re.search(r"\+(.*?)<;>", rest)
                            raw_addr = addr_match.group(1) if addr_match else "3"
                            
                            # CORRECTED: Handle the EH prefix (Entry Handle)
                            roster_name = ""
                            if "<;>EH" in rest:
                                roster_name = rest.split("<;>EH")[1]
                            elif "<;>E" in rest:
                                roster_name = rest.split("<;>E")[1]

                            dcc_addr_int = int(re.sub(r"[^0-9]", "", raw_addr))
                            session_id = library.request_loco_session(dcc_addr_int)
                            
                            if session_id > 0:
                                wi_sessions[throttle_index] = {
                                    "session_id": session_id,
                                    "addr_str": raw_addr,
                                    "speed": 0,
                                    "forward": True
                                }
                                
                                writer.write(f"M{full_key}+{raw_addr}<;>\n".encode())
                                writer.write(f"M{full_key}L{raw_addr}<;>{roster_name}\n".encode())
                                
                                # Initial State Sync
                                writer.write(f"M{full_key}AS{raw_addr}<;>V0\n".encode())
                                writer.write(f"M{full_key}AS{raw_addr}<;>R1\n".encode())
                                writer.write(f"M{full_key}AS{raw_addr}<;>s1\n".encode())
                                
                                # Sync the specific number of functions
                                # First, let's make sure we stripped the 'H' from 'EH' if needed
                                roster_lookup = roster_name
                                if roster_lookup.startswith('H') and roster_lookup not in ROSTER:
                                    roster_lookup = roster_lookup[1:]

                                if roster_lookup in ROSTER:
                                    num_funcs = len(ROSTER[roster_lookup]["functions"])
                                    for f in range(num_funcs):
                                        # Format: M0AS3<;>F0f  (where 0 is 'off' and f is function number)
                                        # Note: No space between F, 0, and the number
                                        writer.write(f"M{full_key}AS{raw_addr}<;>F0{f}\n".encode())
                                    logging.info(f"Synced {num_funcs} functions for {roster_lookup}")
                                else:
                                    # Fallback if roster lookup fails
                                    logging.warning(f"Roster name '{roster_name}' not found. Falling back to default F0-F28.")
                                    for f in range(29):
                                        writer.write(f"M{full_key}AS{raw_addr}<;>F0{f}\n".encode())

                                await writer.drain()
                                logging.info(f"Roster Loco {roster_name} ({raw_addr}) bound successfully.")
                        except Exception as e:
                            logging.error(f"Acquisition error: {e}")
                        continue

                    # --- CONTROL & QUERIES (V, R, F, q, -) ---
                    if throttle_index in wi_sessions:
                        sess = wi_sessions[throttle_index]
                        session_id = sess["session_id"]
                        addr_str = sess["addr_str"]
                        
                        # Handle Queries (qV, qR) - Crucial for UI Sync
                        if "qV" in rest:
                            writer.write(f"M{full_key}AS{addr_str}<;>V{sess['speed']}\n".encode())
                            await writer.drain()
                            continue

                        if "qR" in rest:
                            dir_val = 1 if sess["forward"] else 0
                            writer.write(f"M{full_key}AS{addr_str}<;>R{dir_val}\n".encode())
                            await writer.drain()
                            continue

                        # Clean the action string for control commands
                        clean_action = rest.replace("<;>", "")

                        # SPEED (V)
                        if clean_action.startswith("V"):
                            speed_val = int(clean_action[1:])
                            sess["speed"] = speed_val
                            library.set_loco_speed_and_direction(session_id, speed_val, sess["forward"])

                        # DIRECTION (R)
                        elif clean_action.startswith("R"):
                            dir_val = int(clean_action[1:])
                            sess["forward"] = (dir_val == 1)
                            library.set_loco_speed_and_direction(session_id, sess["speed"], sess["forward"])

                        # FUNCTION (F)
                        elif clean_action.upper().startswith("F"):
                            try:
                                state = (clean_action[1] == '1')
                                func_id = int(clean_action[2:])
                                library.set_loco_function(session_id, func_id, state)
                                # Echo back to keep app buttons in sync
                                writer.write(f"M{full_key}AS{addr_str}<;>{clean_action.upper()}\n".encode())
                                await writer.drain()
                            except Exception as e:
                                logging.error(f"Function Error: {e}")

                        # RELEASE (-)
                        elif clean_action.startswith("-"):
                            library.release_loco_session(session_id)
                            writer.write(f"M{full_key}-*\n".encode())
                            await writer.drain()
                            del wi_sessions[throttle_index]
                    
                    continue


                #---------------------------------------------------------------------------
                # 5 Quit notification (Client has gracefully disconnected)
                #---------------------------------------------------------------------------
                if msg == "Q":
                    logging.info(f"Throttle Server - Client {peer} sent Quit command.")
                    break # This exits the while loop and goes to the 'finally' block
                
                # --- 6. Handle Queries (NEW) ---
                # This prevents 'M0A*<;>qV' and 'M0A*<;>qR' from crashing the loop
                if "<;>q" in msg:
                    # Optimization: To stop Engine Driver from spamming qV and qR, 
                    # you can echo back the current state, but 'continue' is the priority.
                    if server_debug: logging.debug(f"Ignored Query: {msg}")
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
# The actual WiThrottle Server runs in a seperate thread to the main Tkinter thread
#-----------------------------------------------------------------------------------------------

async def throttle_Server_thread():
    global server_loop, stop_event
    server_loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
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

