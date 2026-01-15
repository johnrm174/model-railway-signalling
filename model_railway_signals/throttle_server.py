
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
server_name = "DCC signalling." + server_host
server_ip_address = socket.inet_aton(find_local_ip_address())
server_port_number = 12021
server_debug = True

dcc_power_state = None
# A The dictionary to map WiThrottle keys to CBUS session IDs and DCC addresses
# Format of each entry: {"T1": {"session_id":2, "dcc_address":3, "addr_type":"S", "speed":0, "forward":True},}
wi_sessions = {}

##############################################
ROSTER = {
    "Steam 700": "700",
    "Diesel 55": "55",
}
###############################################

#-----------------------------------------------------------------------------------------------
# Functions for sending specific Responses to WiThrottle Client
#-----------------------------------------------------------------------------------------------

async def send_handshake(writer):
    writer.write(b"VN2.0\n")
    writer.write(f"N{server_name}\n".encode())
    writer.write(b"HT10\n")
    await writer.drain()
    if server_debug: logging.debug("Throttle Server - Handshake sent")

async def send_capabilities(writer):
    # Power capability: 2 = power supported
    writer.write(b"PPA2\n")
    # Turnout capability block (JMRI format)
    writer.write( b"PTT]\\[Turnouts}|{Turnout]"
                  b"\\[Closed}|{2]"
                  b"\\[Thrown}|{4]"
                  b"\\[Unknown}|{1]"
                  b"\\[Inconsistent}|{8\n" )
    # Route capability block (JMRI format)
    writer.write( b"PRT]\\[Routes}|{Route]"
                  b"\\[Active}|{2]"
                  b"\\[Inactive}|{4]"
                  b"\\[Unknown}|{0]"
                  b"\\[Inconsistent}|{8]\n" )
    # Consist count (0 for initialisation)
    writer.write(b"RCC0\n")
    # Function table (JMRI format)
    writer.write(b"PFT1768291381<;>1.0\n")
    await writer.drain()
    if server_debug: logging.debug("Throttle Server - Capabilities sent")
    
# THIS DOESN'T WORK ##################################
# async def send_roster(writer):
# # Format: RL<Count><;><Name><;><Address><;><Type>...
#     # Type: 'S' for Short, 'L' for Long
#     roster_msg = "RL1<;>Class 37<;>3701<;>L\n"
#     writer.write(roster_msg.encode())
#     await writer.drain()
#     if server_debug: logging.debug("Throttle Server - Loco Roster sent")
    
async def send_power_state(writer):
    if dcc_power_state is not None:
        print(int(dcc_power_state))
        writer.write(f"PPA{int(dcc_power_state)}\n".encode())
        writer.write(f"PW{int(dcc_power_state)}\n".encode())
        await writer.drain()
        if server_debug: logging.debug(f"Throttle Server - DCC Power state {dcc_power_state} sent")

#-----------------------------------------------------------------------------------------------
# Function for handling connections initiated from each WiThrottle Client
#-----------------------------------------------------------------------------------------------

async def handle_client(reader, writer):
    connected_clients.add(writer)
    peer = writer.get_extra_info("peername")
    if server_debug: logging.debug(f"Throttle Server - Client connected: {peer}")
    # Send the initial handshake
    await send_handshake(writer)
    try: 
        await send_handshake(writer)
        while True:
            # Read the incoming messages - If None then client has disconnected so we exit
            data = await reader.read(1024)
            if not data: break
            # Decode the Message
            messages = data.decode().split('\n')
            for msg in messages:
                msg=msg.strip()
                if not msg: continue
                if server_debug: logging.debug(f"Throttle Server - Received message: {msg}")
                #---------------------------------------------------------------------------
                # Capabilities requested - respond with capabilities
                #---------------------------------------------------------------------------
                if msg.startswith("HU"):
                    await send_capabilities(writer)
                    ##await send_roster(writer) THIS DOESN'T WORK ##################################
                    await send_power_state(writer)
                #---------------------------------------------------------------------------
                # Heattbeat message - we just need to respond to say we are still alive
                #---------------------------------------------------------------------------
                if msg == "*":
                    writer.write(b"*\n")
                    await writer.drain()
                    continue
                #---------------------------------------------------------------------------
                # DCC Power On/OFF Requested
                #---------------------------------------------------------------------------
                if msg.startswith("PPA"):
                    state = msg[3:]  # "0" or "1"
                    if state == "1": library.request_dcc_power_on()
                    else: library.request_dcc_power_off()
                    continue
                #---------------------------------------------------------------------------
                # Multi-Throttle Commands (acquire/release loco)
                #---------------------------------------------------------------------------
                if msg.startswith("M"):
                    # Identify the Index (the first char after 'M')
                    # Example: In "M0AS123", the index is '0'
                    throttle_index = msg[1]
                    # Define full_key early so it's available for all sub-blocks
                    full_key_match = re.match(r"M([^+\-VRFL<]+)", msg)
                    full_key = full_key_match.group(1).strip() if full_key_match else throttle_index
                    match = re.search(r"[+\-VRFL<].*", msg)
                    if not match: continue
                    rest = match.group(0)
                    # --- ACQUIRE (+) ---
                    if "+" in rest:
                        try:
                            raw_addr = rest.split("<;>")[1]
                            dcc_addr_int = int(raw_addr[1:])
                            session_id = library.request_loco_session(dcc_addr_int)
                            if session_id > 0:
                                # Store it using the SINGLE CHARACTER index (e.g., '0')
                                wi_sessions[throttle_index] = {
                                    "session_id": session_id,
                                    "speed": 0,
                                    "forward": True,
                                    "addr_str": raw_addr}
                                # Echo back the FULL key the client used in the message
                                # If they sent M0+, we reply M0+...
                                full_key_match = re.match(r"M([^+\-VRFL<]+)", msg)
                                full_key = full_key_match.group(1) if full_key_match else throttle_index
                                writer.write(f"M{full_key}+{raw_addr}<;>{raw_addr}\n".encode())
                                await writer.drain()
                                if server_debug: logging.debug(f"Throttle Server - Acquired {raw_addr} for Index "+
                                                               f"{throttle_index} - session ID is {session_id}")
                        except Exception as e:
                            logging.error(f"Acquisition error: {e}")
                        continue
                    # --- CONTROL (V, R, etc.) ---
                    # Look up using only the throttle_index ('0')
                    if throttle_index in wi_sessions:
                        session_id = wi_sessions[throttle_index]["session_id"]
                        action = rest.replace("<;>", "")
                        # SPEED (V)
                        if action.startswith("V"):
                            speed_val = int(action[1:])
                            wi_sessions[throttle_index]["speed"] = speed_val
                            library.set_loco_speed_and_direction(session_id, speed_val, wi_sessions[throttle_index]["forward"])
                            if server_debug: logging.debug(f"Throttle Server - Applied Speed {speed_val} to Session {session_id}")
                        # DIRECTION (R)
                        elif action.startswith("R"):
                            dir_val = int(action[1:])
                            wi_sessions[throttle_index]["forward"] = (dir_val == 1)
                            library.set_loco_speed_and_direction(session_id, wi_sessions[throttle_index]["speed"], wi_sessions[throttle_index]["forward"])
                            if server_debug: logging.debug(f"Throttle Server - Applied Direction {dir_val} to Session {session_id}")
                        # RELEASE (-)
                        elif action.startswith("-"):
                            library.release_loco_session(session_id)
                            if server_debug: logging.debug(f"Throttle Server - Released session {session_id} for Index {throttle_index}")
                            # Acknowledge with the index
                            writer.write(f"M{throttle_index}-*\n".encode())
                            await writer.drain()
                            del wi_sessions[throttle_index]
                        elif action.startswith("q"):
                            # Cab Engineer is just asking for a status update.
                            # We "ignore" this by NOT calling the library, but we MUST reply to the client.
                            if "V" in action:
                                v = wi_sessions[throttle_index]["speed"]
                                # Use full_key here instead of key
                                writer.write(f"M{full_key}<;>V{v}\n".encode())
                            elif "R" in action:
                                r = 1 if wi_sessions[throttle_index]["forward"] else 0
                                # Use full_key here instead of key
                                writer.write(f"M{full_key}<;>R{r}\n".encode())
                            await writer.drain()
                            continue # Skip the rest of the loop for this message
                #---------------------------------------------------------------------------
                # Quit notification (Client has gracefully disconnected)
                #---------------------------------------------------------------------------
                if msg == "Q":
                    logging.info(f"Throttle Server - Client {peer} sent Quit command.")
                    break # This exits the while loop and goes to the 'finally' block
                #---------------------------------------------------------------------------
                # Send Roster request - THIS DOESN'T WORK
                #---------------------------------------------------------------------------
#                 if msg.startswith("RL"):
#                     await send_roster(writer)
#                     continue
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
                properties={"roster": "yes",},
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

